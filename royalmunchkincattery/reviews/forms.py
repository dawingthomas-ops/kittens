from django import forms

from core.forms import HoneypotMixin
from kittens.models import Kitten
from .models import Testimonial

MAX_PHOTO_MB = 5


class TestimonialForm(HoneypotMixin, forms.ModelForm):
    confirm_customer = forms.BooleanField(
        required=True,
        label="I confirm this review is about my own experience as a customer.",
    )

    class Meta:
        model = Testimonial
        fields = ["kitten", "author_name", "author_city_state", "rating", "body", "photo"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 5, "maxlength": 1200}),
            "photo": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_honeypot()
        self.fields["kitten"].queryset = Kitten.objects.all().order_by("name")
        self.fields["kitten"].required = False
        self.fields["kitten"].empty_label = "Not sure / skip"

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo and hasattr(photo, "size") and photo.size > MAX_PHOTO_MB * 1024 * 1024:
            raise forms.ValidationError(f"Please upload a photo under {MAX_PHOTO_MB} MB.")
        return photo


class TestimonialAdminForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ["is_approved"]
