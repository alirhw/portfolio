from django.conf import settings
from django.core.cache import cache

DEFAULT_THROTTLE_LIMIT = getattr(settings, "CONTACT_THROTTLE_LIMIT", 3)
DEFAULT_THROTTLE_TIMEOUT = getattr(settings, "CONTACT_THROTTLE_TIMEOUT", 300)  # 5 minutes


def is_rate_limited(
    ip_address: str,
    limit: int = DEFAULT_THROTTLE_LIMIT,
    timeout: int = DEFAULT_THROTTLE_TIMEOUT,
) -> bool:
    """
    Check and enforce contact form submission rate limit for a specific IP address.
    Returns True if the rate limit is exceeded.
    """
    if not ip_address:
        return False

    cache_key = f"contact_throttle_{ip_address}"
    current_count = cache.get(cache_key, 0)

    if current_count >= limit:
        return True

    cache.set(cache_key, current_count + 1, timeout)
    return False
