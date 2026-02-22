import json
from pathlib import Path
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from CLib import CreationManager
from CLib.Extras.configs import CreationManagerConfig, Module, Subject, Objectives, Objective
from CLib.Users.system_admin import SystemAdmin


# ── Constants ────────────────────────────────────────────────────────────────

OBJECTIVES_DIR = Path("Database/objectives/high_school")
DB_PATH = "Database/cm.pkl"

MODULES = [
    Module("student_creation", "Student Creation"),
]

SUBJECTS = [
    Subject("mathematics", "Matematik"),
    Subject("physics",     "Fizik"),
    Subject("chemistry",   "Kimya"),
    Subject("biology",     "Biyoloji"),
    Subject("history",     "Tarih"),
    Subject("geography",   "Coğrafya"),
    Subject("philosophy",  "Felsefe"),
    Subject("religion",    "Din Kültürü"),
    Subject("turkish",     "Türkçe"),
]


# ── Loaders ──────────────────────────────────────────────────────────────────

def load_objectives(subjects: list[Subject]) -> Objectives:
    """Load objectives for each subject from JSON files."""
    objectives: dict[str, list[Objective]] = {}

    for subject in subjects:
        path = OBJECTIVES_DIR / f"{subject.key}.json"
        with path.open(encoding="utf-8") as f:
            data = json.load(f)

        objectives[subject.key] = [
            Objective(
                entry.get("subject"),
                entry.get("objective"),
                entry.get("code"),
                entry.get("depth"),
            )
            for entry in data
        ]

    return Objectives(objectives)


def build_cm_config() -> CreationManagerConfig:
    return CreationManagerConfig(
        DB_PATH, 50, 10, 45,
        MODULES, SUBJECTS,
        load_objectives(SUBJECTS),
    )


def load_creation_manager(config: CreationManagerConfig) -> CreationManager:
    admin = SystemAdmin("admin", "admin123", "Demo", "Admin")
    cm = CreationManager.load(config.DATABASE_PATH, admin, config)
    cm._config = config  # Reload config class every time
    return cm


# ── Flask extensions ─────────────────────────────────────────────────────────

def create_limiter() -> Limiter:
    return Limiter(
        get_remote_address,
        default_limits=["100 per minute"],
        storage_uri="memory://",
    )


def init_csrf(app) -> CSRFProtect:
    """Attach CSRF protection to the Flask app and return the instance."""
    return CSRFProtect(app)


# ── Initialisation ───────────────────────────────────────────────────────────

CM_CONFIG = build_cm_config()
cm = load_creation_manager(CM_CONFIG)
limiter = create_limiter()
csrf: CSRFProtect | None = None
