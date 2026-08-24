"""
Strict and well-defined Content Security Policy (CSP) directives.
"""

CSP_DIRECTIVES = {
    "default-src": ("'self'",),
    # Scripts: only local host scripts and Cloudflare Turnstile challenge widget
    "script-src": (
        "'self'",
        "https://challenges.cloudflare.com",
    ),
    # Styles: local CSS, inline styles for components, and Google Fonts
    "style-src": (
        "'self'",
        "'unsafe-inline'",
        "https://fonts.googleapis.com",
    ),
    # Images: local host, data URIs, and external assets
    "img-src": (
        "'self'",
        "data:",
        "https:",
    ),
    # Fonts: local static files and Google Fonts webfonts
    "font-src": (
        "'self'",
        "https://fonts.gstatic.com",
        "data:",
    ),
    # Network connections and Fetch: local endpoints and Turnstile verification
    "connect-src": (
        "'self'",
        "https://challenges.cloudflare.com",
    ),
    # Frames: Turnstile challenge iframe
    "frame-src": (
        "https://challenges.cloudflare.com",
    ),
    # Clickjacking protection: disallow embedding site in unauthorized frames
    "frame-ancestors": ("'none'",),
    # Restrict form action destinations
    "form-action": ("'self'",),
    # Restrict document base URI
    "base-uri": ("'self'",),
    # Block legacy plugins
    "object-src": ("'none'",),
}


def build_csp_header(directives: dict[str, tuple[str, ...]] = CSP_DIRECTIVES) -> str:
    """
    Convert CSP directives dictionary to standard Content-Security-Policy header string.
    """
    return "; ".join(
        f"{directive} {' '.join(sources)}" for directive, sources in directives.items()
    )
