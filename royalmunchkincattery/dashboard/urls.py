from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.OverviewView.as_view(), name="overview"),
    path("reservations/", views.ReservationQueueView.as_view(), name="reservations"),
    path("reservations/export.csv", views.ReservationExportView.as_view(), name="reservations_export"),
    path("reservations/<uuid:pk>/edit/", views.ReservationEditView.as_view(), name="reservation_edit"),
    path("reservations/<uuid:pk>/delete/", views.ReservationDeleteView.as_view(), name="reservation_delete"),
    path("reservations/<uuid:pk>/status/", views.ReservationStatusView.as_view(), name="reservation_status"),
    path("testimonials/", views.TestimonialModerationView.as_view(), name="testimonials"),
    path("testimonials/<uuid:pk>/edit/", views.TestimonialEditView.as_view(), name="review_edit"),
    path("testimonials/<uuid:pk>/delete/", views.TestimonialDeleteView.as_view(), name="review_delete"),
    path("testimonials/<uuid:pk>/approve/", views.TestimonialApproveView.as_view(), name="approve_testimonial"),
    path("testimonials/<uuid:pk>/reject/", views.TestimonialRejectView.as_view(), name="reject_testimonial"),
    path("kittens/", views.KittenListView.as_view(), name="kittens"),
    path("kittens/add/", views.KittenCreateView.as_view(), name="kitten_create"),
    path("kittens/<uuid:pk>/edit/", views.KittenUpdateView.as_view(), name="kitten_update"),
    path("kittens/<uuid:pk>/delete/", views.KittenDeleteView.as_view(), name="kitten_delete"),
    path("posts/", views.PostListView.as_view(), name="posts"),
    path("posts/add/", views.PostCreateView.as_view(), name="post_create"),
    path("posts/<int:pk>/edit/", views.PostUpdateView.as_view(), name="post_update"),
    path("posts/<int:pk>/delete/", views.PostDeleteView.as_view(), name="post_delete"),
    path("inbox/", views.InboxView.as_view(), name="inbox"),
    path("inbox/<str:kind>/<int:pk>/toggle/", views.InboxToggleView.as_view(), name="inbox_toggle"),
    path("api/analytics/", views.AnalyticsJsonView.as_view(), name="analytics_json"),
]
