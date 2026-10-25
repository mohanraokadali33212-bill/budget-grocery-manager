import calendar
from datetime import date, datetime, timedelta
import io
import math
import os
import re
import uuid

from flask import current_app, url_for
from PIL import Image
from sqlalchemy import extract, func

from extensions import db
from models import Category, Expense, ExpenseItem, PantryItem

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
MOBILE_RE = re.compile(r"^[6-9]\d{9}$")
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.]{3,30}$")
ALLOWED_EXT = {"jpg", "jpeg", "png", "webp"}


def to_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def to_float(value, default=0.0):
    try:
        number = float(value)
        return number if math.isfinite(number) else default
    except (TypeError, ValueError):
        return default


def valid_password(pw):
    return bool(pw) and len(pw) >= 8 and re.search(r"[A-Za-z]", pw) and re.search(r"\d", pw)


def safe_next(url):
    if url and url.startswith("/") and not url.startswith("//"):
        return url
    return None


def money(value):
    value = float(value or 0)
    if value == int(value):
        return f"₹{int(value):,}"
    return f"₹{value:,.2f}"


def get_current_month_range(target_date=None):
    """Return (first_day, last_day) of the month for given date (defaults to today)."""
    t = target_date or date.today()
    first_day = date(t.year, t.month, 1)
    _, last_day_num = calendar.monthrange(t.year, t.month)
    last_day = date(t.year, t.month, last_day_num)
    return first_day, last_day


def get_user_monthly_summary(user, target_month=None, target_year=None):
    """Calculates comprehensive monthly budget analytics for a customer."""
    today = date.today()
    m = target_month or today.month
    y = target_year or today.year

    month_name = calendar.month_name[m]
    first_day, last_day = get_current_month_range(date(y, m, 1))

    # All expenses in this month
    expenses = (
        Expense.query.filter(
            Expense.user_id == user.id,
            Expense.expense_date >= first_day,
            Expense.expense_date <= last_day,
        )
        .order_by(Expense.expense_date.desc(), Expense.id.desc())
        .all()
    )

    total_spent = round(sum(exp.total_amount for exp in expenses), 2)
    budget = float(user.monthly_budget or 0)
    remaining = round(budget - total_spent, 2)
    is_over = budget > 0 and total_spent > budget
    over_amount = round(total_spent - budget, 2) if is_over else 0.0
    percent = round((total_spent / budget) * 100, 1) if budget > 0 else 0

    # Spending by store
    store_map = {}
    for exp in expenses:
        store_map[exp.store_name] = store_map.get(exp.store_name, 0.0) + exp.total_amount
    store_stats = sorted(
        [{"store": k, "amount": round(v, 2), "percent": round((v / total_spent) * 100, 1) if total_spent > 0 else 0}
         for k, v in store_map.items()],
        key=lambda x: x["amount"],
        reverse=True
    )

    # Spending by category from expense items
    cat_rows = (
        db.session.query(Category.name, Category.icon, func.sum(ExpenseItem.subtotal))
        .join(ExpenseItem, ExpenseItem.category_id == Category.id)
        .join(Expense, Expense.id == ExpenseItem.expense_id)
        .filter(
            Expense.user_id == user.id,
            Expense.expense_date >= first_day,
            Expense.expense_date <= last_day,
        )
        .group_by(Category.name, Category.icon)
        .all()
    )
    category_stats = [
        {"name": name, "icon": icon, "amount": round(amt or 0, 2),
         "percent": round(((amt or 0) / total_spent) * 100, 1) if total_spent > 0 else 0}
        for name, icon, amt in sorted(cat_rows, key=lambda x: x[2] or 0, reverse=True)
    ]

    # Pantry summary
    pantry_all = PantryItem.query.filter_by(user_id=user.id).all()
    pantry_count = len(pantry_all)
    expiring_soon_count = sum(1 for p in pantry_all if p.expiry_status == "expiring_soon")
    expired_count = sum(1 for p in pantry_all if p.expiry_status == "expired")
    low_stock_count = sum(1 for p in pantry_all if p.is_low_stock)

    # Daily pace calculation
    days_in_month = (last_day - first_day).days + 1
    current_day = today.day if (today.year == y and today.month == m) else days_in_month
    avg_per_day = round(total_spent / current_day, 2) if current_day > 0 else 0.0
    projected_month_end = round(avg_per_day * days_in_month, 2)

    return {
        "month_name": month_name,
        "month": m,
        "year": y,
        "budget": budget,
        "total_spent": total_spent,
        "remaining": remaining,
        "is_over": is_over,
        "over_amount": over_amount,
        "percent": percent,
        "expense_count": len(expenses),
        "recent_expenses": expenses[:6],
        "store_stats": store_stats,
        "category_stats": category_stats,
        "pantry_count": pantry_count,
        "expiring_soon_count": expiring_soon_count,
        "expired_count": expired_count,
        "low_stock_count": low_stock_count,
        "avg_per_day": avg_per_day,
        "projected_month_end": projected_month_end,
    }


def save_image(file_storage):
    """Validate, optimize and store receipt or grocery image. Returns URL or None."""
    if not file_storage or not file_storage.filename:
        return None
    name = file_storage.filename
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if ext not in ALLOWED_EXT:
        raise ValueError("Only JPG, JPEG, PNG, or WEBP images are allowed.")
    try:
        img = Image.open(file_storage.stream)
        img.verify()
        file_storage.stream.seek(0)
        img = Image.open(file_storage.stream)
        if img.format not in ("JPEG", "PNG", "WEBP"):
            raise ValueError("bad format")
        img = img.convert("RGB")
        img.thumbnail((1200, 1200))
        buf = io.BytesIO()
        img.save(buf, "WEBP", quality=82)
        buf.seek(0)
    except Exception:
        raise ValueError("The uploaded file is not a valid image.")

    cfg = current_app.config
    if cfg.get("CLOUDINARY_CLOUD_NAME") and cfg.get("CLOUDINARY_API_KEY") and cfg.get("CLOUDINARY_API_SECRET"):
        import cloudinary
        import cloudinary.uploader
        cloudinary.config(
            cloud_name=cfg["CLOUDINARY_CLOUD_NAME"],
            api_key=cfg["CLOUDINARY_API_KEY"],
            api_secret=cfg["CLOUDINARY_API_SECRET"],
            secure=True,
        )
        try:
            result = cloudinary.uploader.upload(buf, folder="grocery-budget-manager", resource_type="image")
            return result["secure_url"]
        except Exception:
            raise ValueError("Receipt upload to Cloudinary failed. Check Cloudinary settings.")

    folder = os.path.join(current_app.static_folder, "uploads")
    os.makedirs(folder, exist_ok=True)
    filename = uuid.uuid4().hex + ".webp"
    with open(os.path.join(folder, filename), "wb") as out:
        out.write(buf.read())
    return url_for("static", filename="uploads/" + filename)
