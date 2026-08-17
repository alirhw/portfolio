from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from django.views.generic import FormView

from .forms import ContactForm
from .services.submission import ContactSubmissionService
from .utils import get_client_ip


class ContactFormView(FormView):
    form_class = ContactForm
    http_method_names = ["post"]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["remote_ip"] = get_client_ip(self.request)
        return kwargs

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        client_ip = get_client_ip(self.request)

        ContactSubmissionService.submit_message(
            sender_name=cleaned_data["sender_name"],
            email=cleaned_data["email"],
            message=cleaned_data["message"],
            ip_address=client_ip,
        )

        success_msg = _("Thank you! Your message has been sent successfully.")

        if (
            self.request.headers.get("X-Requested-With") == "XMLHttpRequest"
            or self.request.content_type == "application/json"
        ):
            return JsonResponse({"status": "success", "message": str(success_msg)}, status=200)

        messages.success(self.request, success_msg)
        return redirect(self.request.POST.get("next") or "portfolio:home")

    def form_invalid(self, form):
        if (
            self.request.headers.get("X-Requested-With") == "XMLHttpRequest"
            or self.request.content_type == "application/json"
        ):
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)

        for error_list in form.errors.values():
            for error in error_list:
                messages.error(self.request, error)

        return redirect(self.request.POST.get("next") or "portfolio:home")
