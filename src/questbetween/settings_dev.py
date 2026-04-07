from pathlib import Path

from .settings import *  # noqa: F403,F401

# Local host-run profile: avoids requiring PostgreSQL when testing UI flows.
BASE_DIR = Path(__file__).resolve().parents[2]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "dev.sqlite3",
    }
}
