from .common_routes import common_routes
from .admin_routes import admin_routes
from .teacher_routes import teacher_routes
from .student_routes import student_routes
from .parent_routes import parent_routes

routes = [common_routes, admin_routes, teacher_routes, student_routes, parent_routes]
