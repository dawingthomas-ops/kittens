from django.db import models


class PageView(models.Model):
    """Lightweight first-party analytics event. Powers the dashboard charts
    without shipping visitor data to a third party."""

    path = models.CharField(max_length=255)
    kitten = models.ForeignKey("kittens.Kitten", on_delete=models.SET_NULL, null=True, blank=True, related_name="page_views")
    referrer = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["created_at"]), models.Index(fields=["path"])]
