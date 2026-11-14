import uuid

from django.core.validators import RegexValidator
from django.db import models

phone_validator = RegexValidator(
    regex=r"^\+?[\d\s().-]{7,20}$",
    message="Enter a valid phone number, e.g. +1 555 123 4567.",
)


class Reservation(models.Model):
    """A reservation/inquiry submitted from a kitten page. This is the single
    source of truth for every lead: nothing is emailed without also being
    persisted here, so the dashboard can report on it."""

    class ContactPreference(models.TextChoices):
        EMAIL = "email", "Email"
        PHONE = "phone", "Phone call or text"

    class MessageChannel(models.TextChoices):
        EMAIL = "email", "Email"
        GOOGLE_VOICE = "sms", "Google Voice text"

    class DeliveryMethod(models.TextChoices):
        UNDECIDED = "undecided", "Not sure yet"
        PICKUP = "pickup", "I will pick up"
        GROUND = "ground", "Ground delivery"
        FLIGHT_NANNY = "flight_nanny", "Flight nanny"

    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        DEPOSIT_RECEIVED = "deposit_received", "Deposit received"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission_key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    kitten = models.ForeignKey("kittens.Kitten", on_delete=models.CASCADE, related_name="reservations")

    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=24, validators=[phone_validator], blank=True)
    contact_preference = models.CharField(max_length=10, choices=ContactPreference.choices, default=ContactPreference.EMAIL)
    message_channel = models.CharField(
        "Send reservation details via",
        max_length=10,
        choices=MessageChannel.choices,
        default=MessageChannel.EMAIL,
    )

    shipping_city = models.CharField("City", max_length=100)
    shipping_state = models.CharField("State / region", max_length=40)
    delivery_method = models.CharField(max_length=14, choices=DeliveryMethod.choices, default=DeliveryMethod.UNDECIDED)
    has_other_pets = models.BooleanField("Other pets at home", default=False)
    message = models.TextField(blank=True, max_length=1000)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    admin_notes = models.TextField(blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status"]), models.Index(fields=["created_at"])]

    def __str__(self):
        return f"{self.full_name} -> {self.kitten.name} ({self.status})"

    def contact_target(self):
        return self.phone if self.contact_preference == self.ContactPreference.PHONE else self.email
