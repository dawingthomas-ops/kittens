import re
from urllib.parse import quote, urlencode

from django.conf import settings
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from core.middleware import client_ip
from core.models import SiteSettings
from kittens.models import Kitten
from .emails import notify_reservation_submission
from .forms import ReservationForm
from .models import Reservation


class ReservationFormView(View):
    """Server-rendered reservation form, progressively enhanced by JS for the
    animated stepper. Works fully without JavaScript."""

    template_name = "reservations/form.html"

    def _kitten(self, slug):
        return get_object_or_404(Kitten.objects.exclude(status=Kitten.Status.ADOPTED), slug=slug)

    def _context(self, kitten, form):
        return {
            "kitten": kitten,
            "form": form,
            "breadcrumbs": [("Home", "/"), ("Kittens", "/kittens/"), (kitten.name, kitten.get_absolute_url()), ("Reserve", "")],
        }

    def get(self, request, kitten_slug):
        kitten = self._kitten(kitten_slug)
        return render(request, self.template_name, self._context(kitten, ReservationForm()))

    def post(self, request, kitten_slug):
        kitten = self._kitten(kitten_slug)
        form = ReservationForm(request.POST)
        if form.is_valid():
            if form.is_spam:  # honeypot tripped: pretend success, save nothing
                return redirect(reverse("reservations:thank_you", kwargs={"kitten_slug": kitten.slug}))
            reservation = form.save(commit=False)
            reservation.submission_key = form.cleaned_data["submission_key"]
            reservation.kitten = kitten
            reservation.ip_address = client_ip(request)
            try:
                with transaction.atomic():
                    reservation.save()
            except IntegrityError:
                existing = Reservation.objects.filter(submission_key=reservation.submission_key).select_related("kitten").first()
                if existing is None:
                    raise
                return redirect(
                    reverse(
                        "reservations:thank_you_details",
                        kwargs={"kitten_slug": existing.kitten.slug, "reservation_id": existing.pk},
                    )
                )
            notify_reservation_submission(reservation)
            return redirect(
                reverse(
                    "reservations:thank_you_details",
                    kwargs={"kitten_slug": kitten.slug, "reservation_id": reservation.pk},
                )
            )
        return render(request, self.template_name, self._context(kitten, form), status=422)


class ReservationThankYouView(View):
    def get(self, request, kitten_slug, reservation_id=None):
        kitten = get_object_or_404(Kitten, slug=kitten_slug)
        context = {"kitten": kitten}
        if reservation_id:
            reservation = get_object_or_404(
                Reservation.objects.select_related("kitten"),
                pk=reservation_id,
                kitten=kitten,
            )
            site_settings = SiteSettings.load()
            email_to = site_settings.contact_email or settings.ADMIN_NOTIFICATION_EMAIL
            phone_digits = re.sub(r"\D", "", site_settings.contact_phone or settings.SITE_PHONE)
            phone_to = f"+{phone_digits}" if phone_digits else ""
            subject = f"Reservation inquiry: {kitten.name}"
            kitten_url = request.build_absolute_uri(kitten.get_absolute_url())
            body = "\n".join(
                [
                    f"Hello American Munchkin House,",
                    "",
                    f"I'd like to reserve or ask a question about {kitten.name}.",
                    "",
                    f"Kitten: {kitten.name}",
                    f"Profile: {kitten.listing_title}",
                    f"Price: ${kitten.price:,.0f}",
                    f"Kitten profile link: {kitten_url}",
                    "",
                    f"Name: {reservation.full_name}",
                    f"Email: {reservation.email}",
                    f"Phone: {reservation.phone or 'Not provided'}",
                    f"Location: {reservation.shipping_city}, {reservation.shipping_state}",
                    f"Preferred delivery: {reservation.get_delivery_method_display()}",
                    f"Other pets at home: {'Yes' if reservation.has_other_pets else 'No'}",
                    "",
                    "My message:",
                    reservation.message or "Please contact me with more information.",
                    "",
                    f"Reservation reference: {reservation.pk}",
                ]
            )
            email_params = urlencode({"view": "cm", "fs": "1", "to": email_to, "su": subject, "body": body})
            context.update(
                {
                    "reservation": reservation,
                    "gmail_compose_url": f"https://mail.google.com/mail/?{email_params}",
                    "email_compose_url": f"mailto:{quote(email_to, safe='@')}?{urlencode({'subject': subject, 'body': body})}",
                    "sms_compose_url": f"sms:{phone_to}?body={quote(body, safe='')}",
                    "message_channel": reservation.message_channel,
                }
            )
        return render(request, "reservations/thank_you.html", context)
