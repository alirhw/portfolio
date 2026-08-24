import pytest
from playwright.sync_api import Page, expect


@pytest.mark.django_db
def test_accessibility_landmarks_and_skip_link(live_server, page: Page, seed_e2e_data):
    """
    Verify ARIA landmarks and skip link presence/functionality.
    """
    page.goto(f"{live_server.url}/en/")

    # Check main ARIA landmark roles
    expect(page.locator("header[role='banner']")).to_be_visible()
    expect(page.locator("main#main-content[role='main']")).to_be_visible()
    expect(page.locator("footer[role='contentinfo']")).to_be_visible()
    expect(page.locator("nav[role='navigation']")).to_be_visible()

    # Check Skip Link
    skip_link = page.locator(".skip-to-content")
    expect(skip_link).to_have_attribute("href", "#main-content")


@pytest.mark.django_db
def test_seo_meta_tags_and_opengraph_integrity(live_server, page: Page, seed_e2e_data):
    """
    Verify Title, Description, Canonical, and OpenGraph meta tags integrity.
    """
    page.goto(f"{live_server.url}/en/")

    # Title and meta description validation
    title = page.title()
    assert len(title) > 0

    description = page.locator("meta[name='description']").get_attribute("content")
    assert description is not None and len(description) > 10

    # OpenGraph meta tags validation
    og_title = page.locator("meta[property='og:title']").get_attribute("content")
    og_image = page.locator("meta[property='og:image']").get_attribute("content")
    canonical = page.locator("link[rel='canonical']").get_attribute("href")

    assert og_title is not None
    assert og_image is not None
    assert canonical is not None


@pytest.mark.django_db
def test_all_interactive_elements_have_accessible_labels(live_server, page: Page, seed_e2e_data):
    """
    Ensure all buttons and inputs have accessible names/labels or associated label tags.
    """
    page.goto(f"{live_server.url}/en/")

    buttons = page.locator("button").all()
    for btn in buttons:
        has_text = len((btn.text_content() or "").strip()) > 0
        has_aria_label = btn.get_attribute("aria-label") is not None
        assert has_text or has_aria_label, f"Button {btn} misses accessible label"

    inputs = page.locator("input:not([type='hidden'])").all()
    for inp in inputs:
        has_aria_label = inp.get_attribute("aria-label") is not None
        input_id = inp.get_attribute("id")
        has_linked_label = (
            page.locator(f"label[for='{input_id}']").count() > 0 if input_id else False
        )
        assert has_aria_label or has_linked_label, f"Input {inp} lacks an associated label"
