import uuid

from django import forms
from django.core.validators import RegexValidator

from .models import ContactMessage, WaitlistEntry

phone_validator = RegexValidator(
    regex=r"^\+?[\d\s().-]{7,20}$",
    message="Enter a valid phone number, e.g. +1 555 123 4567.",
)


class HoneypotMixin:
    """A hidden field real visitors never fill in. Bots usually do."""

    honeypot_field = "website"

    def add_honeypot(self):
        self.fields[self.honeypot_field] = forms.CharField(
            required=False,
            label="Leave this field empty",
            widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off", "aria-hidden": "true"}),
        )

    @property
    def is_spam(self):
        return bool(self.cleaned_data.get(self.honeypot_field))


class ContactForm(HoneypotMixin, forms.ModelForm):
    submission_key = forms.UUIDField(widget=forms.HiddenInput, initial=uuid.uuid4)
    phone = forms.CharField(required=False, validators=[phone_validator], max_length=24)

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 5, "maxlength": 2000})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_honeypot()
        self.fields["name"].widget.attrs.update({"autocomplete": "name"})
        self.fields["email"].widget.attrs.update({"autocomplete": "email"})
        self.fields["phone"].widget.attrs.update({"autocomplete": "tel", "inputmode": "tel"})


class WaitlistForm(HoneypotMixin, forms.ModelForm):
    phone = forms.CharField(required=False, validators=[phone_validator], max_length=24)

    class Meta:
        model = WaitlistEntry
        fields = ["name", "email", "phone", "preferred_gender", "preferred_coat_length", "preferred_colors", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3, "maxlength": 1000})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_honeypot()
        self.fields["name"].widget.attrs.update({"autocomplete": "name"})
        self.fields["email"].widget.attrs.update({"autocomplete": "email"})
        self.fields["phone"].widget.attrs.update({"autocomplete": "tel", "inputmode": "tel"})
        self.fields["preferred_colors"].widget.attrs.update({"placeholder": "e.g. calico, black, red tabby"})
