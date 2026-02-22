import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SESSION_LIFETIME = timedelta(minutes=30)

    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    DEBUG = False
    PROPAGATE_EXCEPTIONS = False

    MAINTENANCE_MODE = os.environ.get("MAINTENANCE_MODE", "false").lower() == "true"
    ALLOWED_IPS = os.environ.get("ALLOWED_IPS", "").split(",") if os.environ.get("ALLOWED_IPS") else []
    BLACKLISTED_IPS = os.environ.get("BLACKLISTED_IPS", "").split(",") if os.environ.get("BLACKLISTED_IPS") else []