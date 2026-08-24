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
