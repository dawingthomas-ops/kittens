from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView
from django.views.static import serve as serve_media
from rest_framework.routers import DefaultRouter

from core.sitemaps import JournalSitemap, KittenSitemap, LandingPageSitemap, StaticViewSitemap
from kittens.api_views import KittenViewSet
from reservations.api_views import ReservationCreateAPIView
from reviews.api_views import TestimonialCreateAPIView, TestimonialListAPIView

router = DefaultRouter()
router.register("kittens", KittenViewSet, basename="kitten")

sitemaps = {
    "pages": StaticViewSitemap,
    "kittens": KittenSitemap,
    "landing": LandingPageSitemap,
    "journal": JournalSitemap,
}

handler404 = "core.views.not_found"
handler500 = "core.views.server_error"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", include("dashboard.urls")),
    path("accounts/", include("accounts.urls")),

    path("api/", include(router.urls)),
    path("api/reservations/", ReservationCreateAPIView.as_view(), name="api-reservation-create"),
    path("api/testimonials/", TestimonialListAPIView.as_view(), name="api-testimonial-list"),
    path("api/testimonials/submit/", TestimonialCreateAPIView.as_view(), name="api-testimonial-create"),

    path("sitemap.xml", sitemap, {"sitemaps": sitemaps, "template_name": "sitemap.xml"}, name="django.contrib.sitemaps.views.sitemap"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path("site.webmanifest", TemplateView.as_view(template_name="site.webmanifest", content_type="application/manifest+json")),
    path("favicon.ico", RedirectView.as_view(url="/static/img/favicon.svg", permanent=True)),

    path("", include("core.urls")),
    path("", include("kittens.urls")),
    path("", include("reservations.urls")),
    path("", include("reviews.urls")),
]

if settings.SERVE_LOCAL_MEDIA and not settings.USE_S3:
    urlpatterns += [
        path("media/<path:path>", serve_media, {"document_root": settings.MEDIA_ROOT}),
    ]
