from rest_framework import generics, permissions

from core.middleware import client_ip
from .emails import notify_reservation_submission
from .serializers import ReservationCreateSerializer


class ReservationCreateAPIView(generics.CreateAPIView):
    """Public endpoint for the reservation form. Persists the lead, emails
    admin at ADMIN_NOTIFICATION_EMAIL, then sends the customer a receipt."""

    serializer_class = ReservationCreateSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        reservation = serializer.save(ip_address=client_ip(self.request))
        notify_reservation_submission(reservation)
        return reservation
