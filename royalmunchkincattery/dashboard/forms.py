from django import forms
from django.forms import ModelForm
from django.forms.models import inlineformset_factory

from core.models import Post
from kittens.models import Kitten, KittenImage


class KittenForm(ModelForm):
    class Meta:
        model = Kitten
        fields = [
            "name", "litter", "gender", "date_of_birth", "available_from", "coat_length", "leg_length",
            "coat_color", "pattern", "eye_color", "weight_estimate_lb", "status", "price", "deposit_amount",
            "headline", "description", "energy", "personality_tags", "good_with_kids", "good_with_pets",
            "vet_checked", "vaccinations_up_to_date", "dewormed", "microchipped", "litter_trained",
            "spay_neuter_agreement", "care_info_confirmed", "registry", "health_guarantee_years", "cover_photo", "cover_alt",
            "video_url", "nationwide_delivery_available", "delivery_notes", "is_featured",
        ]


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = [
            "title", "slug", "category", "excerpt", "meta_description", "content",
            "featured_image", "is_published", "published_at",
        ]
        widgets = {
            "excerpt": forms.Textarea(attrs={"rows": 3}),
            "meta_description": forms.Textarea(attrs={"rows": 2}),
            "content": forms.Textarea(attrs={"rows": 18, "spellcheck": "true"}),
            "published_at": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={"type": "datetime-local"},
            ),
        }


KittenImageFormSet = inlineformset_factory(
    Kitten, KittenImage, fields=("image", "caption", "ordering"), extra=3, can_delete=True, max_num=10
)
