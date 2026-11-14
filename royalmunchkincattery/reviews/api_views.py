from rest_framework import generics, permissions

from .models import Testimonial
from .serializers import TestimonialCreateSerializer, TestimonialPublicSerializer


class TestimonialListAPIView(generics.ListAPIView):
    """Only ever returns admin-approved testimonials: the sole public read
    path, so an unapproved review cannot leak through the API."""

    serializer_class = TestimonialPublicSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Testimonial.objects.filter(is_approved=True).select_related("kitten")


class TestimonialCreateAPIView(generics.CreateAPIView):
    serializer_class = TestimonialCreateSerializer
    permission_classes = [permissions.AllowAny]
