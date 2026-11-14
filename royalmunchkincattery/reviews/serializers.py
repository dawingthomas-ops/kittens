from rest_framework import serializers

from kittens.models import Kitten
from .models import Testimonial


class TestimonialPublicSerializer(serializers.ModelSerializer):
    """Read-only shape for approved testimonials shown on the site."""

    class Meta:
        model = Testimonial
        fields = ["id", "author_name", "author_city_state", "rating", "body", "photo", "submitted_at"]


class TestimonialCreateSerializer(serializers.ModelSerializer):
    kitten_slug = serializers.SlugRelatedField(
        source="kitten", slug_field="slug", queryset=Kitten.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Testimonial
        fields = ["id", "kitten_slug", "author_name", "author_city_state", "rating", "body", "photo"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        # is_approved defaults to False at the model level: every submission
        # lands in the moderation queue, never live directly.
        return Testimonial.objects.create(**validated_data)
