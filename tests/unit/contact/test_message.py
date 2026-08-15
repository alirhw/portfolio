import pytest

from apps.contact.models import ContactMessage


@pytest.mark.django_db
def test_contact_message_can_be_created_with_defaults():
    msg = ContactMessage.objects.create(
        name="John Doe",
        email="john@example.com",
        subject="Inquiry regarding backend work",
        message="Hello, I would like to discuss a project.",
        ip_address="192.168.1.100",
    )

    assert msg.pk is not None
    assert msg.is_read is False
    assert msg.created_at is not None
    assert str(msg) == "Message from John Doe (john@example.com)"


@pytest.mark.django_db
def test_contact_message_is_read_defaults_to_false():
    msg = ContactMessage.objects.create(
        name="Jane Smith",
        email="jane@example.com",
        message="Test message.",
    )

    assert msg.is_read is False
    assert msg.ip_address is None


@pytest.mark.django_db
def test_contact_message_ip_address_storage():
    msg_ipv4 = ContactMessage.objects.create(
        name="IPv4 User",
        email="ipv4@example.com",
        message="IPv4 test.",
        ip_address="203.0.113.195",
    )
    msg_ipv6 = ContactMessage.objects.create(
        name="IPv6 User",
        email="ipv6@example.com",
        message="IPv6 test.",
        ip_address="2001:db8::8a2e:370:7334",
    )

    assert msg_ipv4.ip_address == "203.0.113.195"
    assert msg_ipv6.ip_address == "2001:db8::8a2e:370:7334"


@pytest.mark.django_db
def test_contact_message_descending_created_at_index():
    index_fields = [index.fields for index in ContactMessage._meta.indexes]
    assert ["-created_at"] in index_fields
