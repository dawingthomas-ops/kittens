from django.urls import path, re_path

from . import views
from .landing_pages import LANDING_PAGES

app_name = "core"

_landing_slugs = "|".join(LANDING_PAGES.keys())

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("faq/", views.FAQView.as_view(), name="faq"),
    path("delivery/", views.DeliveryView.as_view(), name="delivery"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("contact/thank-you/", views.ThanksView.as_view(
        title="Message sent",
        message="Thank you for reaching out. A confirmation was emailed to you from Royal Munchkin Cattery, and our team will reply within one business day. If you do not see the confirmation, check your spam folder."), name="contact_thanks"),
    path("waitlist/", views.WaitlistView.as_view(), name="waitlist"),
    path("waitlist/thank-you/", views.ThanksView.as_view(
        title="You're on the waitlist",
        message="We saved your preferences and will email you first when a matching kitten is on the way."), name="waitlist_thanks"),
    path("munchkin-cat-breed-guide/", views.BreedGuideView.as_view(), name="breed_guide"),
    path("journal/", views.JournalListView.as_view(), name="journal_list"),
    path("journal/<slug:slug>/", views.JournalDetailView.as_view(), name="journal_detail"),
    path("privacy/", views.PrivacyView.as_view(), name="privacy"),
    path("terms/", views.TermsView.as_view(), name="terms"),
    re_path(rf"^(?P<slug>{_landing_slugs})/$", views.LandingPageView.as_view(), name="landing"),
]
