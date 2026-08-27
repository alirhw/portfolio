"""
Production pre-flight check script.
Verifies database connectivity, applies pending migrations,
and tests persistent media storage access.
"""

import os
import pathlib
import sys
import tempfile

import django

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Ensure project root is on sys.path
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from django.apps import apps  # noqa: E402

# Initialize Django environment safely if not already initialized
if not apps.ready:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
    django.setup()

from django.core.management import call_command  # noqa: E402
from django.db import connection  # noqa: E402


def check_database_connection():
    """Verify production database connectivity by executing a lightweight query."""
    print("--> [1/3] Checking Production Database connectivity...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            row = cursor.fetchone()
            if not row or row[0] != 1:
                raise RuntimeError("Unexpected response from database query.")
        print("[OK] Database connection verified successfully.")
    except Exception as exc:
        print(f"[FAIL] Database connection failed: {exc}", file=sys.stderr)
        sys.exit(1)


def run_database_migrations():
    """Apply pending database migrations without interactive prompts."""
    print("--> [2/3] Applying pending database migrations...")
    try:
        call_command("migrate", interactive=False, verbosity=1)
        print("[OK] Database migrations applied successfully.")
    except Exception as exc:
        print(f"[FAIL] Failed to apply database migrations: {exc}", file=sys.stderr)
        sys.exit(1)


def check_media_storage_volume():
    """Verify Railway persistent volume write and read access at MEDIA_ROOT."""
    print("--> [3/3] Verifying Railway Persistent Volume write access at /app/media...")
    media_dir = os.getenv("MEDIA_ROOT", "/app/media")
    os.makedirs(media_dir, exist_ok=True)

    try:
        with tempfile.NamedTemporaryFile(dir=media_dir, prefix="probe_", suffix=".tmp") as tmp_file:
            tmp_file.write(b"storage_read_write_verification")
            tmp_file.flush()
            assert os.path.exists(tmp_file.name), "Temporary media file was not created."
        print(f"[OK] Persistent volume at '{media_dir}' is writable and healthy.")
    except Exception as exc:
        print(f"[FAIL] Media storage volume permission failure: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    print("========================================================================")
    print("RUNNING PRODUCTION PRE-FLIGHT DATABASE & STORAGE VERIFICATION")
    print("========================================================================")
    check_database_connection()
    run_database_migrations()
    check_media_storage_volume()
    print("========================================================================")
    print("[OK] PRE-FLIGHT CHECKS PASSED: READY TO SERVE TRAFFIC")
    print("========================================================================")
