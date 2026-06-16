"""Email notification service for MediCare.

Handles sending transactional emails (appointment confirmations,
order confirmations, bed bookings, welcome emails) via SMTP.
"""

import logging

from flask import Flask
from flask_mail import Mail, Message

from config.settings import (
    MAIL_SERVER,
    MAIL_PORT,
    MAIL_USE_TLS,
    MAIL_USE_SSL,
    MAIL_USERNAME,
    MAIL_PASSWORD,
    MAIL_DEFAULT_SENDER,
    MAIL_DEBUG,
)

logger = logging.getLogger(__name__)

mail: Mail | None = None


def init_mail(app: Flask) -> Mail:
    """Configure and initialise the Flask-Mail extension on the given app.

    Args:
        app: The Flask application instance.

    Returns:
        The configured ``Mail`` instance.
    """
    app.config["MAIL_SERVER"] = MAIL_SERVER
    app.config["MAIL_PORT"] = MAIL_PORT
    app.config["MAIL_USE_TLS"] = MAIL_USE_TLS
    app.config["MAIL_USE_SSL"] = MAIL_USE_SSL
    app.config["MAIL_USERNAME"] = MAIL_USERNAME
    app.config["MAIL_PASSWORD"] = MAIL_PASSWORD
    app.config["MAIL_DEFAULT_SENDER"] = MAIL_DEFAULT_SENDER
    app.config["MAIL_DEBUG"] = MAIL_DEBUG

    global mail  # noqa: PLW0603
    mail = Mail(app)
    logger.info("Flask-Mail initialised (server=%s, port=%s)", MAIL_SERVER, MAIL_PORT)
    return mail


def _send_email(to: str, subject: str, body: str) -> dict:
    """Send an email via the configured SMTP server.

    Args:
        to: Recipient email address.
        subject: Email subject line.
        body: Plain-text email body.

    Returns:
        A dict with keys ``success`` (bool) and ``message`` (str).
    """
    try:
        msg = Message(
            subject=subject,
            recipients=[to],
            body=body,
            sender=MAIL_DEFAULT_SENDER,
        )
        mail.send(msg)  # type: ignore[union-attr]
        logger.info("Email sent successfully to %s (subject=%s)", to, subject)
        return {"success": True, "message": "Email sent successfully"}

    except Exception as exc:
        logger.error("Failed to send email to %s: %s", to, exc, exc_info=True)
        logger.debug("Email content (not sent) -> To: %s | Subject: %s", to, subject)
        return {"success": False, "message": f"Email failed to send: {exc}"}


def send_appointment_email(
    name: str, email: str, doctor: str, date: str, time: str
) -> dict:
    """Send an appointment confirmation email.

    Args:
        name: Patient name.
        email: Patient email address.
        doctor: Doctor name.
        date: Appointment date.
        time: Appointment time.

    Returns:
        Result dict from ``_send_email``.
    """
    subject = "Appointment Confirmation - MediCare"
    body = (
        f"Dear {name},\n\n"
        f"Your appointment with Dr. {doctor} has been confirmed for {date} at {time}.\n\n"
        f"Please arrive 15 minutes before your scheduled appointment time. "
        f"If you need to reschedule or cancel, please contact us at least 24 hours in advance.\n\n"
        f"Appointment Details:\n"
        f"- Doctor: Dr. {doctor}\n"
        f"- Date: {date}\n"
        f"- Time: {time}\n"
        f"- Patient: {name}\n\n"
        f"Thank you for choosing MediCare!\n\n"
        f"Best regards,\n"
        f"The MediCare Team\n"
        f"medicare162733@gmail.com"
    )
    return _send_email(email, subject, body)


def send_bed_booking_email(
    name: str, email: str, hospital: str, date: str, ward_type: str = ""
) -> dict:
    """Send a hospital bed booking confirmation email.

    Args:
        name: Patient name.
        email: Patient email address.
        hospital: Hospital name.
        date: Admission date.
        ward_type: Type of ward booked (optional).

    Returns:
        Result dict from ``_send_email``.
    """
    subject = "Hospital Bed Booking Confirmation - MediCare"
    body = (
        f"Dear {name},\n\n"
        f"Your hospital bed booking has been confirmed.\n\n"
        f"Booking Details:\n"
        f"- Hospital: {hospital}\n"
        f"- Admission Date: {date}\n"
        f"- Ward Type: {ward_type}\n"
        f"- Patient: {name}\n\n"
        f"Please arrive at the hospital reception desk on the scheduled date "
        f"with your ID proof and any relevant medical records.\n\n"
        f"If you need to reschedule or cancel your booking, "
        f"please contact us at least 48 hours in advance.\n\n"
        f"Thank you for choosing MediCare!\n\n"
        f"Best regards,\n"
        f"The MediCare Team\n"
        f"medicare162733@gmail.com"
    )
    return _send_email(email, subject, body)


def send_order_email(name: str, email: str, order_id: str, medicines: list) -> dict:
    """Send a medicine order confirmation email.

    Args:
        name: Customer name.
        email: Customer email address.
        order_id: Unique order identifier.
        medicines: List of medicine dicts containing 'name' and 'quantity' keys.

    Returns:
        Result dict from ``_send_email``.
    """
    medicine_lines = "\n".join(
        f"- {m.get('name', 'Unknown')} (Qty: {m.get('quantity', 'N/A')})"
        for m in medicines
    )
    subject = "Order Confirmation - MediCare"
    body = (
        f"Dear {name},\n\n"
        f"Thank you for your order with MediCare!\n\n"
        f"Your medicine order (Order ID: {order_id}) has been received "
        f"and is being processed.\n\n"
        f"Order Details:\n"
        f"- Order ID: {order_id}\n"
        f"- Customer: {name}\n"
        f"- Status: Processing\n\n"
        f"Items Ordered:\n"
        f"{medicine_lines}\n\n"
        f"If you have any questions, please contact our customer service team.\n\n"
        f"Thank you for choosing MediCare!\n\n"
        f"Best regards,\n"
        f"The MediCare Team\n"
        f"medicare162733@gmail.com"
    )
    return _send_email(email, subject, body)


def send_welcome_email(name: str, email: str) -> dict:
    """Send a welcome email to a newly registered user.

    Args:
        name: User's full name.
        email: User's email address.

    Returns:
        Result dict from ``_send_email``.
    """
    subject = "Welcome to MediCare!"
    body = (
        f"Dear {name},\n\n"
        f"Welcome to MediCare! We're thrilled to have you join our healthcare platform.\n\n"
        f"With your new account, you can:\n"
        f"- Book appointments with top doctors\n"
        f"- Order medicines online\n"
        f"- Book hospital beds\n"
        f"- Access our AI doctor for quick consultations\n\n"
        f"If you have any questions, please don't hesitate to contact our support team.\n\n"
        f"Thank you for choosing MediCare!\n\n"
        f"Best regards,\n"
        f"The MediCare Team\n"
        f"medicare162733@gmail.com"
    )
    return _send_email(email, subject, body)
