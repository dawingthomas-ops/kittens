from rest_framework import serializers

from kittens.models import Kitten
from .models import Reservation


class ReservationCreateSerializer(serializers.ModelSerializer):
    kitten_slug = serializers.SlugRelatedField(
        source="kitten", slug_field="slug", queryset=Kitten.objects.exclude(status=Kitten.Status.ADOPTED)
    )

    class Meta:
        model = Reservation
        fields = [
            "id", "kitten_slug", "full_name", "email", "phone", "contact_preference", "shipping_city",
            "shipping_state", "delivery_method", "has_other_pets", "message",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        if attrs.get("contact_preference") == Reservation.ContactPreference.PHONE and not attrs.get("phone"):
            raise serializers.ValidationError(
                {"phone": "Phone number is required when phone is the preferred contact method."}
            )
        return attrs
