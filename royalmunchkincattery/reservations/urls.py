from django.urls import path

from . import views

app_name = "reservations"

urlpatterns = [
    path("reserve/<slug:kitten_slug>/", views.ReservationFormView.as_view(), name="create"),
    path("reserve/<slug:kitten_slug>/thank-you/", views.ReservationThankYouView.as_view(), name="thank_you"),
    path(
        "reserve/<slug:kitten_slug>/thank-you/<uuid:reservation_id>/",
        views.ReservationThankYouView.as_view(),
        name="thank_you_details",
    ),
]
