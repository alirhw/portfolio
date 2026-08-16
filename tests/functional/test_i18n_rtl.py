import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_english_homepage_has_ltr_and_correct_lang(client):
    response = client.get("/en/")
    assert response.status_code == 200

    html = response.content.decode()
    assert 'lang="en"' in html
    assert 'dir="ltr"' in html


@pytest.mark.django_db
def test_persian_homepage_has_rtl_and_correct_lang(client):
    response = client.get("/fa/")
    assert response.status_code == 200

    html = response.content.decode()
    assert 'lang="fa"' in html
    assert 'dir="rtl"' in html


@pytest.mark.django_db
def test_language_switch_retains_next_target(client):
    set_lang_url = reverse("set_language")
    target_path = "/fa/#projects"

    response = client.post(
        set_lang_url,
        data={"language": "fa", "next": target_path},
    )

    assert response.status_code == 302
    assert response.headers["Location"] == target_path


@pytest.mark.django_db
def test_persian_translations_render_in_output(client):
    response = client.get("/fa/")
    html = response.content.decode()

    assert "پروژه‌ها" in html
    assert "مهارت‌ها" in html
