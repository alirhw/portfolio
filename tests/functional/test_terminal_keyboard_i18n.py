import pytest


@pytest.mark.django_db
def test_terminal_maintains_ltr_on_persian_page(client):
    # Request Persian language page
    response = client.get("/fa/")
    assert response.status_code == 200

    html = response.content.decode()

    # Verify parent document tag is RTL
    assert 'lang="fa"' in html
    assert 'dir="rtl"' in html

    # Verify terminal element is explicitly LTR and lang=en
    assert 'id="portfolio-terminal"' in html
    assert 'dir="ltr"' in html
    assert 'lang="en"' in html
