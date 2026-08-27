import os

import pytest

from scripts.prod_preflight_check import (
    check_database_connection,
    check_media_storage_volume,
    run_database_migrations,
)


@pytest.mark.django_db
def test_preflight_database_check_passes():
    """Verify preflight database connectivity check runs cleanly."""
    check_database_connection()


@pytest.mark.django_db
def test_preflight_migrations_execution():
    """Verify preflight migrations execution runs cleanly."""
    run_database_migrations()


def test_preflight_media_storage_volume_writable(tmp_path, monkeypatch):
    """Verify preflight media storage volume check verifies write access."""
    test_media_dir = str(tmp_path / "media")
    monkeypatch.setenv("MEDIA_ROOT", test_media_dir)

    check_media_storage_volume()
    assert os.path.exists(test_media_dir)
