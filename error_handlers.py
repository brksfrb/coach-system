from flask import Blueprint, render_template, redirect, url_for, Flask
from flask_wtf.csrf import CSRFError

from logger import logger

error_routes = Blueprint("error_routes", __name__)

# ERRORS TO HANDLE: 400, 401, 402, 403, 500, 502, 503, 504
def register_error_handlers(app: Flask):
    @app.errorhandler(404)
    def page_not_found(error):
        return redirect(url_for('common_routes.dashboard_page'))  # or render_template('404.html'), 404

    @app.errorhandler(429)
    def ratelimit_handler(e):
        retry_after = getattr(e, "retry_after", 60)
        try:
            retry_after = int(retry_after)
        except (ValueError, TypeError):
            retry_after = 60
        return render_template("error_handlers/login_tries_exceeded.html", retry_after=retry_after), 429

    @app.errorhandler(500)
    def internal_server_error(e):
        logger.error(f"Internal Server Error: {e}")
        return render_template("error_handlers/500.html"), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        # e.description contains the error message
        return render_template("error_handlers/csrf_error.html"), 401

    @app.errorhandler(405)
    def method_not_allowed_error(e):
        return render_template("error_handlers/405.html")

