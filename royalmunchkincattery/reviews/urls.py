from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
    path("reviews/", views.TestimonialListView.as_view(), name="list"),
    path("reviews/submit/", views.TestimonialSubmitView.as_view(), name="submit"),
    path("reviews/thank-you/", views.TestimonialThankYouView.as_view(), name="thank_you"),
]
