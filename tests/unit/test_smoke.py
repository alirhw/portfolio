import os

from django.apps import apps


def test_django_smoke():
    assert os.environ["DJANGO_SETTINGS_MODULE"] == "config.settings.test"
    assert apps.ready

    installed_apps = {config.name for config in apps.get_app_configs()}

    assert "apps.portfolio" in installed_apps
    assert "apps.contact" in installed_apps
