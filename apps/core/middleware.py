from django.conf import settings

from .csp import build_csp_header


class SecurityHeadersMiddleware:
    """
    Append supplementary security headers not configured by default in Django SecurityMiddleware.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Prevent unauthorized access to sensitive client hardware features
        response["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
        response["Cross-Origin-Opener-Policy"] = "same-origin"

        return response


class ContentSecurityPolicyMiddleware:
    """
    Inject Content-Security-Policy header and frontend defenses into HTTP responses.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.csp_header_value = build_csp_header()

    def __call__(self, request):
        response = self.get_response(request)

        # Enable CSP header across environments unless explicitly disabled
        if getattr(settings, "CSP_ENABLED", True):
            response["Content-Security-Policy"] = self.csp_header_value

        return response
