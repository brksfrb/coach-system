from flask import Blueprint, session, url_for, redirect, render_template, request

from CLib.Extras.messaging import MessageData
from infrastructure import limiter, cm
from forms import LoginForm, SettingsForm, ChangePasswordForm, MessagingForm

common_routes = Blueprint("common_routes", __name__)
ROLES = ["student", "teacher", "principal", "admin", "dietitian"]

@common_routes.route("/login", methods = ["GET", "POST"])
@limiter.limit("3 per minute", methods=["POST"])
def login_page():
    form = LoginForm()
    if form.validate_on_submit() and request.method == "POST":
        username = form.username.data.lower()
        password = form.password.data
        user = cm.get_user_by_username(username)
        if user:
            if password == user.password:
                session.clear()
                session.permanent = True
                session["username"] = user.username
                session["role"] = user.role
                session["logged_in"] = True

    if session.get("role") or session.get("role") in ROLES:
        return redirect(url_for("common_routes.dashboard_page"))
    return render_template("common/login.html", form=form)

@common_routes.route("/logout", methods = ["GET"])
def logout_page():
    session.clear()
    return redirect(url_for("common_routes.login_page"))

@common_routes.route("/", methods = ["GET"])
def base_page():
    if not session.get("logged_in"):
        return redirect(url_for("common_routes.login_page"))
    return redirect(url_for("common_routes.dashboard_page"))

@common_routes.route("/dashboard", methods = ["GET"])
def dashboard_page():
    user = cm.get_user_by_username(session.get("username"))
    if user is not None:
        if user.role == "system_admin":
            return redirect(url_for("admin_routes.dashboard_page"))
    else:
        return redirect(url_for("common_routes.login_page"))
    return render_template("common/dashboard.html", background="ffebcc")

@common_routes.route("/settings", methods = ["GET", "POST"])
def settings_page():
    user = cm.get_user_by_username(session.get("username"))
    if not user: return redirect(url_for("common_routes.dashboard_page"))
    form = SettingsForm()

    if request.method == "POST" and form.validate_on_submit():
        theme = form.theme.data
        cm.change_user_settings(user, theme, "", False)
    else:
        form.theme.data = user.theme
    return render_template("common/settings.html", user=user, form=form, background="d9ffcc")

@common_routes.route("/messaging", methods=["GET", "POST"])
def messaging_page():
    user = cm.get_user_by_username(session.get("username"))
    if not user:
        logger.info("Redirecting to dashboard.")
        return redirect(url_for("common_routes.dashboard_page"))
    messages: list[dict] = cm.get_user_message_data_jsonized(user)
    form = MessagingForm()
    if form.validate_on_submit():
        pass

    contacts = cm.get_user_contact_data(user)
    return render_template("common/messaging.html", messages=messages if messages else [], contacts=contacts, user=user, form=form, background="ffec70")

@common_routes.route("/change-password", methods= ["GET", "POST"])
@limiter.limit("3 per minute", methods=["POST"])
def change_password_page():
    form = ChangePasswordForm()
    if request.method == "POST":
        current_password_input = form.old_password.data
        user = cm.get_user_by_username(session.get("username"))
        current_password_real = user.password
        if current_password_input != current_password_real:
            return render_template("common/change_password.html", try_status="Hatalı eski şifre.", status_color = "red", form=form, background="ffaa80")
        new_password = form.new_password.data
        new_password_confirmation = form.new_password_again.data
        if new_password != new_password_confirmation:
            return render_template("common/change_password.html", try_status= "Girdiğiniz yeni şifreler birbirinden farklı.", status_color = "red", form=form, background="ffaa80")
        user.change_password(current_password_input, new_password)
        return render_template("common/change_password.html", try_status = "Şifreniz başarıyla değiştirildi.", status_color = "green", form=form, background="ffaa80")

    return render_template("common/change_password.html", try_status = "empty", status_color= "green", form=form, background="ffaa80")