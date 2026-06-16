"""Centralized logging configuration for the MediCare application.

Replaces bare ``print()`` calls with structured logging that includes
timestamps, log levels, and module origins.
"""

import logging
import sys


def configure_logging(level: int = logging.INFO) -> None:
    """Configure the root logger with a consistent format and stream handler.

    Args:
        level: Logging level (e.g. ``logging.DEBUG``, ``logging.INFO``).
               Defaults to ``logging.INFO``.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
