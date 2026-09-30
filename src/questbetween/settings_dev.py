from pathlib import Path

from . import settings as base_settings

for setting_name in dir(base_settings):
    if setting_name.isupper():
        globals()[setting_name] = getattr(base_settings, setting_name)

# Local host-run profile: avoids requiring PostgreSQL when testing UI flows.
BASE_DIR = Path(__file__).resolve().parents[2]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(BASE_DIR / "dev.sqlite3"),
    }
}
