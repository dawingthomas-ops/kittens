from django.db.models import Max
from django.utils import timezone
from rest_framework import permissions, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import KittenFilter
from .models import Kitten
from .serializers import KittenDetailSerializer, KittenListSerializer


class ReservedKittenToastSerializer(serializers.ModelSerializer):
    reserved_at = serializers.DateTimeField(source="latest_reservation_at", read_only=True)
    image = serializers.SerializerMethodField()
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    toast_message = serializers.SerializerMethodField()

    class Meta:
        model = Kitten
        fields = ["id", "name", "slug", "url", "reserved_at", "image", "toast_message"]

    def get_image(self, obj):
        if not obj.cover_photo:
            return None
        url = obj.cover_photo.url
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request is not None else url

    def get_toast_message(self, obj):
        reserved_at = getattr(obj, "latest_reservation_at", None)
        if not reserved_at:
            return f"{obj.name} was reserved recently."
        minutes = max(0, int((timezone.now() - reserved_at).total_seconds() // 60))
        if minutes < 1:
            return f"{obj.name} was reserved just moments ago."
        if minutes < 60:
            return f"{obj.name} was reserved {minutes} minute{'s' if minutes != 1 else ''} ago."
        hours = max(1, minutes // 60)
        if hours < 24:
            return f"{obj.name} was reserved {hours} hour{'s' if hours != 1 else ''} ago."
        days = max(1, hours // 24)
        return f"{obj.name} was reserved {days} day{'s' if days != 1 else ''} ago."


class KittenViewSet(viewsets.ReadOnlyModelViewSet):
    """Public read-only API for the search UI, favorites and social proof.
    Writes happen only through Django admin / the staff dashboard, never
    through this endpoint, which keeps the attack surface small."""

    queryset = Kitten.objects.all().prefetch_related("gallery_images")
    filterset_class = KittenFilter
    lookup_field = "slug"
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        return KittenDetailSerializer if self.action == "retrieve" else KittenListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "list":
            qs = qs.exclude(status=Kitten.Status.ADOPTED)
        return qs

    @action(detail=False, methods=["get"], url_path="reserved-toasts")
    def reserved_toasts(self, request):
        cutoff = timezone.now() - timezone.timedelta(days=3)
        queryset = (
            Kitten.objects.filter(status=Kitten.Status.RESERVED)
            .annotate(latest_reservation_at=Max("reservations__created_at"))
            .filter(latest_reservation_at__gte=cutoff)
            .order_by("-latest_reservation_at")
        )
        serializer = ReservedKittenToastSerializer(queryset, many=True, context={"request": request})
        return Response({"count": len(serializer.data), "results": serializer.data})
