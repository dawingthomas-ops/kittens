import json
import re
import uuid
from datetime import timedelta
from decimal import Decimal
from html import unescape
from io import BytesIO
from urllib.parse import parse_qs, urlsplit

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core import mail
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from core.models import ContactMessage, Post, SiteSettings, WaitlistEntry
from kittens.matching import best_matches, score_kitten
from kittens.models import Kitten, Litter
from kittens.serializers import KittenDetailSerializer
from reservations.models import Reservation
from reviews.models import Testimonial


def make_image(name="k.jpg"):
    buf = BytesIO()
    Image.new("RGB", (40, 50), (200, 120, 60)).save(buf, "JPEG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/jpeg")


def make_kitten(name="Luna", price=900, **kw):
    defaults = dict(
        name=name, gender="female", coat_length="longhair", coat_color="red", pattern="tabby",
        date_of_birth=timezone.localdate() - timedelta(weeks=9), price=price, headline="Sweet",
        description="A sweet kitten.", cover_photo=make_image(), energy="calm",
    )
    defaults.update(kw)
    k = Kitten(**defaults)
    k.full_clean()
    k.save()
    return k


@override_settings(ALLOWED_HOSTS=["testserver"])
class PriceRuleTests(TestCase):
    def test_price_inside_range_ok(self):
        for p in (800, 900, 1000):
            make_kitten(name=f"K{p}", price=p)

    def test_price_outside_range_rejected_by_validator(self):
        for p in (799.99, 1000.01, 500, 2500):
            k = Kitten(name="X", gender="male", coat_color="black", date_of_birth=timezone.localdate(),
                       price=Decimal(str(p)), headline="h", description="d", cover_photo=make_image())
            with self.assertRaises(ValidationError):
                k.full_clean()

    def test_database_constraint_blocks_bad_price_even_without_validation(self):
        k = make_kitten()
        with self.assertRaises(IntegrityError), transaction.atomic():
            Kitten.objects.filter(pk=k.pk).update(price=1500)

    def test_slug_is_unique_and_seo_friendly(self):
        a, b = make_kitten("Luna"), make_kitten("Luna")
        self.assertNotEqual(a.slug, b.slug)
        self.assertIn("munchkin-kitten", a.slug)


@override_settings(ALLOWED_HOSTS=["testserver"])
class PublicPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.kitten = make_kitten()
        cls.adopted = make_kitten("Gone", status="adopted")
        Post.objects.create(title="Hello Post", content="<p>Body</p>", excerpt="e")

    def test_core_pages_render(self):
        from core.landing_pages import LANDING_PAGES
        urls = ["/", "/kittens/", "/kitten-match/", "/favorites/", "/about/", "/faq/", "/delivery/", "/contact/", "/waitlist/",
                "/munchkin-cat-breed-guide/", "/journal/", "/privacy/", "/terms/", "/reviews/", "/reviews/submit/", "/accounts/login/"]
        urls += [f"/{s}/" for s in LANDING_PAGES]
        for u in urls:
            self.assertEqual(self.client.get(u).status_code, 200, u)

    def test_footer_has_small_admin_login_section(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<div class="footer-admin">', html=False)
        self.assertContains(response, 'href="/accounts/login/" rel="nofollow">Admin sign in</a>', html=False)

    def test_new_brand_is_used_in_site_and_app_manifest(self):
        response = self.client.get("/")
        self.assertContains(response, "American Munchkin House")
        self.assertContains(response, f'href="https://{settings.SITE_DOMAIN}/"')

        manifest = self.client.get("/site.webmanifest")
        self.assertContains(manifest, '"name": "American Munchkin House"')
        self.assertContains(manifest, '"short_name": "Munchkin House"')

    def test_google_voice_and_email_are_public_contact_methods(self):
        self.assertEqual(settings.ADMIN_NOTIFICATION_EMAIL, "dawingthomas@gmail.com")
        site_settings = SiteSettings.load()
        site_settings.contact_email = "dawingthomas@gmail.com"
        site_settings.contact_phone = "+1 (720) 819-6325"
        site_settings.save()

        footer = self.client.get("/")
        self.assertContains(footer, "mailto:dawingthomas@gmail.com")
        self.assertContains(footer, "tel:+17208196325")
        self.assertContains(footer, "sms:+17208196325")
        contact = self.client.get("/contact/")
        self.assertContains(contact, "dawingthomas@gmail.com")
        self.assertContains(contact, "Google Voice")
        self.assertContains(contact, "sms:+17208196325")

    def test_reviews_page_shows_all_supplied_photos_as_gallery_not_reviews(self):
        response = self.client.get("/reviews/")
        self.assertEqual(response.status_code, 200)
        for index in range(1, 7):
            self.assertContains(response, f"img/reviews/family-{index:02}.jpg")
        self.assertContains(response, "These images are not review quotes")

    def test_404_uses_custom_template_and_is_noindex(self):
        r = self.client.get("/nothing-here/")
        self.assertEqual(r.status_code, 404)
        self.assertContains(r, "noindex", status_code=404)

    def test_unique_titles_and_descriptions_on_landing_pages(self):
        from core.landing_pages import LANDING_PAGES
        titles, descs = set(), set()
        for slug in LANDING_PAGES:
            html = self.client.get(f"/{slug}/").content.decode()
            titles.add(re.search(r"<title>(.*?)</title>", html).group(1))
            descs.add(re.search(r'name="description" content="(.*?)"', html).group(1))
        self.assertEqual(len(titles), len(LANDING_PAGES))
        self.assertEqual(len(descs), len(LANDING_PAGES))

    def test_adopted_kitten_hidden_from_list_but_page_still_resolves(self):
        self.assertNotContains(self.client.get("/kittens/"), "Gone")
        self.assertEqual(self.client.get(self.adopted.get_absolute_url()).status_code, 200)

    def test_unconfirmed_kitten_facts_are_not_presented_as_known(self):
        kitten = make_kitten(
            "Silver",
            gender=Kitten.Gender.UNCONFIRMED,
            leg_length=Kitten.LegLength.UNCONFIRMED,
            energy=Kitten.Energy.UNCONFIRMED,
            date_of_birth=None,
            care_info_confirmed=False,
            vet_checked=False,
            vaccinations_up_to_date=False,
            dewormed=False,
            microchipped=False,
            litter_trained=False,
            good_with_kids=False,
            good_with_pets=False,
        )
        self.assertIsNone(kitten.age_weeks)
        self.assertIsNone(kitten.go_home_date)
        self.assertEqual(kitten.readiness_label, "Go-home timing to be confirmed")

        response = self.client.get(kitten.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Age to be confirmed")
        self.assertContains(response, "Go-home timing to be confirmed")
        self.assertContains(response, "Health, care, and household-suitability details")
        self.assertNotContains(response, "Vet-checked")
        self.assertNotContains(response, "Good with children")
        serialized = KittenDetailSerializer(kitten).data
        self.assertIsNone(serialized["vet_checked"])
        self.assertIsNone(serialized["good_with_kids"])

    def ld_blocks(self, url):
        html = self.client.get(url).content.decode()
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        return [json.loads(b) for b in blocks]  # raises if any block is invalid JSON

    def test_every_jsonld_block_is_valid_json_on_every_page_type(self):
        from core.landing_pages import LANDING_PAGES
        urls = ["/", "/kittens/", "/faq/", "/contact/", "/munchkin-cat-breed-guide/", "/reviews/",
                self.kitten.get_absolute_url(), "/journal/hello-post/"] + [f"/{s}/" for s in LANDING_PAGES]
        for u in urls:
            self.assertGreaterEqual(len(self.ld_blocks(u)), 0, u)
        home = self.ld_blocks("/")
        types = {n["@type"] for b in home if "@graph" in b for n in b["@graph"]} | {b.get("@type") for b in home}
        self.assertTrue({"Organization", "WebSite", "PetStore", "FAQPage"} <= types)

    def test_detail_schema_has_product_offer_and_no_empty_rating(self):
        product = next(b for b in self.ld_blocks(self.kitten.get_absolute_url()) if b.get("@type") == "Product")
        self.assertEqual(product["offers"]["price"], "900.00")
        self.assertEqual(product["offers"]["priceCurrency"], "USD")
        self.assertNotIn("aggregateRating", product)  # never emit a 0-review rating
        crumbs = next(b for b in self.ld_blocks(self.kitten.get_absolute_url()) if b.get("@type") == "BreadcrumbList")
        self.assertEqual(len(crumbs["itemListElement"]), 3)

    def test_filters_work_and_price_cap_enforced(self):
        make_kitten("Tom", gender="male", coat_length="shorthair", price=850)
        r = self.client.get("/kittens/?gender=male")
        self.assertContains(r, "Tom"); self.assertNotContains(r, "Luna")
        r = self.client.get("/kittens/?max_price=850")
        self.assertContains(r, "Tom"); self.assertNotContains(r, "Luna")

    def test_fetch_header_returns_partial_only(self):
        r = self.client.get("/kittens/", HTTP_X_REQUESTED_WITH="fetch")
        self.assertNotContains(r, "<html")
        self.assertContains(r, "kitten-grid")

    def test_filtered_listing_is_noindex_with_clean_canonical(self):
        html = self.client.get("/kittens/?gender=female").content.decode()
        self.assertIn("noindex", html)
        self.assertIn('rel="canonical" href="https://americanmunchkinhouse.com/kittens/"', html)

    def test_sitemap_and_robots(self):
        sm = self.client.get("/sitemap.xml").content.decode()
        self.assertIn(self.kitten.slug, sm)
        self.assertNotIn(self.adopted.slug, sm)
        self.assertIn("image:image", sm)
        self.assertIn("munchkin-kittens-for-sale", sm)
        self.assertIn("hello-post", sm)
        robots = self.client.get("/robots.txt").content.decode()
        self.assertIn("Sitemap: https://americanmunchkinhouse.com/sitemap.xml", robots)
        self.assertIn("Disallow: /dashboard/", robots)

    def test_match_quiz_scores_and_ranks(self):
        calm = make_kitten("Calmy", energy="calm", coat_length="longhair", price=800)
        wild = make_kitten("Wildy", energy="adventurous", coat_length="shorthair", price=1000)
        res = best_matches(Kitten.objects.filter(pk__in=[calm.pk, wild.pk]),
                           {"coat": "longhair", "energy": "calm", "budget": Decimal(900)})
        self.assertEqual(res[0]["kitten"], calm)
        self.assertGreater(res[0]["percent"], res[1]["percent"])
        r = self.client.get("/kitten-match/?go=1&coat=longhair&energy=calm&budget=999999")
        self.assertContains(r, "% match")  # out-of-range budget is clamped, not a crash
        self.assertEqual(self.client.get("/kitten-match/?go=1&budget=abc").status_code, 200)

    def test_match_does_not_treat_unconfirmed_traits_as_mismatches(self):
        kitten = make_kitten(
            "Mystery",
            gender=Kitten.Gender.UNCONFIRMED,
            energy=Kitten.Energy.UNCONFIRMED,
            date_of_birth=None,
            care_info_confirmed=False,
            good_with_kids=False,
            good_with_pets=False,
        )
        _, reasons = score_kitten(
            kitten,
            {"energy": "playful", "kids": "yes", "pets": "yes", "gender": "female"},
        )
        self.assertNotIn("personality", " ".join(reasons))
        self.assertNotIn("gender", " ".join(reasons))
        self.assertNotIn("children", " ".join(reasons))
        self.assertNotIn("other pets", " ".join(reasons))

    def test_visit_counts_views_but_not_bots(self):
        self.client.get(self.kitten.get_absolute_url())
        self.client.get(self.kitten.get_absolute_url(), HTTP_USER_AGENT="Googlebot/2.1")
        self.kitten.refresh_from_db()
        self.assertEqual(self.kitten.view_count, 1)


@override_settings(ALLOWED_HOSTS=["testserver"], ADMIN_NOTIFICATION_EMAIL="owner@example.com",
                   EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class FormFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.kitten = make_kitten()

    def setUp(self):
        cache.clear()

    def reserve_payload(self, **kw):
        data = dict(full_name="Ann Buyer", email="ann@example.com", phone="", contact_preference="email",
                    message_channel="email", shipping_city="Austin", shipping_state="TX", delivery_method="ground",
                    message="Hi", website="", submission_key=str(uuid.uuid4()))
        data.update(kw)
        return data

    def test_reservation_saves_and_emails_admin_and_customer(self):
        r = self.client.post(f"/reserve/{self.kitten.slug}/", self.reserve_payload())
        reservation = Reservation.objects.get()
        self.assertRedirects(
            r,
            f"/reserve/{self.kitten.slug}/thank-you/{reservation.pk}/",
        )
        self.assertEqual(Reservation.objects.count(), 1)
        self.assertEqual(reservation.message_channel, Reservation.MessageChannel.EMAIL)
        self.assertEqual(mail.outbox[0].to, ["owner@example.com"])
        self.assertEqual(mail.outbox[0].reply_to, ["ann@example.com"])
        self.assertEqual(mail.outbox[1].to, ["ann@example.com"])
        self.assertIn("Thank you for your interest", mail.outbox[1].body)

    def test_email_reservation_does_not_offer_a_second_manual_email(self):
        response = self.client.post(
            f"/reserve/{self.kitten.slug}/",
            self.reserve_payload(message="Please tell me about Luna."),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No need to send a second email")
        self.assertNotContains(response, "mail.google.com")

    def test_duplicate_reservation_submission_sends_no_duplicate_emails(self):
        payload = self.reserve_payload()
        first = self.client.post(f"/reserve/{self.kitten.slug}/", payload)
        second = self.client.post(f"/reserve/{self.kitten.slug}/", payload)
        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 302)
        self.assertEqual(Reservation.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 2)

    def test_google_voice_choice_opens_prefilled_text_to_business_number(self):
        response = self.client.post(
            f"/reserve/{self.kitten.slug}/",
            self.reserve_payload(message_channel="sms", message="Could you send a video?"),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Open prefilled text to our Google Voice number")
        self.assertEqual(Reservation.objects.get().message_channel, Reservation.MessageChannel.GOOGLE_VOICE)
        page = unescape(response.content.decode())
        sms_href = re.search(r'href="(sms:[^\"]+)"', page).group(1)
        self.assertEqual(urlsplit(sms_href).path, "+17208196325")
        body = parse_qs(urlsplit(sms_href).query)["body"][0]
        self.assertIn("Kitten: Luna", body)
        self.assertIn("Could you send a video?", body)
        self.assertIn(self.kitten.get_absolute_url(), body)

    def test_invalid_message_channel_does_not_create_reservation(self):
        response = self.client.post(
            f"/reserve/{self.kitten.slug}/",
            self.reserve_payload(message_channel="carrier-pigeon"),
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(Reservation.objects.count(), 0)

    def test_phone_required_when_phone_preferred(self):
        r = self.client.post(f"/reserve/{self.kitten.slug}/", self.reserve_payload(contact_preference="phone"))
        self.assertEqual(r.status_code, 422)
        self.assertEqual(Reservation.objects.count(), 0)

    def test_honeypot_silently_drops_spam(self):
        r = self.client.post(f"/reserve/{self.kitten.slug}/", self.reserve_payload(website="http://spam"))
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Reservation.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_smtp_failure_never_loses_the_lead_or_500s(self):
        with override_settings(EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend", EMAIL_HOST="127.0.0.1", EMAIL_PORT=1, EMAIL_TIMEOUT=1):
            r = self.client.post(f"/reserve/{self.kitten.slug}/", self.reserve_payload())
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Reservation.objects.count(), 1)

    def test_cannot_reserve_adopted_kitten(self):
        k = make_kitten("Done", status="adopted")
        self.assertEqual(self.client.post(f"/reserve/{k.slug}/", self.reserve_payload()).status_code, 404)

    def test_contact_and_waitlist_persist_and_notify(self):
        contact_payload = dict(
            name="Bo",
            email="bo@example.com",
            phone="",
            subject="Q",
            message="Hello?",
            website="",
            submission_key=str(uuid.uuid4()),
        )
        r = self.client.post("/contact/", contact_payload)
        self.assertRedirects(r, "/contact/thank-you/")
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertEqual(mail.outbox[0].to, ["owner@example.com"])
        self.assertEqual(mail.outbox[1].to, ["bo@example.com"])
        self.assertIn("We received your message", mail.outbox[1].body)
        duplicate = self.client.post("/contact/", contact_payload)
        self.assertRedirects(duplicate, "/contact/thank-you/")
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 2)

        r = self.client.post("/waitlist/", dict(name="Cy", email="cy@example.com", phone="", preferred_gender="female",
                                                preferred_coat_length="longhair", preferred_colors="calico", notes="", website=""))
        self.assertRedirects(r, "/waitlist/thank-you/")
        self.assertEqual(WaitlistEntry.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 4)  # contact admin/confirmation, waitlist admin/confirmation

    def test_same_admin_and_customer_address_receives_one_combined_reservation_email(self):
        response = self.client.post(
            f"/reserve/{self.kitten.slug}/",
            self.reserve_payload(email="owner@example.com"),
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["owner@example.com"])
        self.assertIn("Thank you for your interest", mail.outbox[0].body)
        self.assertIn("New reservation inquiry", mail.outbox[0].body)

    def test_same_admin_and_customer_address_receives_one_combined_contact_email(self):
        response = self.client.post(
            "/contact/",
            {
                "name": "Bo",
                "email": "owner@example.com",
                "phone": "",
                "subject": "Question",
                "message": "Hello?",
                "website": "",
                "submission_key": str(uuid.uuid4()),
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["owner@example.com"])
        self.assertIn("We received your message", mail.outbox[0].body)
        self.assertIn("New contact message", mail.outbox[0].body)

    def test_rate_limit_blocks_bursts(self):
        codes = [self.client.post("/contact/", dict(name="", email="x", message="")).status_code for _ in range(12)]
        self.assertIn(429, codes)

    def test_rate_limit_ignores_spoofed_left_forwarded_ip(self):
        for i in range(12):
            r = self.client.post("/waitlist/", dict(name="", email="x"), HTTP_X_FORWARDED_FOR=f"9.9.9.{i}, 1.2.3.4")
        self.assertEqual(r.status_code, 429)  # same real (right-most) IP, so the limit still applies


@override_settings(ALLOWED_HOSTS=["testserver"])
class ReviewModerationTests(TestCase):
    def test_submission_is_unapproved_and_hidden_everywhere(self):
        k = make_kitten()
        r = self.client.post("/reviews/submit/", dict(author_name="Dee", author_city_state="Reno, NV", rating=5,
                                                      body="Wonderful!", kitten=k.pk, website="",
                                                      confirm_customer="on", is_approved="true"))
        self.assertEqual(r.status_code, 302)
        t = Testimonial.objects.get()
        self.assertFalse(t.is_approved)
        self.assertNotContains(self.client.get("/reviews/"), "Wonderful")
        self.assertNotContains(self.client.get(k.get_absolute_url()), "Wonderful")
        self.assertEqual(self.client.get("/api/testimonials/").json()["results"], [])
        self.assertNotIn("aggregateRating", self.client.get("/reviews/").content.decode())

    def test_submission_requires_customer_confirmation(self):
        response = self.client.post("/reviews/submit/", dict(
            author_name="Dee", rating=5, body="My genuine experience.", website="",
        ))
        self.assertEqual(response.status_code, 422)
        self.assertFalse(Testimonial.objects.exists())

    def test_approved_review_shows_and_adds_rating_schema(self):
        k = make_kitten()
        t = Testimonial.objects.create(author_name="Eve", rating=4, body="Lovely cat", kitten=k)
        t.approve()
        self.assertContains(self.client.get("/reviews/"), "Lovely cat")
        self.assertIn("aggregateRating", self.client.get(k.get_absolute_url()).content.decode())

    def test_api_cannot_publish_a_review_directly(self):
        r = self.client.post("/api/testimonials/submit/", dict(author_name="Mal", rating=5, body="spam", is_approved=True))
        self.assertEqual(r.status_code, 201)
        self.assertFalse(Testimonial.objects.get().is_approved)


@override_settings(ALLOWED_HOSTS=["testserver"])
class DashboardSecurityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.admin = User.objects.create_superuser("admin", "admin@example.com", "admin-password-12345")
        cls.staff = User.objects.create_user("staff", password="x" * 14, is_staff=True)
        cls.visitor = User.objects.create_user("visitor", password="x" * 14)
        cls.kitten = make_kitten()
        cls.res = Reservation.objects.create(kitten=cls.kitten, full_name="=HYPERLINK(1)", email="a@b.co",
                                             shipping_city="A", shipping_state="TX")
        cls.review = Testimonial.objects.create(author_name="Fay", rating=5, body="Great")
        cls.post = Post.objects.create(
            title="Getting ready for a kitten",
            excerpt="A practical checklist.",
            content="<p>Prepare a calm room.</p>",
            is_published=False,
        )

    def test_anonymous_and_non_staff_are_blocked(self):
        for path in ("/dashboard/", "/dashboard/reservations/", "/dashboard/kittens/", "/dashboard/inbox/", "/dashboard/reservations/export.csv"):
            self.assertEqual(self.client.get(path).status_code, 302, path)
        self.client.force_login(self.visitor)
        self.assertEqual(self.client.get("/dashboard/").status_code, 403)
        response = self.client.post(f"/dashboard/testimonials/{self.review.pk}/approve/")
        self.assertEqual(response.status_code, 403)
        self.review.refresh_from_db()
        self.assertFalse(self.review.is_approved)

    def test_staff_cannot_use_admin_login_or_dashboard(self):
        limited_staff = get_user_model().objects.create_user(
            "limited-staff", "staff@example.com", "test-password-12345", is_staff=True
        )
        response = self.client.post(
            "/accounts/login/",
            {"username": "limited-staff", "password": "test-password-12345"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign-in failed")
        self.client.force_login(limited_staff)
        for path in ("/dashboard/", "/dashboard/kittens/", "/dashboard/posts/", "/dashboard/posts/add/"):
            self.assertEqual(self.client.get(path).status_code, 403, path)
        self.assertEqual(
            self.client.post(
                "/dashboard/posts/add/",
                {"title": "Unauthorized", "content": "<p>Not allowed</p>"},
            ).status_code,
            403,
        )
        self.assertFalse(Post.objects.filter(title="Unauthorized").exists())
        self.assertEqual(self.client.get("/admin/").status_code, 302)
        self.client.logout()
        admin_login = self.client.post(
            "/admin/login/",
            {"username": "limited-staff", "password": "test-password-12345"},
        )
        self.assertEqual(admin_login.status_code, 200)
        self.assertContains(admin_login, "restricted to the site administrator")
        self.client.force_login(limited_staff)
        response = self.client.post(f"/dashboard/testimonials/{self.review.pk}/approve/")
        self.assertEqual(response.status_code, 403)
        self.review.refresh_from_db()
        self.assertFalse(self.review.is_approved)

    def test_admin_can_sign_in(self):
        response = self.client.post(
            "/accounts/login/",
            {"username": "admin", "password": "admin-password-12345"},
        )
        self.assertRedirects(response, "/dashboard/")
        self.assertEqual(self.client.get("/dashboard/").status_code, 200)
        self.assertEqual(self.client.get("/admin/").status_code, 200)

    def test_admin_can_use_every_dashboard_page(self):
        self.client.force_login(self.admin)
        paths = ["/dashboard/", "/dashboard/reservations/", f"/dashboard/reservations/{self.res.pk}/edit/", f"/dashboard/reservations/{self.res.pk}/delete/",
                 "/dashboard/testimonials/", f"/dashboard/testimonials/{self.review.pk}/edit/", "/dashboard/kittens/", "/dashboard/kittens/add/",
                 f"/dashboard/kittens/{self.kitten.pk}/edit/", "/dashboard/posts/", "/dashboard/posts/add/",
                 f"/dashboard/posts/{self.post.pk}/edit/", "/dashboard/inbox/", "/dashboard/api/analytics/"]
        for p in paths:
            self.assertEqual(self.client.get(p).status_code, 200, p)

    def test_state_changes_require_post(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(f"/dashboard/testimonials/{self.review.pk}/approve/").status_code, 405)
        self.assertEqual(self.client.get(f"/dashboard/testimonials/{self.review.pk}/reject/").status_code, 405)
        self.client.post(f"/dashboard/testimonials/{self.review.pk}/approve/")
        self.review.refresh_from_db()
        self.assertTrue(self.review.is_approved)
        self.assertEqual(self.review.approved_by, self.admin)

    def test_status_update_and_csv_injection_guard(self):
        self.client.force_login(self.admin)
        self.client.post(f"/dashboard/reservations/{self.res.pk}/status/", {"status": "confirmed"})
        self.res.refresh_from_db()
        self.assertEqual(self.res.status, "confirmed")
        csv_text = self.client.get("/dashboard/reservations/export.csv").content.decode()
        self.assertIn("'=HYPERLINK(1)", csv_text)

    def test_logout_works_via_post(self):
        self.client.force_login(self.admin)
        self.client.post("/accounts/logout/")
        self.assertEqual(self.client.get("/dashboard/").status_code, 302)

    def test_dashboard_kitten_create_enforces_price_range(self):
        self.client.force_login(self.admin)
        data = dict(name="New", gender="male", date_of_birth="2026-01-01", coat_length="shorthair", leg_length="standard",
                    coat_color="black", pattern="solid", status="available", price="1500", deposit_amount="200",
                    headline="h", description="d", energy="calm", health_guarantee_years=1,
                    delivery_notes="x", **{"kitten_images-TOTAL_FORMS": 0, "kitten_images-INITIAL_FORMS": 0,
                                           "gallery_images-TOTAL_FORMS": 0, "gallery_images-INITIAL_FORMS": 0,
                                           "gallery_images-MIN_NUM_FORMS": 0, "gallery_images-MAX_NUM_FORMS": 10})
        r = self.client.post("/dashboard/kittens/add/", data)
        self.assertEqual(r.status_code, 200)  # re-rendered with errors
        self.assertFalse(Kitten.objects.filter(name="New").exists())

    def test_admin_can_create_update_publish_and_delete_posts(self):
        self.client.force_login(self.admin)
        post_data = {
            "title": "Choosing a kitten carrier",
            "slug": "",
            "category": "Kitten care",
            "excerpt": "A concise guide to safe travel.",
            "meta_description": "How to choose a secure carrier for a kitten.",
            "content": "<p>Choose a secure, well-ventilated carrier.</p>",
            "is_published": "",
            "published_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
        }
        response = self.client.post("/dashboard/posts/add/", post_data)
        self.assertEqual(response.status_code, 302)
        post = Post.objects.get(title="Choosing a kitten carrier")
        self.assertFalse(post.is_published)
        self.assertEqual(self.client.get(post.get_absolute_url()).status_code, 404)

        post_data["is_published"] = "on"
        response = self.client.post(f"/dashboard/posts/{post.pk}/edit/", post_data)
        self.assertEqual(response.status_code, 302)
        post.refresh_from_db()
        self.assertTrue(post.is_published)
        self.assertEqual(self.client.get(post.get_absolute_url()).status_code, 200)

        self.assertEqual(self.client.get(f"/dashboard/posts/{post.pk}/delete/").status_code, 200)
        response = self.client.post(f"/dashboard/posts/{post.pk}/delete/")
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Post.objects.filter(pk=post.pk).exists())


@override_settings(ALLOWED_HOSTS=["testserver"])
class ApiTests(TestCase):
    def test_list_excludes_adopted_and_supports_slug_filter(self):
        a, b = make_kitten("A"), make_kitten("B")
        make_kitten("Gone", status="adopted")
        names = {k["name"] for k in self.client.get("/api/kittens/").json()["results"]}
        self.assertEqual(names, {"A", "B"})
        r = self.client.get(f"/api/kittens/?slugs={a.slug}").json()
        self.assertEqual([k["name"] for k in r["results"]], ["A"])

    def test_api_is_read_only_for_kittens(self):
        self.assertEqual(self.client.post("/api/kittens/", {}).status_code, 405)

    def test_reserved_toasts_only_recent_real_reservations(self):
        k = make_kitten(status="reserved")
        Reservation.objects.create(kitten=k, full_name="x", email="x@y.co", shipping_city="a", shipping_state="TX")
        data = self.client.get("/api/kittens/reserved-toasts/").json()
        self.assertEqual(data["count"], 1)
        Reservation.objects.update(created_at=timezone.now() - timedelta(days=10))
        self.assertEqual(self.client.get("/api/kittens/reserved-toasts/").json()["count"], 0)


@override_settings(ALLOWED_HOSTS=["testserver"])
class SeedCommandTests(TestCase):
    def test_seeds_are_valid_and_in_price_range(self):
        from django.core.management import call_command
        call_command("seed_demo_data", verbosity=0)
        call_command("seed_journal", verbosity=0)
        self.assertEqual(Kitten.objects.count(), 8)
        self.assertTrue(all(800 <= k.price <= 1000 for k in Kitten.objects.all()))
        self.assertEqual(Post.objects.count(), 7)
        self.assertEqual(Testimonial.objects.count(), 0)  # never seed fake reviews
        call_command("seed_demo_data", "--clear", verbosity=0)
        self.assertEqual(Kitten.objects.count(), 0)
