#!/usr/bin/env python
import os
import sys
from pathlib import Path


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "questbetween.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
