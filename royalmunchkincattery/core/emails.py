"""Email helpers. Every send is wrapped so a flaky SMTP server can never turn
a saved lead into a 500 error: the lead is already in the database and the
failure is logged."""

import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

logger = logging.getLogger("americanmunchkinhouse")


def _send(subject, body, to, reply_to=None):
    try:
        sent = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to,
            reply_to=reply_to or [],
        ).send(fail_silently=False)
        return sent == 1
    except Exception:  # noqa: BLE001 - never break the request over email
        logger.exception("Email send failed: %s", subject)
        return False


def _send_admin_and_customer(admin_subject, admin_body, customer_subject, customer_body, customer_email, reply_to):
    admin_email = settings.ADMIN_NOTIFICATION_EMAIL.strip().casefold()
    customer_email_normalized = customer_email.strip().casefold()
    if admin_email == customer_email_normalized:
        combined_body = f"{customer_body}\n\n--- Cattery notification ---\n{admin_body}"
        sent = _send(admin_subject, combined_body, [settings.ADMIN_NOTIFICATION_EMAIL], reply_to)
        return sent, sent

    admin_sent = _send(admin_subject, admin_body, [settings.ADMIN_NOTIFICATION_EMAIL], reply_to)
    customer_sent = _send(customer_subject, customer_body, [customer_email], [settings.ADMIN_NOTIFICATION_EMAIL])
    return admin_sent, customer_sent


def notify_admin_of_contact(message):
    body = render_to_string("emails/contact_admin_notice.txt", {"m": message})
    return _send(f"New contact message: {message.subject or message.name}", body, [settings.ADMIN_NOTIFICATION_EMAIL], [message.email])


def notify_contact_submission(message):
    admin_subject = f"New contact message: {message.subject or message.name}"
    admin_body = render_to_string("emails/contact_admin_notice.txt", {"m": message})
    customer_subject = "We received your message | American Munchkin House"
    customer_body = render_to_string("emails/contact_customer_confirmation.txt", {"message": message})
    return _send_admin_and_customer(
        admin_subject,
        admin_body,
        customer_subject,
        customer_body,
        message.email,
        [message.email],
    )


def notify_admin_of_waitlist(entry):
    body = render_to_string("emails/waitlist_admin_notice.txt", {"e": entry})
    return _send(f"New waitlist signup: {entry.name}", body, [settings.ADMIN_NOTIFICATION_EMAIL], [entry.email])


def confirm_waitlist(entry):
    body = render_to_string("emails/waitlist_customer_confirmation.txt", {"e": entry})
    return _send("You're on the American Munchkin House waitlist", body, [entry.email], [settings.ADMIN_NOTIFICATION_EMAIL])
