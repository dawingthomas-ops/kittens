import uuid

from django import forms

from core.forms import HoneypotMixin
from .models import Reservation


class ReservationForm(HoneypotMixin, forms.ModelForm):
    submission_key = forms.UUIDField(widget=forms.HiddenInput, initial=uuid.uuid4)

    class Meta:
        model = Reservation
        fields = [
            "full_name", "email", "phone", "contact_preference", "message_channel", "shipping_city",
            "shipping_state", "delivery_method", "has_other_pets", "message",
        ]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4, "maxlength": 1000}),
            "contact_preference": forms.RadioSelect,
            "message_channel": forms.RadioSelect,
            "delivery_method": forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_honeypot()
        self.fields["full_name"].widget.attrs.update({"autocomplete": "name"})
        self.fields["email"].widget.attrs.update({"autocomplete": "email"})
        self.fields["phone"].widget.attrs.update({"autocomplete": "tel", "inputmode": "tel"})
        self.fields["shipping_city"].widget.attrs.update({"autocomplete": "address-level2"})
        self.fields["shipping_state"].widget.attrs.update({"autocomplete": "address-level1"})

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("contact_preference") == Reservation.ContactPreference.PHONE and not cleaned.get("phone"):
            self.add_error("phone", "Please add a phone number since you chose phone as your preferred contact.")
        return cleaned


class ReservationAdminForm(forms.ModelForm):
    """Used by the staff dashboard, where status and notes are editable."""

    class Meta:
        model = Reservation
        fields = [
            "status", "full_name", "email", "phone", "contact_preference", "shipping_city", "shipping_state",
            "delivery_method", "message", "admin_notes",
        ]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 3}),
            "admin_notes": forms.Textarea(attrs={"rows": 4}),
        }
