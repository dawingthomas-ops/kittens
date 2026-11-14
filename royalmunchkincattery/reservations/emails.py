from django.conf import settings
from django.template.loader import render_to_string

from core.emails import _send, _send_admin_and_customer


def notify_admin_of_reservation(reservation):
    """Sends the reservation and the buyer's preferred contact method to the
    admin inbox (ADMIN_NOTIFICATION_EMAIL). Reply-To is the customer, so
    admin can answer straight from their mail client."""
    subject = f"New reservation inquiry: {reservation.kitten.name} / {reservation.full_name}"
    body = render_to_string("emails/reservation_admin_notice.txt", {"reservation": reservation, "SITE_DOMAIN": settings.SITE_DOMAIN})
    return _send(subject, body, [settings.ADMIN_NOTIFICATION_EMAIL], [reservation.email])


def notify_customer_confirmation(reservation):
    subject = f"We received your inquiry about {reservation.kitten.name} | Royal Munchkin Cattery"
    body = render_to_string("emails/reservation_customer_confirmation.txt", {"reservation": reservation})
    return _send(subject, body, [reservation.email], [settings.ADMIN_NOTIFICATION_EMAIL])


def notify_reservation_submission(reservation):
    admin_subject = f"New reservation inquiry: {reservation.kitten.name} / {reservation.full_name}"
    admin_body = render_to_string(
        "emails/reservation_admin_notice.txt",
        {"reservation": reservation, "SITE_DOMAIN": settings.SITE_DOMAIN},
    )
    customer_subject = f"We received your inquiry about {reservation.kitten.name} | Royal Munchkin Cattery"
    customer_body = render_to_string(
        "emails/reservation_customer_confirmation.txt",
        {"reservation": reservation},
    )
    return _send_admin_and_customer(
        admin_subject,
        admin_body,
        customer_subject,
        customer_body,
        reservation.email,
        [reservation.email],
    )
