from flask import Blueprint, render_template, render_template_string, request, session, redirect, url_for

from CLib.Extras.configs import TeacherConfig
from infrastructure import cm
from forms import TeachersCreationForm
from logger import logger

admin_routes = Blueprint("admin_routes", __name__, url_prefix="/admin")

@admin_routes.before_request
def role_check():
    if not session.get("username"): return redirect(url_for("common_routes.login_page"))
    user = cm.get_user_by_username(session.get("username"), "system_admin")
    if not user or user.role != "system_admin" : return redirect(url_for("common_routes.dashboard_page"))

@admin_routes.route("/dashboard")
def dashboard_page():
    return render_template("admin/dashboard.html", numbers= (len(cm.users), len(cm.teachers), len(cm.students), len(cm.parents)))

@admin_routes.route("/create-user", methods= ["GET", "POST"])
def create_teacher_page():
    form = TeachersCreationForm()
    if form.validate_on_submit():
        name = form.name.data
        surname = form.surname.data
        gender = form.gender.data
        max_students = form.max_students.data
        modules = form.modules.data
        cm.create_teacher(name, surname, gender, TeacherConfig(max_students, modules))
    elif request.method == "POST":
        logger.error("Form errors:", form.errors)
    return render_template("admin/create_teacher.html", form= form)

@admin_routes.route("/users")
def users_page():
    return render_template("admin/users.html", users= cm.users, background="ccffe6")

@admin_routes.route("/teachers")
def teachers_page():
    return render_template("admin/teachers.html", teachers= cm.teachers, background="ffd6cc")

@admin_routes.route("/teachers/view/<username>")
def view_teacher_page(username: str):
    teacher = cm.get_user_by_username(username, "teacher")
    if not teacher: return redirect(url_for("admin_routes.teachers_page"))
    return render_template("admin/view_teacher.html", teacher=teacher, background="d9ffb3")

@admin_routes.route("/students")
def students_page():
    return render_template("admin/students.html", students= cm.students, background="fff2cc")

@admin_routes.route("/admin-panel/", defaults={"section": "not_set"})
@admin_routes.route("/admin-panel/<section>")
def admin_panel(section = "not_set"):
    if section not in ["not_set", "server_status", "logs", "secure_panel"]:
        logger.warning("Redirecting due to section error.")
        return redirect(url_for("admin_routes.dashboard_page"))
    return render_template(f"admin/admin_panel_{section}.html", background="ccebff")
