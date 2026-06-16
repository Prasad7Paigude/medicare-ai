"""User authentication routes for MediCare.

Handles user registration (signup) and login with bcrypt password hashing.
"""

import datetime
import logging

import bcrypt
import pymongo
from bson.objectid import ObjectId
from flask import Blueprint, jsonify, request

from src.database import get_database
from src.email_service import send_welcome_email

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["POST"])
def signup():
    """Register a new user account.

    Request JSON body:
        - fullName (str): User's full name.
        - email (str): User's email address.
        - phone (str): User's phone number.
        - password (str): User's password (will be hashed).

    Returns:
        201 on success, 400 if validation fails or email exists, 500 on error.
    """
    db = get_database()
    if db is None:
        logger.error("Signup blocked: database unavailable")
        return jsonify({"success": False, "message": "Database unavailable"}), 503

    try:
        data: dict = request.json or {}
        full_name: str | None = data.get("fullName")
        email: str | None = data.get("email")
        phone: str | None = data.get("phone")
        password: str | None = data.get("password")

        if not all([full_name, email, phone, password]):
            return jsonify({"success": False, "message": "Missing required fields"}), 400

        existing_user = db.users.find_one({"email": email})
        if existing_user:
            return jsonify({"success": False, "message": "Email already registered"}), 400

        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        user = {
            "fullName": full_name,
            "email": email,
            "phone": phone,
            "password": hashed.decode("utf-8"),
            "createdAt": datetime.datetime.now(),
        }
        result = db.users.insert_one(user)

        user_response = {
            "id": str(result.inserted_id),
            "fullName": full_name,
            "email": email,
            "phone": phone,
        }

        email_result = send_welcome_email(full_name, email)

        return jsonify({
            "success": True,
            "message": "Account created successfully!",
            "user": user_response,
            "email_status": email_result,
        })

    except Exception as exc:
        logger.error("Signup error: %s", exc, exc_info=True)
        return jsonify({"success": False, "message": f"Error: {exc}"}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate an existing user.

    Request JSON body:
        - email (str): User's email address.
        - password (str): User's password.

    Returns:
        200 on success with user object, 400/401 on validation failure,
        500 on error.
    """
    db = get_database()
    if db is None:
        logger.error("Login blocked: database unavailable")
        return jsonify({"success": False, "message": "Database unavailable"}), 503

    try:
        data: dict = request.json or {}
        email: str | None = data.get("email")
        password: str | None = data.get("password")

        if not all([email, password]):
            return jsonify({"success": False, "message": "Email and password are required"}), 400

        user = db.users.find_one({"email": email})
        if not user:
            return jsonify({"success": False, "message": "Invalid email or password"}), 401

        if not bcrypt.checkpw(
            password.encode("utf-8"), user["password"].encode("utf-8")
        ):
            return jsonify({"success": False, "message": "Invalid email or password"}), 401

        user_response = {
            "id": str(user["_id"]),
            "fullName": user.get("fullName"),
            "email": user.get("email"),
            "phone": user.get("phone"),
        }

        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": user_response,
        })

    except Exception as exc:
        logger.error("Login error: %s", exc, exc_info=True)
        return jsonify({"success": False, "message": f"Error: {exc}"}), 500
