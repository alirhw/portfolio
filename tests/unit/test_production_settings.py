import importlib


def test_production_settings_database_url_and_storages(monkeypatch):
    """
    Verify DATABASE_URL parsing and WhiteNoise storage configuration.
    """
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-1234567890-test")
    monkeypatch.setenv("DATABASE_URL", "postgresql://dbuser:dbpass@postgres:5432/portfolio_prod")
    monkeypatch.setenv("ALLOWED_HOSTS", "portfolio.example.com,localhost")
    monkeypatch.setenv("SENTRY_DSN", "")

    import config.settings.production as prod_settings

    importlib.reload(prod_settings)

    assert prod_settings.DEBUG is False
    assert prod_settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"
    assert prod_settings.DATABASES["default"]["NAME"] == "portfolio_prod"
    assert prod_settings.DATABASES["default"]["USER"] == "dbuser"
    assert prod_settings.DATABASES["default"]["CONN_HEALTH_CHECKS"] is True

    # Check WhiteNoise storage
    storage_backend = prod_settings.STORAGES["staticfiles"]["BACKEND"]
    assert "whitenoise" in storage_backend.lower()

    # Check logging structure
    assert "verbose" in prod_settings.LOGGING["formatters"]
    assert "console" in prod_settings.LOGGING["handlers"]


def test_csrf_trusted_origins_constructed_correctly(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("ALLOWED_HOSTS", "mysite.com,api.mysite.com")
    monkeypatch.setenv("DATABASE_URL", "sqlite:////tmp/test.db")

    import config.settings.production as prod_settings

    importlib.reload(prod_settings)

    assert "https://mysite.com" in prod_settings.CSRF_TRUSTED_ORIGINS
    assert "https://api.mysite.com" in prod_settings.CSRF_TRUSTED_ORIGINS
