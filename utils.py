from flask import session, redirect, url_for, g
from functools import wraps

from infrastructure import cm
from logger import logger

def role_required(*required_roles):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not session.get("logged_in"):
                logger.warning("User not logged in.")
                return redirect(url_for("auth_routes.login_page"))

            username = session.get("username")
            user = cm.get_user_by_username(username) if username else None
            if not user:
                logger.error("Couldn't load user from session.")
                return redirect(url_for("auth_routes.login_page"))

            if not user.role or user.role not in required_roles:
                logger.error("User doesn't have access to view this page.")
                return redirect(url_for("auth_routes.login_page"))

            return f(*args, **kwargs)
        return decorated
    return wrapper