from django import template
from django.conf import settings

register = template.Library()


@register.filter
def absolute_url(value):
    """Turn '/media/x.jpg' into 'https://domain/media/x.jpg' (S3 URLs pass through)."""
    value = str(value or "")
    if value.startswith(("http://", "https://")):
        return value
    return f"https://{settings.SITE_DOMAIN}{value}"


@register.filter
def split_lines(value):
    """Split a text block into paragraphs on blank lines."""
    return [p.strip() for p in str(value or "").replace("\r", "").split("\n\n") if p.strip()]
