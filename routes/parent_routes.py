from flask import Blueprint, session, redirect, url_for, render_template

from infrastructure import cm


parent_routes = Blueprint("parent_routes", __name__, url_prefix="/parent")

@parent_routes.before_request
def role_check():
    if not session.get("username"): return redirect(url_for("common_routes.login_page"))
    user = cm.get_user_by_username(session.get("username"), "parent")
    if not user or user.role != "parent" : return redirect(url_for("common_routes.dashboard_page"))

@parent_routes.route("/program")
def program_page():
    return render_template("common/under_construction.html")

@parent_routes.route("/homework")
def homework_page():
    return render_template("common/under_construction.html")
