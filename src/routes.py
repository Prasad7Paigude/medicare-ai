"""Miscellaneous API routes for MediCare.

Contains generic email-sending endpoints and the AI Doctor endpoint.
"""

import logging

from flask import Blueprint, jsonify, request

from src.email_service import (
    _send_email,
    send_appointment_email,
    send_bed_booking_email,
    send_order_email,
)
from src.ai_doctor import AIDoctorAgent

logger = logging.getLogger(__name__)

routes_bp = Blueprint("routes", __name__)

_ai_doctor_agent: AIDoctorAgent | None = None


def set_ai_doctor_agent(agent: AIDoctorAgent) -> None:
    """Inject the shared AI Doctor agent instance into this module.

    Args:
        agent: The application-wide ``AIDoctorAgent`` singleton.
    """
    global _ai_doctor_agent  # noqa: PLW0603
    _ai_doctor_agent = agent


# ── Generic email endpoint ──────────────────────────────────────────────


@routes_bp.route("/api/send-email", methods=["POST"])
def api_send_email():
    """Send an arbitrary email via POST.

    Request JSON body:
        - to (str): Recipient address.
        - subject (str): Email subject.
        - body (str): Email body.

    Returns:
        200 on success, 400 on missing fields.
    """
    data: dict = request.json or {}
    to: str | None = data.get("to")
    subject: str | None = data.get("subject")
    body: str | None = data.get("body")

    if not all([to, subject, body]):
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    result = _send_email(to, subject, body)
    return jsonify(result)


# ── Appointment confirmation ────────────────────────────────────────────


@routes_bp.route("/api/send-appointment-confirmation", methods=["POST"])
def send_appointment_confirmation():
    """Send a pre-formatted appointment confirmation email.

    Request JSON body:
        - email, name, doctor, date, time (all str, required).
    """
    data: dict = request.json or {}
    result = send_appointment_email(
        name=data.get("name", ""),
        email=data.get("email", ""),
        doctor=data.get("doctor", ""),
        date=data.get("date", ""),
        time=data.get("time", ""),
    )
    return jsonify(result)


# ── Order confirmation ──────────────────────────────────────────────────


@routes_bp.route("/api/send-order-confirmation", methods=["POST"])
def send_order_confirmation():
    """Send a pre-formatted medicine order confirmation email.

    Request JSON body:
        - email, name, orderId (all str, required).
    """
    data: dict = request.json or {}
    result = send_order_email(
        name=data.get("name", ""),
        email=data.get("email", ""),
        order_id=data.get("orderId", ""),
        medicines=data.get("medicines", []),
    )
    return jsonify(result)


# ── Bed booking confirmation ────────────────────────────────────────────


@routes_bp.route("/api/send-bed-confirmation", methods=["POST"])
def send_bed_confirmation():
    """Send a pre-formatted hospital bed booking confirmation email.

    Request JSON body:
        - email, name, hospital, date (all str, required).
    """
    data: dict = request.json or {}
    result = send_bed_booking_email(
        name=data.get("name", ""),
        email=data.get("email", ""),
        hospital=data.get("hospital", ""),
        date=data.get("date", ""),
    )
    return jsonify(result)


# ── AI Doctor endpoint ──────────────────────────────────────────────────


@routes_bp.route("/api/ai-doctor", methods=["POST"])
def ai_doctor():
    """Send a message to the AI Doctor and receive a response.

    Request JSON body:
        - message (str, required): The user's input text.
        - userId (str, required): Unique user identifier for session
          tracking.

    Returns:
        200 with AI response, 400 on missing fields, 503 if agent down.
    """
    data: dict = request.json or {}
    user_input: str | None = data.get("message")
    user_id: str | None = data.get("userId")

    if not user_input or not user_id:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    if _ai_doctor_agent is None:
        logger.warning("AI Doctor endpoint called but agent is None")
        return jsonify({
            "success": False,
            "message": "AI Doctor service is currently unavailable. Please try again later.",
        }), 503

    result = _ai_doctor_agent.process_message(user_input, user_id)
    status_code = 200 if result["success"] else 503
    return jsonify(result), status_code
