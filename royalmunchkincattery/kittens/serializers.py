from rest_framework import serializers

from .models import Kitten, KittenImage


class KittenImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = KittenImage
        fields = ["id", "image", "caption", "ordering"]


class KittenListSerializer(serializers.ModelSerializer):
    """Compact representation used for search results / cards."""

    gender_display = serializers.CharField(source="get_gender_display", read_only=True)
    coat_length_display = serializers.CharField(source="get_coat_length_display", read_only=True)
    leg_length_display = serializers.CharField(source="get_leg_length_display", read_only=True)
    coat_color_display = serializers.CharField(source="get_coat_color_display", read_only=True)
    pattern_display = serializers.CharField(source="get_pattern_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    look = serializers.CharField(read_only=True)
    readiness = serializers.CharField(source="readiness_label", read_only=True)

    class Meta:
        model = Kitten
        fields = [
            "id", "name", "slug", "url", "gender", "gender_display", "coat_length", "coat_length_display",
            "leg_length", "leg_length_display", "coat_color", "coat_color_display", "pattern", "pattern_display",
            "look", "status", "status_display", "price", "headline", "cover_photo", "age_weeks", "readiness",
            "energy", "is_featured", "nationwide_delivery_available",
        ]


class KittenDetailSerializer(KittenListSerializer):
    gallery_images = KittenImageSerializer(many=True, read_only=True)

    class Meta(KittenListSerializer.Meta):
        fields = KittenListSerializer.Meta.fields + [
            "description", "deposit_amount", "weight_estimate_lb", "vet_checked", "vaccinations_up_to_date",
            "dewormed", "microchipped", "litter_trained", "spay_neuter_agreement", "registry",
            "health_guarantee_years", "care_info_confirmed", "delivery_notes", "gallery_images", "date_of_birth", "good_with_kids",
            "good_with_pets",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not instance.care_info_confirmed:
            for field in (
                "vet_checked", "vaccinations_up_to_date", "dewormed", "microchipped", "litter_trained",
                "spay_neuter_agreement", "health_guarantee_years", "good_with_kids", "good_with_pets",
            ):
                data[field] = None
        return data
