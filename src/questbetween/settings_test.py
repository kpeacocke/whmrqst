import os

from . import settings as base_settings


for setting_name in dir(base_settings):
    if setting_name.isupper():
        globals()[setting_name] = getattr(base_settings, setting_name)

MIDDLEWARE = [
    middleware
    for middleware in base_settings.MIDDLEWARE
    if middleware != "whitenoise.middleware.WhiteNoiseMiddleware"
]
DEBUG = True
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

if os.getenv("QUESTBETWEEN_TEST_DATABASE", "sqlite").lower() in {
    "postgres",
    "postgresql",
}:
    DATABASES = base_settings.DATABASES
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
