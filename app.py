from werkzeug.serving import WSGIRequestHandler
from flask import Flask, session, request, render_template
from flask_socketio import SocketIO, disconnect, emit
import psutil, GPUtil

from config import Config
from infrastructure import cm, limiter, init_csrf
from routes import routes
from error_handlers import register_error_handlers
from logger import logger

WSGIRequestHandler.server_version = ""
WSGIRequestHandler.sys_version = ""

app = Flask(__name__)
app.config.from_object(Config)

app.secret_key = app.config["SECRET_KEY"]
app.permanent_session_lifetime = app.config["SESSION_LIFETIME"]

init_csrf(app)
limiter.init_app(app)
register_error_handlers(app)

for r in routes:
    app.register_blueprint(r)

socketio = SocketIO(app, manage_session=False, async_mode="threading")

# Pre-Check
@app.before_request
def load_user_type():
    if request.remote_addr in app.config["BLACKLISTED_IPS"]:
        return render_template("error_handlers/blacklisted.html"), 403 # 403 = Forbidden
    if app.config["MAINTENANCE_MODE"]:
        if request.remote_addr not in app.config["ALLOWED_IPS"]:
            return render_template("error_handlers/maintenance_mode.html"), 503  # 503 = Service Unavailable

# Hide server information
@app.after_request
def hide_server_headers(response):
    # remove the Server header (Werkzeug or others)
    response.headers.pop('Server', None)
    response.headers["Server"] = "Unknown"

    # remove any X-Powered-By header if present
    response.headers.pop('X-Powered-By', None)

    # optionally set a generic Server header
    # response.headers['Server'] = 'MyApp'   # or set nothing

    # add security headers (recommended)
    response.headers.setdefault('X-Content-Type-Options', 'nosniff')
    response.headers.setdefault('X-Frame-Options', 'DENY')
    response.headers.setdefault('Referrer-Policy', 'no-referrer-when-downgrade')
    response.headers.setdefault('X-XSS-Protection', '0')  # deprecated, but some still use
    return response


# Global Jinja2 variables injection
@app.context_processor
def inject_global_variables():
    user = cm.get_user_by_username(session.get("username"))
    user_role = "na"
    logged_in = False
    if user is not None:
        user_role = user.role
        logged_in = True
    return dict(
        sidebar_links = cm.get_features_by_role(user_role),
        ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest",
        name_surname=f"{user.name} {user.surname}" if user else "",
        page_theme = user.theme if user and user.theme else "light",
        logged_in = logged_in
    )

# Server status socket
@socketio.on("connect", namespace="/server-status")
def socket_connect_server_status():
    if session.get("role", "") != "system_admin":
        disconnect()

def socket_send_server_status():
    while True:
        gpus = GPUtil.getGPUs()
        gpu_load = gpus[0].load * 100 if gpus else 0
        gpu_temp = gpus[0].temperature if gpus else 0
        socketio.emit('status', {
            'cpu': psutil.cpu_percent(),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent,
            'gpu': gpu_load,
            'gpu_temp': gpu_temp
        }, namespace="/server-status")
        socketio.sleep(0.5)  # non-blocking sleep


connected_users_message = {}

# Messaging socket
@socketio.on("connect", namespace="/messaging")
def socket_connect_message():
    username = session.get("username")
    if not username or not cm.get_user_by_username(username):
        return

    if username not in connected_users_message:
        connected_users_message[username] = []

    if request.sid not in connected_users_message[username]:
        connected_users_message[username].append(request.sid)

    logger.info(f"{username} connected (sid: {request.sid})")


@socketio.on("disconnect", namespace="/messaging")
def socket_disconnect_message():
    # Remove only the specific SID that disconnected
    for user, sids in list(connected_users_message.items()):
        if request.sid in sids:
            sids.remove(request.sid)
            logger.info(f"{user} disconnected one session ({request.sid})")
            # If user has no more active connections, remove them from dict
            if not sids:
                try:
                    del connected_users_message[user]
                except KeyError:
                    logger.error("Couldn't find user in connected_users_message (website.py, 135)")
            break


@socketio.on("message_in", namespace="/messaging")
def socket_handle_message(data):
    message = data.get("message")
    md_id = data.get("md_id")
    from_who = session.get("username")
    md = cm.get_md_by_id(md_id)
    if md is None:
        return

    cm.new_message(message, md, cm.get_user_by_username(from_who))

    for contact_object in md.contacts:
        contact = contact_object.username
        target_sids = connected_users_message.get(contact)
        if not target_sids:  # None or empty list
            logger.warning(f"{contact} is not connected, skipping")
            continue
        for target_sid in target_sids:
            emit("message_out", {
                "message": message,
                "from_who": from_who,
                "md_id": md_id
            }, namespace="/messaging", to=target_sid)


# Start background thread
socketio.start_background_task(socket_send_server_status)

if __name__ == "__main__":
    socketio.run(
        app,
        allow_unsafe_werkzeug=True,
        host="0.0.0.0",
        port=5000,
    )
