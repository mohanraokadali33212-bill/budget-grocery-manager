# 🛒 Grocery and Budget Manager
### *Smart Household Grocery Budgeting, Live In-Store Cart Tracking & Food Waste Reducer*

A modern, responsive, production-ready web application built **specifically for customers and households** to manage their grocery spending, prevent supermarket overspending, log grocery bills from physical stores or delivery apps, and track home pantry expiry dates.

---

## 🌟 Core Features for Customers

### 1. 🛒 Interactive Shopping Trip Mode *(In-Store / Online Real-Time Cart)*
- Walk into supermarkets (**DMart**, **Reliance Fresh**, **Local Kirana**) or shop on delivery apps (**Blinkit**, **Zepto**, **Instamart**).
- Set a **Trip Budget** (or use your remaining monthly budget).
- Add items rapidly as you place them into your physical basket.
- **Live Budget HUD**: Real-time tally of items, cart cost, remaining budget, and an instant **Red Alert (⚠️ Budget Exceeded)** if you go over your limit.
- **Interactive Checkbox & Touch Steppers**: Check off items `[✓]` as they enter your basket, adjust quantities with tactile `[-] [+]` buttons.
- **1-Click Finish**: Automatically records the trip into your monthly expense log and can automatically populate purchased groceries straight into your **Pantry & Fridge**!

### 2. 🧾 Expense & Receipt Logging
- Record bills from any store with store names, dates, amounts, and payment methods (**UPI**, **Cash**, **Card**).
- Upload and inspect **Receipt / Bill Photos** (stored locally or synced with Cloudinary).
- Optional **Itemized Breakdown** for detailed category analytics.
- Filter bills by store, month, and year to see where your household grocery budget is actually spent.

### 3. 🥫 Pantry & Expiry Tracker *(Avoid Duplicates & Food Waste)*
- Track food items stored in your **❄️ Fridge**, **🥫 Pantry / Shelf**, or **🧊 Freezer**.
- Real-time expiry countdowns:
  - 🟢 **Fresh / Good**
  - 🟠 **Expiring Soon** (≤ 3 days countdown)
  - 🔴 **Expired** alert
  - ⚠️ **Running Low** flag
- **1-Click "Add to Shopping Trip"**: Running low on Milk or Atta? Send it directly to your next shopping list so you never forget essentials or buy unnecessary duplicates.

### 4. 📊 Household Monthly Budget Dashboard
- Set a target monthly grocery budget (e.g. ₹12,000/month).
- Live progress bar showing total spent, remaining balance, and daily spending pace.
- Store breakdown charts (DMart vs Blinkit vs Kirana).

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, Vanilla CSS3 (Custom design tokens, CSS Grid, Flexbox, touch-friendly mobile bottom navigation, modals, toasts), Vanilla JavaScript (No React/Vue).
- **Backend**: Python 3, Flask (Modular Blueprints: `auth`, `dashboard`, `trips`, `expenses`, `pantry`), Flask-Login, Flask-WTF (CSRF Protection), Werkzeug password hashing.
- **Database**: SQLite for development (`instance/grocery.db`) and PostgreSQL for production (`render.yaml`).
- **Images**: Pillow (image optimization, resizing to WebP) with optional Cloudinary support.
- **Production Server**: Gunicorn (`web: gunicorn app:app`).

---

## 🚀 Quick Start / Local Setup

```powershell
# 1. Activate your virtual environment
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the application
python app.py
```

Open your browser at:
👉 **[http://localhost:5000](http://localhost:5000)**

---

## 🔑 Demo Account Credentials

A pre-seeded customer account is ready for instant testing:
- **Email:** `customer@example.com`
- **Password:** `Password123`
*(Or click the 1-click demo login button on the login screen!)*

You can also register your own personal account anytime at `/register`.

---

## 📱 Mobile-First Supermarket Experience

Designed to be carried while shopping:
- Sticky top HUD keeping your cart subtotal and budget visible at all times.
- Large touch targets (≥ 44px) for steppers and checkboxes.
- Quick bottom navigation bar for one-thumb switching between Trips, Bills, and Pantry.
