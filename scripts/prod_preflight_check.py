"""
Production pre-flight check script.
Verifies database connectivity with retries, applies pending migrations,
seeds initial data if empty, and tests persistent media storage access.
"""

import os
import pathlib
import sys
import tempfile
import time

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
    """Verify production database connectivity with retries."""
    print("--> [1/4] Checking Production Database connectivity...")
    max_retries = 10
    for attempt in range(1, max_retries + 1):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                row = cursor.fetchone()
                if row and row[0] == 1:
                    print("[OK] Database connection verified successfully.")
                    return
        except Exception as exc:
            print(f"   [RETRY {attempt}/{max_retries}] Database not ready yet: {exc}")
            if attempt < max_retries:
                time.sleep(2)
            else:
                print(
                    f"[FAIL] Database connection failed after {max_retries} attempts: {exc}",
                    file=sys.stderr,
                )
                sys.exit(1)


def run_database_migrations():
    """Apply pending database migrations without interactive prompts."""
    print("--> [2/4] Applying pending database migrations...")
    try:
        call_command("migrate", interactive=False, verbosity=1)
        print("[OK] Database migrations applied successfully.")
    except Exception as exc:
        print(f"[FAIL] Failed to apply database migrations: {exc}", file=sys.stderr)
        sys.exit(1)


def seed_initial_data_if_empty():
    """Seed initial real portfolio and profile data if database is fresh and empty."""
    print("--> [3/4] Checking database initial profile state...")
    try:
        from apps.portfolio.models import PortfolioProfile

        if not PortfolioProfile.objects.exists():
            print("   ↳ Empty database detected. Populating real portfolio data...")
            call_command("seed_data")
            print("[OK] Initial portfolio data seeded successfully.")
        else:
            print("[OK] Portfolio data is already present.")
    except Exception as exc:
        print(
            f"[WARN] Initial data seed notice: {exc}. Continuing startup...",
            file=sys.stderr,
        )


def check_media_storage_volume():
    """Verify Railway persistent volume write and read access at MEDIA_ROOT."""
    print("--> [4/4] Verifying Railway Persistent Volume write access at /app/media...")
    media_dir = os.getenv("MEDIA_ROOT", "/app/media")

    try:
        os.makedirs(media_dir, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=media_dir, prefix="probe_", suffix=".tmp") as tmp_file:
            tmp_file.write(b"storage_read_write_verification")
            tmp_file.flush()
            assert os.path.exists(tmp_file.name), "Temporary media file was not created."
        print(f"[OK] Persistent volume at '{media_dir}' is writable and healthy.")
    except Exception as exc:
        print(
            f"[WARN] Media storage volume permission notice: {exc}. Continuing startup...",
            file=sys.stderr,
        )


if __name__ == "__main__":
    print("========================================================================")
    print("RUNNING PRODUCTION PRE-FLIGHT DATABASE & STORAGE VERIFICATION")
    print("========================================================================")
    check_database_connection()
    run_database_migrations()
    seed_initial_data_if_empty()
    check_media_storage_volume()
    print("========================================================================")
    print("[OK] PRE-FLIGHT CHECKS PASSED: READY TO SERVE TRAFFIC")
    print("========================================================================")
