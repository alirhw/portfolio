import pytest
from playwright.sync_api import Page, expect


@pytest.mark.django_db
def test_theme_switching_journey(live_server, page: Page, seed_e2e_data):
    """
    Scenario 1: Initial load and light/dark theme switching via navbar toggle.
    """
    page.goto(f"{live_server.url}/en/")

    html = page.locator("html")
    theme_btn = page.locator("#theme-toggle")

    # Verify initial state
    expect(theme_btn).to_be_visible()
    initial_theme = html.get_attribute("data-theme") or "light"

    # Click to toggle theme
    theme_btn.click()
    expected_theme = "dark" if initial_theme == "light" else "light"
    expect(html).to_have_attribute("data-theme", expected_theme)

    # Verify localStorage persistence after reload
    page.reload()
    expect(html).to_have_attribute("data-theme", expected_theme)


@pytest.mark.django_db
def test_terminal_interactive_and_autocomplete_journey(live_server, page: Page, seed_e2e_data):
    """
    Scenario 2: Terminal interaction, Tab autocomplete, and execution of help and skills commands.
    """
    page.goto(f"{live_server.url}/en/")

    terminal_section = page.locator("#terminal-section")
    terminal_input = page.locator("#terminal-input")
    terminal_output = page.locator("#terminal-output")

    # Confirm progressive enhancement initialization
    expect(terminal_section).to_be_visible()

    # Test 1: Type 'sk' and press Tab to autocomplete to 'skills '
    terminal_input.fill("sk")
    terminal_input.press("Tab")
    expect(terminal_input).to_have_value("skills ")

    # Execute command with Enter
    terminal_input.press("Enter")

    # Confirm skills rendered in output
    expect(terminal_output).to_contain_text("Technical Competencies")
    expect(terminal_output).to_contain_text("Python")
    expect(terminal_output).to_contain_text("Django")

    # Test 2: Execute help command
    terminal_input.fill("help")
    terminal_input.press("Enter")
    expect(terminal_output).to_contain_text("Available commands:")


@pytest.mark.django_db
def test_language_and_bidi_layout_journey(live_server, page: Page, seed_e2e_data):
    """
    Scenario 3: Language switch to Persian, RTL layout validation, and LTR terminal isolation.
    """
    # Load English page
    page.goto(f"{live_server.url}/en/")
    html = page.locator("html")
    expect(html).to_have_attribute("lang", "en")
    expect(html).to_have_attribute("dir", "ltr")

    # Click language switcher to toggle to Persian
    lang_btn = page.locator(".lang-btn")
    expect(lang_btn).to_be_visible()
    lang_btn.click()

    # Confirm redirect to /fa/ with RTL direction
    expect(html).to_have_attribute("lang", "fa")
    expect(html).to_have_attribute("dir", "rtl")
    expect(page.locator("body")).to_contain_text("پروژه‌ها")

    # Confirm LTR isolation on terminal window even in Persian mode
    terminal_window = page.locator("#portfolio-terminal")
    expect(terminal_window).to_have_attribute("dir", "ltr")
    expect(terminal_window).to_have_attribute("lang", "en")


@pytest.mark.django_db
def test_contact_form_submission_journey(live_server, page: Page, seed_e2e_data):
    """
    Scenario 4: Contact form filling and successful message submission.
    """
    page.goto(f"{live_server.url}/en/")

    # Locate contact form inputs
    name_input = page.locator("input[name='sender_name']")
    email_input = page.locator("input[name='email']")
    message_input = page.locator("textarea[name='message']")
    submit_btn = page.locator("button[type='submit']:has-text('Send')")

    # Fill inputs with valid data
    name_input.fill("Grace Hopper")
    email_input.fill("grace@compiler.org")
    message_input.fill("Hello, let us collaborate on language compiler design.")

    # Submit form
    submit_btn.click()

    # Confirm success message is displayed
    expect(page.locator(".messages, .alert, .toast, body")).to_contain_text(
        "Thank you! Your message has been sent successfully."
    )
