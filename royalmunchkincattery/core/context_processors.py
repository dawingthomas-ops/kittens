import re

from django.conf import settings
from django.db import DatabaseError

from .landing_pages import LANDING_PAGES
from .models import SiteSettings


def site_meta(request):
    """Injects site-wide SEO + business info into every template context."""
    try:
        site_settings = SiteSettings.load()
    except DatabaseError:  # e.g. before the first migration
        site_settings = SiteSettings()

    whatsapp = (site_settings.whatsapp_number or settings.WHATSAPP_NUMBER or "").strip().lstrip("+")
    phone = (site_settings.contact_phone or settings.SITE_PHONE or "").strip()
    phone_uri = re.sub(r"(?<!^)\+", "", re.sub(r"[^\d+]", "", phone))

    return {
        "SITE_NAME": settings.SITE_NAME,
        "SITE_SHORT_NAME": settings.SITE_SHORT_NAME,
        "SITE_DOMAIN": settings.SITE_DOMAIN,
        "SITE_URL": f"https://{settings.SITE_DOMAIN}",
        "GOOGLE_SITE_VERIFICATION": settings.GOOGLE_SITE_VERIFICATION,
        "BING_SITE_VERIFICATION": settings.BING_SITE_VERIFICATION,
        "GA_MEASUREMENT_ID": settings.GA_MEASUREMENT_ID,
        "SITE_DEFAULT_DESCRIPTION": settings.SITE_DEFAULT_DESCRIPTION,
        "SITE_DEFAULT_KEYWORDS": settings.SITE_DEFAULT_KEYWORDS,
        "SITE_LOCATION_SUMMARY": settings.SITE_LOCATION_SUMMARY,
        "SITE_SERVICE_AREAS": settings.SITE_SERVICE_AREAS,
        "TWITTER_HANDLE": settings.TWITTER_HANDLE,
        "MIN_PRICE": settings.KITTEN_MIN_PRICE,
        "MAX_PRICE": settings.KITTEN_MAX_PRICE,
        "CONTACT_PHONE": phone,
        "CONTACT_PHONE_URI": phone_uri,
        "WHATSAPP_NUMBER": whatsapp,
        "site_settings": site_settings,
        "FOOTER_LANDING_LINKS": [(slug, p["nav_label"]) for slug, p in LANDING_PAGES.items()],
    }
