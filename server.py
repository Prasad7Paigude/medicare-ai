"""MediCare backend entry point.

This module provides backward-compatible access to the refactored
application.  All core logic now lives in the ``src`` package.
"""

import logging
import os

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)

from src.app import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":
    import config.settings as settings

    app.run(
        host=settings.FLASK_HOST,
        port=settings.FLASK_PORT,
        debug=settings.FLASK_DEBUG,
    )
