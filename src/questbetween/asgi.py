import os
import sys
from pathlib import Path

from django.core.asgi import get_asgi_application

project_root = Path(__file__).resolve().parents[2]
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "questbetween.settings")

application = get_asgi_application()
