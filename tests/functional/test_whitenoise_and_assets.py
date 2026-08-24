import os
import shutil
import tempfile

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.management import call_command
from django.test import SimpleTestCase, override_settings

TEST_STATIC_DIR = tempfile.mkdtemp(prefix="whitenoise_test_")


@override_settings(
    DEBUG=False,
    STATIC_ROOT=TEST_STATIC_DIR,
    STATIC_URL="/static/",
    STORAGES={
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        }
    },
)
class WhiteNoiseAssetVerificationTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        call_command("collectstatic", interactive=False, verbosity=0, clear=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(TEST_STATIC_DIR):
            shutil.rmtree(TEST_STATIC_DIR, ignore_errors=True)
        super().tearDownClass()

    def test_manifest_file_generated(self):
        """
        Verify staticfiles.json manifest file exists and contains hash mappings.
        """
        manifest_path = os.path.join(settings.STATIC_ROOT, "staticfiles.json")
        self.assertTrue(os.path.exists(manifest_path))

    def test_css_asset_hashed_and_compressed(self):
        """
        Verify CSS asset has content hash in URL and is gzip compressed on disk.
        """
        hashed_css_url = staticfiles_storage.url("css/main.css")
        self.assertIn("main.", hashed_css_url)

        rel_path = hashed_css_url.replace(settings.STATIC_URL, "")
        full_path = os.path.join(settings.STATIC_ROOT, rel_path)
        self.assertTrue(os.path.exists(full_path))

        # Check for gzip compressed version (.gz)
        gzip_path = f"{full_path}.gz"
        self.assertTrue(os.path.exists(gzip_path))

    def test_whitenoise_serves_immutable_cache_headers(self):
        """
        Verify response includes max-age and public Cache-Control headers.
        """
        hashed_css_url = staticfiles_storage.url("css/main.css")
        response = self.client.get(hashed_css_url)

        self.assertEqual(response.status_code, 200)
        cache_control = response.headers.get("Cache-Control", "")
        self.assertIn("max-age=31536000", cache_control)
        self.assertIn("public", cache_control)
