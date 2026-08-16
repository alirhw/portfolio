from django.http import HttpRequest


def get_client_ip(request: HttpRequest) -> str:
    """
    Extract client IP address safely from HTTP request headers.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR", "")
    return ip
