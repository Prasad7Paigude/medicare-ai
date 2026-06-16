"""Booking and ordering routes for MediCare.

Handles appointment booking, hospital bed booking, and medicine order
placement. Each route persists data to MongoDB and triggers a
confirmation email.
"""

import datetime
import logging

from bson.objectid import ObjectId
from flask import Blueprint, jsonify, request

from src.database import get_database
from src.email_service import (
    send_appointment_email,
    send_bed_booking_email,
    send_order_email,
)

logger = logging.getLogger(__name__)

bookings_bp = Blueprint("bookings", __name__)


@bookings_bp.route("/book-appointment", methods=["POST"])
def book_appointment():
    """Book a doctor appointment.

    Request JSON body:
        - name, email, contact, doctor, date, time (all str, required).

    Returns:
        200 on success, 400 on missing fields, 500 on error.
    """
    db = get_database()
    if db is None:
        return jsonify({"success": False, "message": "Database unavailable"}), 503

    try:
        data: dict = request.json or {}
        name: str | None = data.get("name")
        email: str | None = data.get("email")
        contact: str | None = data.get("contact")
        doctor: str | None = data.get("doctor")
        date: str | None = data.get("date")
        time: str | None = data.get("time")

        if not all([name, email, contact, doctor, date, time]):
            return jsonify({"success": False, "message": "Missing required fields"}), 400

        appointment_id = str(ObjectId())
        appointment = {
            "_id": appointment_id,
            "name": name,
            "email": email,
            "contact": contact,
            "doctor": doctor,
            "date": date,
            "time": time,
            "status": "confirmed",
            "created_at": datetime.datetime.now(),
        }

        try:
            db.appointments.insert_one(appointment)
            logger.info("Appointment saved (id=%s)", appointment_id)
        except Exception as db_err:
            logger.error("Database error saving appointment: %s", db_err)
            return jsonify({"success": False, "message": f"Database error: {db_err}"}), 500

        email_result = send_appointment_email(name, email, doctor, date, time)

        return jsonify({
            "success": True,
            "message": "Appointment booked successfully",
            "appointment_id": appointment_id,
            "email_status": email_result,
        })

    except Exception as exc:
        logger.error("Error booking appointment: %s", exc, exc_info=True)
        return jsonify({"success": False, "message": f"Error: {exc}"}), 500


@bookings_bp.route("/api/bed-bookings", methods=["POST"])
def book_bed():
    """Book a hospital bed.

    Request JSON body:
        - patientName, patientEmail, patientContact, hospitalName,
          wardType, admissionDate, feesPerDay (all str, required).

    Returns:
        200 on success, 400 on missing fields, 500 on error.
    """
    db = get_database()
    if db is None:
        return jsonify({"success": False, "message": "Database unavailable"}), 503

    try:
        data: dict = request.json or {}
        patient_name: str | None = data.get("patientName")
        patient_email: str | None = data.get("patientEmail")
        patient_contact: str | None = data.get("patientContact")
        hospital_name: str | None = data.get("hospitalName")
        ward_type: str | None = data.get("wardType")
        admission_date: str | None = data.get("admissionDate")
        fees_per_day: str | None = data.get("feesPerDay")

        if not all([patient_name, patient_email, patient_contact, hospital_name, ward_type, admission_date]):
            return jsonify({"success": False, "message": "Missing required fields"}), 400

        booking_id: str = data.get("id") or f"BED{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

        bed_booking = {
            "_id": booking_id,
            "patientName": patient_name,
            "patientEmail": patient_email,
            "patientContact": patient_contact,
            "hospitalName": hospital_name,
            "wardType": ward_type,
            "admissionDate": admission_date,
            "feesPerDay": fees_per_day,
            "status": "confirmed",
            "bookingDate": datetime.datetime.now(),
        }

        try:
            db.bed_bookings.insert_one(bed_booking)
            logger.info("Bed booking saved (id=%s)", booking_id)
        except Exception as db_err:
            logger.error("Database error saving bed booking: %s", db_err)
            return jsonify({"success": False, "message": f"Database error: {db_err}"}), 500

        email_result = send_bed_booking_email(
            patient_name, patient_email, hospital_name, admission_date, ward_type
        )

        return jsonify({
            "success": True,
            "message": "Bed booked successfully",
            "id": booking_id,
            "email_status": email_result,
        })

    except Exception as exc:
        logger.error("Error booking bed: %s", exc, exc_info=True)
        return jsonify({"success": False, "message": f"Error: {exc}"}), 500


@bookings_bp.route("/order-medicine", methods=["POST"])
def order_medicine():
    """Place a medicine order.

    Request JSON body:
        - name, email, phone, address, medicines (list), paymentMethod
          (all required).

    Returns:
        200 on success, 400 on missing fields, 500 on error.
    """
    db = get_database()
    if db is None:
        return jsonify({"success": False, "message": "Database unavailable"}), 503

    try:
        data: dict = request.json or {}
        name: str | None = data.get("name")
        email: str | None = data.get("email")
        phone: str | None = data.get("phone")
        address: str | None = data.get("address")
        medicines: list = data.get("medicines", [])
        payment_method: str | None = data.get("paymentMethod")

        if not all([name, email, phone, address, medicines, payment_method]):
            return jsonify({"success": False, "message": "Missing required fields"}), 400

        order_id: str = f"ORD{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

        order = {
            "_id": order_id,
            "name": name,
            "email": email,
            "phone": phone,
            "address": address,
            "medicines": medicines,
            "paymentMethod": payment_method,
            "status": "processing",
            "orderDate": datetime.datetime.now(),
        }

        try:
            db.medicine_orders.insert_one(order)
            logger.info("Medicine order saved (id=%s)", order_id)
        except Exception as db_err:
            logger.error("Database error saving order: %s", db_err)
            return jsonify({"success": False, "message": f"Database error: {db_err}"}), 500

        email_result = send_order_email(name, email, order_id, medicines)

        return jsonify({
            "success": True,
            "message": "Order placed successfully",
            "order_id": order_id,
            "email_status": email_result,
        })

    except Exception as exc:
        logger.error("Error placing order: %s", exc, exc_info=True)
        return jsonify({"success": False, "message": f"Error: {exc}"}), 500
