from flask import Blueprint, session, redirect, url_for, render_template
from infrastructure import cm

student_routes = Blueprint("student_routes", __name__, url_prefix="/student")


@student_routes.before_request
def role_check():
    if not session.get("username"): return redirect(url_for("common_routes.login_page"))
    user = cm.get_user_by_username(session.get("username"), "student")
    if not user or user.role != "student" : return redirect(url_for("common_routes.dashboard_page"))

@student_routes.route("/homeworks")
def homeworks_page():
    student = cm.get_user_by_username(session.get("username"), "student")
    return render_template("student/homework.html", homeworks = student.homeworks, numbers = (student.total_homeworks, student.done_homeworks, student.missing_homeworks), background="e6ccff")

@student_routes.route("/program")
def program_page():
    student = cm.get_user_by_username(session.get("username"), "student")
    return render_template("student/program.html", lessons = student.lessons, background="ccf2ff")