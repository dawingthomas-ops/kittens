import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Testimonial(models.Model):
    """A customer review. Nothing shows on the public site until an admin
    explicitly approves it (is_approved + approved_at/by)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kitten = models.ForeignKey("kittens.Kitten", on_delete=models.SET_NULL, null=True, blank=True, related_name="testimonials")
    reservation = models.OneToOneField(
        "reservations.Reservation", on_delete=models.SET_NULL, null=True, blank=True, related_name="testimonial"
    )

    author_name = models.CharField(max_length=100)
    author_city_state = models.CharField(max_length=100, blank=True, help_text="e.g. 'Denver, CO'")
    rating = models.PositiveSmallIntegerField(choices=[(i, f"{i} star{'s' if i != 1 else ''}") for i in range(1, 6)])
    body = models.TextField(max_length=1200)
    photo = models.ImageField(upload_to="testimonials/", blank=True, null=True)

    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_testimonials"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.author_name}, {self.rating}\u2605 ({'approved' if self.is_approved else 'pending'})"

    def approve(self, user=None):
        self.is_approved = True
        self.approved_at = timezone.now()
        self.approved_by = user
        self.save(update_fields=["is_approved", "approved_at", "approved_by"])
