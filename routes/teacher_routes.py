from flask import Blueprint, render_template, session, request, redirect, url_for

from CLib.Extras.configs import Row, Hour
from CLib.Extras.date import CustomDate
from CLib.Users.parent import Parent, ParentInformation
from forms import StudentCreationForm, HomeworkCreationForm, make_program_form, StudentNotesForm
from infrastructure import cm
from logger import logger

teacher_routes = Blueprint("teacher_routes", __name__, url_prefix="/teacher")

@teacher_routes.before_request
def role_check():
    if not session.get("username"): return redirect(url_for("common_routes.login_page"))
    user = cm.get_user_by_username(session.get("username"), "teacher")
    if not user or user.role != "teacher" : return redirect(url_for("common_routes.dashboard_page"))

@teacher_routes.route("/create-student", methods= ["GET", "POST"])
def create_student_page():
    form = StudentCreationForm()
    teacher = cm.get_user_by_username(session.get("username"))
    if not teacher: return redirect(url_for("common_routes.dashboard_page"))
    extra_messages = ""
    extra_errors = ""
    if form.errors: extra_errors = "Lütfen tüm alanları doldurduğunuzdan emin olun."
    if form.validate_on_submit():
        name = form.name.data
        surname = form.surname.data
        gender = form.gender.data
        grade = form.grade.data
        num_parents = form.num_parents.data
        parents = []
        if num_parents > 0:
            first_parent_name = form.first_parent_name.data
            first_parent_surname = form.first_parent_surname.data
            first_parent_gender = form.first_parent_gender.data
            first_parent_relation = form.first_parent_relation.data
            parents.append(ParentInformation(first_parent_name, first_parent_surname, first_parent_gender, first_parent_relation))
            if num_parents > 1:
                second_parent_name = form.second_parent_name.data
                second_parent_surname = form.second_parent_surname.data
                second_parent_gender = form.second_parent_gender.data
                second_parent_relation = form.second_parent_relation.data
                parents.append(ParentInformation(second_parent_name, second_parent_surname, second_parent_gender, second_parent_relation))
        if not cm.create_student(name, surname, gender, grade, teacher, parents): extra_errors = f"Öğrenci oluşturulamadı: Öğrenci limitinizi({teacher.config.MAX_STUDENTS}) doldurdunuz."
        else: extra_messages = "Öğrenci başarıyla oluşturuldu."
    return render_template("teacher/create_student.html", form=form, extra_errors= extra_errors, extra_messages= extra_messages, background="e6ccff")

@teacher_routes.route("/students")
def students_page():
    teacher = cm.get_user_by_username(session.get("username"))
    if not teacher: return redirect(url_for("common_routes.dashboard_page"))
    return render_template("teacher/students.html", students= teacher.students, background="ccffe6")

@teacher_routes.route("/students/view/<username>/<section>", methods = ["GET", "POST"])
def manage_student_page(username: str, section: str = "not_set"):
    if section not in ["not_set", "general", "security", "homeworks"]:
        logger.error("Not a valid section for student management.")
        return redirect(url_for("teacher_routes.students_page"))
    teacher = cm.get_user_by_username(session.get("username"), "teacher")
    if not teacher: return redirect(url_for("common_routes.dashboard_page"))
    student = cm.get_user_by_username(username, "student")
    if student is None or student not in teacher.students: return redirect(url_for("teacher_routes.students_page"))
    form = HomeworkCreationForm()
    notes_form = StudentNotesForm()
    if request.method == "GET": notes_form.notes.data = student.notes
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        start_date = CustomDate.date_to_customdate(form.start_date.data)
        end_date = CustomDate.date_to_customdate(form.end_date.data)
        subject = cm.get_turkish_subject(form.subject.data)
        objective = cm.get_objective_by_code(form.objective.data)
        num_questions = form.num_questions.data
        cm.add_student_homework(student, title, description, start_date, end_date, subject, objective, num_questions)
    elif notes_form.validate_on_submit():
        notes = notes_form.notes.data
        if notes is not None:
            student.notes = notes
            cm.save()
    elif request.method == "POST":
        logger.error(f"Form Errors: {form.errors}")
    if section == "homeworks": return render_template("teacher/manage_student_homeworks.html", student = student, form = form, objectives = cm.config.HIGH_SCHOOL_OBJECTIVES.objectives, background="ccffe6")
    return render_template(f"teacher/manage_student_{section}.html", student=student, background="ccffe6", notes_form = notes_form if section == "general" else None)

@teacher_routes.route("/plan-program", methods=["GET", "POST"])
def plan_program_page():
    teacher = cm.get_user_by_username(session.get("username"), "teacher")
    num_columns = 5
    form = make_program_form(students= teacher.students, program= teacher.program, column_count= num_columns)
    if form.validate_on_submit():
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
            for i in range(num_columns + 1):
                field_name = f"{day}_{i}"
                selected_username = getattr(form, field_name).data

                selected_student = next((s for s in teacher.students if s.username == selected_username), None)
                teacher.program.set_box(day, i, selected_student)
        cm.save()
    return render_template("teacher/plan_program.html", form=form, rows = [Row(teacher.program.hours[i - 1][0], teacher.program.hours[i - 1][1]) for i in range(1, num_columns + 1)], background="ccebff")
