from django import forms
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    # Hidden honeypot field to trap automated spam bots
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(
            attrs={
                "autocomplete": "off",
                "tabindex": "-1",
                "aria-hidden": "true",
            }
        ),
    )

    sender_name = forms.CharField(
        max_length=120,
        validators=[MinLengthValidator(2, message=_("Name must be at least 2 characters long."))],
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Your Name"),
                "class": "form-input",
                "required": "required",
            }
        ),
    )
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "placeholder": _("your.email@example.com"),
                "class": "form-input",
                "required": "required",
            }
        ),
    )
    message = forms.CharField(
        max_length=3000,
        validators=[
            MinLengthValidator(10, message=_("Message must be at least 10 characters long."))
        ],
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": _("Your message here..."),
                "class": "form-textarea",
                "required": "required",
            }
        ),
    )

    class Meta:
        model = ContactMessage
        fields = ["sender_name", "email", "message"]

    def clean_website(self):
        """Honeypot validation: Reject submission if honeypot is filled."""
        website_value = self.cleaned_data.get("website")
        if website_value:
            raise forms.ValidationError(_("Spam detected."))
        return website_value

    def clean_sender_name(self):
        name = self.cleaned_data.get("sender_name", "").strip()
        return name

    def clean_message(self):
        message = self.cleaned_data.get("message", "").strip()
        return message
