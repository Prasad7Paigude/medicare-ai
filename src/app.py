"""MediCare Flask application factory and entry point.

Assembles the Flask application, registers blueprints, initialises
services (MongoDB, Mail, aiXplain), and begins serving requests.
"""

import logging
import os

from flask import Flask, send_from_directory
from flask_cors import CORS

from config.settings import (
    FLASK_HOST,
    FLASK_PORT,
    FLASK_DEBUG,
    TEAM_API_KEY,
    UPLOAD_DIR,
    FRONTEND_DIR,
    ALLOWED_EXTENSIONS,
)
from utils.logging_setup import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

# Set API key early so aiXplain imports can read it
os.environ["TEAM_API_KEY"] = TEAM_API_KEY


def create_app() -> Flask:
    """Build and return a fully configured Flask application.

    Returns:
        A ready-to-run ``Flask`` instance.
    """
    app = Flask(
        __name__,
        static_folder=str(FRONTEND_DIR),
        static_url_path="/",
    )
    CORS(app)

    # ── Upload directory ────────────────────────────────────────────
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = str(UPLOAD_DIR)

    # ── Database ────────────────────────────────────────────────────
    from src.database import connect_to_mongodb

    connect_to_mongodb()

    # ── Email ───────────────────────────────────────────────────────
    from src.email_service import init_mail

    init_mail(app)
    _verify_mail_connection(app)

    # ── AI Doctor agent ─────────────────────────────────────────────
    from src.ai_doctor import AIDoctorAgent
    from src.routes import set_ai_doctor_agent

    agent = AIDoctorAgent()
    set_ai_doctor_agent(agent)

    # ── Register blueprints ─────────────────────────────────────────
    from src.auth import auth_bp
    from src.bookings import bookings_bp
    from src.routes import routes_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(routes_bp)

    # ── Static file serving ─────────────────────────────────────────
    @app.route("/<path:path>")
    def serve_static(path: str):
        return send_from_directory(str(FRONTEND_DIR), path)

    @app.route("/")
    def index():
        return send_from_directory(str(FRONTEND_DIR), "index.html")

    return app


def _verify_mail_connection(app: Flask) -> None:
    """Verify SMTP connectivity inside an application context.

    Args:
        app: The Flask application instance.
    """
    try:
        with app.app_context():
            from src.email_service import mail

            if mail:
                mail.connect()
                logger.info("Email server connection verified")
    except Exception as exc:
        logger.warning("Email server connection failed: %s", exc)
        logger.info("Application will continue without email functionality")


def main() -> None:
    """Run the MediCare Flask application."""
    app = create_app()
    logger.info(
        "Starting MediCare server on %s:%s (debug=%s)",
        FLASK_HOST,
        FLASK_PORT,
        FLASK_DEBUG,
    )
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)


if __name__ == "__main__":
    main()
