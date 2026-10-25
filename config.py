import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))


def _load_env_file():
    """Load .env safely. Handles UTF-8, UTF-8 with BOM and UTF-16 (PowerShell) files,
    and never crashes the app if the file is unreadable."""
    path = os.path.join(basedir, ".env")
    if not os.path.isfile(path):
        return
    for encoding in ("utf-8-sig", "utf-16", "cp1252"):
        try:
            load_dotenv(path, encoding=encoding)
            return
        except Exception:
            continue


_load_env_file()


def database_url():
    url = os.environ.get("DATABASE_URL")
    if url:
        # Render/Heroku style URLs start with postgres://, SQLAlchemy needs postgresql://
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url
    os.makedirs(os.path.join(basedir, "instance"), exist_ok=True)
    return "sqlite:///" + os.path.join(basedir, "instance", "grocery.db")


IS_PROD = os.environ.get("FLASK_ENV") == "production"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = database_url()
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = IS_PROD
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = IS_PROD

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB uploads
    PER_PAGE = 12
    LOW_STOCK_LIMIT = 10

    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET")

    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin@1234")
    SEED_SAMPLE_DATA = os.environ.get("SEED_SAMPLE_DATA", "1") == "1"
