"""MongoDB database connection management.

Provides a singleton-like connection to MongoDB Atlas and exposes
the top-level database handle for use across the application.
"""

import logging

import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError

from config.settings import MONGODB_URI, MONGODB_DB_NAME

logger = logging.getLogger(__name__)

client: MongoClient | None = None
db: pymongo.database.Database | None = None


def connect_to_mongodb() -> pymongo.database.Database | None:
    """Establish connection to MongoDB Atlas and verify it is alive.

    Returns:
        A ``pymongo.database.Database`` instance for the configured
        database, or ``None`` if the connection could not be established.
    """
    global client, db  # noqa: PLW0603

    try:
        client = MongoClient(MONGODB_URI)
        db = client.get_database(MONGODB_DB_NAME)

        client.admin.command("ping")
        logger.info("MongoDB Atlas connected successfully to '%s'", MONGODB_DB_NAME)

        collections = db.list_collection_names()
        logger.info("Available collections: %s", collections)

        return db

    except ConnectionFailure as exc:
        logger.error("MongoDB Atlas connection failure: %s", exc)
    except ConfigurationError as exc:
        logger.error("MongoDB configuration error: %s", exc)
    except Exception as exc:
        logger.error("Unexpected MongoDB connection error: %s", exc, exc_info=True)

    return None


def get_database() -> pymongo.database.Database | None:
    """Return the active database handle.

    Returns:
        The ``pymongo.database.Database`` instance if connected,
        otherwise ``None``.
    """
    return db
