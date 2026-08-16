from django import forms
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _

from .models import ContactMessage
from .services.turnstile import TurnstileVerificationService


class ContactForm(forms.ModelForm):
    # 1. Hidden honeypot field to trap automated spam bots
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

    # 2. Turnstile captcha token field submitted from client
    cf_turnstile_response = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )

    sender_name = forms.CharField(
        max_length=120,
        validators=[MinLengthValidator(2, message=_("Name must be at least 2 characters long."))],
        widget=forms.TextInput(
            attrs={"placeholder": _("Your Name"), "class": "form-input", "required": "required"}
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

    def __init__(
        self,
        *args,
        remote_ip: str | None = None,
        turnstile_service: TurnstileVerificationService | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.remote_ip = remote_ip
        self.turnstile_service = turnstile_service or TurnstileVerificationService()

    class Meta:
        model = ContactMessage
        fields = ["sender_name", "email", "message"]

    def clean_website(self):
        """Honeypot validation: Reject submission if honeypot is filled."""
        website_val = self.cleaned_data.get("website")
        if website_val:
            raise forms.ValidationError(_("Spam detected."))
        return website_val

    def clean_sender_name(self):
        name = self.cleaned_data.get("sender_name", "").strip()
        return name

    def clean_message(self):
        message = self.cleaned_data.get("message", "").strip()
        return message

    def clean(self):
        """Final validation and Turnstile captcha verification."""
        cleaned_data = super().clean()

        # If honeypot caught spam, skip Turnstile external API verification
        if "website" in self.errors:
            return cleaned_data

        token = self.data.get("cf-turnstile-response") or cleaned_data.get("cf_turnstile_response")

        if self.turnstile_service.secret_key:
            if not token or not self.turnstile_service.verify(token, remote_ip=self.remote_ip):
                raise forms.ValidationError(_("Security verification failed. Please try again."))

        return cleaned_data
