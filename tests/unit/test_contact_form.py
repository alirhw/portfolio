import pytest

from apps.contact.forms import ContactForm


def test_contact_form_valid_data():
    form_data = {
        "sender_name": "John Doe",
        "email": "john@example.com",
        "message": "Hello, I would like to discuss a project collaboration.",
        "website": "",  # Empty honeypot (natural user input)
    }
    form = ContactForm(data=form_data)
    assert form.is_valid()


def test_contact_form_honeypot_triggers_spam_error():
    form_data = {
        "sender_name": "Spam Bot",
        "email": "bot@spam.com",
        "message": "Check out this random link right now!",
        "website": "http://spam-link.ru",  # Honeypot filled by bot
    }
    form = ContactForm(data=form_data)

    assert not form.is_valid()
    assert "website" in form.errors
    assert "Spam detected." in form.errors["website"]


def test_contact_form_invalid_email():
    form_data = {
        "sender_name": "Jane",
        "email": "not-a-valid-email",
        "message": "Testing invalid email input format.",
        "website": "",
    }
    form = ContactForm(data=form_data)

    assert not form.is_valid()
    assert "email" in form.errors


def test_contact_form_min_length_validation():
    form_data = {
        "sender_name": "A",  # Less than 2 chars
        "email": "valid@example.com",
        "message": "Short",  # Less than 10 chars
        "website": "",
    }
    form = ContactForm(data=form_data)

    assert not form.is_valid()
    assert "sender_name" in form.errors
    assert "message" in form.errors


@pytest.mark.django_db
def test_contact_form_save_creates_database_record():
    form_data = {
        "sender_name": "Real Client",
        "email": "client@company.com",
        "message": "Interested in hiring for a backend project.",
        "website": "",
    }
    form = ContactForm(data=form_data)
    assert form.is_valid()

    instance = form.save()
    assert instance.id is not None
    assert instance.sender_name == "Real Client"
    assert instance.is_notified is False
