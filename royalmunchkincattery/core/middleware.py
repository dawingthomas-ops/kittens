from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse


class HttpResponseTooManyRequests(HttpResponse):
    status_code = 429


def client_ip(request):
    """Best-effort client IP behind `TRUSTED_PROXY_COUNT` reverse proxies.

    X-Forwarded-For is client-controllable on its left side, so we count from
    the right (the entries appended by *our* proxies) instead of trusting the
    first value."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        parts = [p.strip() for p in forwarded.split(",") if p.strip()]
        count = max(1, getattr(settings, "TRUSTED_PROXY_COUNT", 1))
        if parts:
            return parts[-count] if len(parts) >= count else parts[0]
    return request.META.get("REMOTE_ADDR", "unknown")


class RateLimitFormsMiddleware:
    """A minimal, dependency-free rate limiter for the POST endpoints most
    likely to be abused by bots: reservations, reviews, contact and waitlist.
    A defense-in-depth layer, not a replacement for a real WAF."""

    LIMITED_PATHS = (
        "/reserve/",
        "/contact/",
        "/waitlist/",
        "/reviews/submit/",
        "/api/reservations/",
        "/api/testimonials/",
        "/accounts/login/",
    )
    MAX_REQUESTS = 8
    WINDOW_SECONDS = 60

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "POST" and any(request.path.startswith(p) for p in self.LIMITED_PATHS):
            ip = client_ip(request)
            key = f"ratelimit:{ip}:{request.path.strip('/').split('/')[0]}"
            count = cache.get(key, 0)
            if count >= self.MAX_REQUESTS:
                return HttpResponseTooManyRequests("Too many requests. Please try again in a minute.")
            cache.set(key, count + 1, timeout=self.WINDOW_SECONDS)
        return self.get_response(request)
