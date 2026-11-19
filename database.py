"""MongoDB database connectivity, collection management, and indexing for VoltKart."""

import logging
from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import mongomock

import config

logger = logging.getLogger("voltkart.database")


class DatabaseManager:
    """Manages MongoDB connections, collection handles, and index initialization."""

    _instance = None
    _client = None
    _db = None
    _is_mock = False
    _connection_error = None
    _active_uri = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self, uri: str = None):
        """Initializes connection to MongoDB with mongomock fallback for resilience."""
        target_uri = uri or config.MONGODB_URI
        self._active_uri = target_uri
        self._connection_error = None

        try:
            # Attempt connection to MongoDB with 3-second timeout
            client = MongoClient(target_uri, serverSelectionTimeoutMS=3000)
            client.admin.command("ping")
            self._client = client
            self._db = client[config.DATABASE_NAME]
            self._is_mock = False
            self._connection_error = None
            logger.info("Connected to live MongoDB at %s", target_uri)
        except Exception as exc:
            self._connection_error = str(exc)
            logger.warning(
                "Could not connect to MongoDB at %s (%s). Falling back to resilient in-memory mock database.",
                target_uri,
                exc,
            )
            # Resilient in-memory fallback using mongomock
            self._client = mongomock.MongoClient()
            self._db = self._client[config.DATABASE_NAME]
            self._is_mock = True

        self.ensure_indexes()

    def reconnect(self, uri: str):
        """Attempts reconnection with a new or updated MongoDB URI."""
        self._initialize(uri=uri)

    @property
    def db(self):
        """Returns the active MongoDB database instance."""
        return self._db

    @property
    def is_mock(self) -> bool:
        """Returns True if running on in-memory mock fallback."""
        return self._is_mock

    @property
    def connection_error(self) -> str | None:
        """Returns the connection error message if fallback was used."""
        return self._connection_error

    @property
    def active_uri(self) -> str:
        """Returns the currently configured connection URI."""
        return self._active_uri or config.MONGODB_URI

    def get_collection(self, collection_name: str):
        """Returns a collection by name."""
        return self._db[collection_name]

    def ensure_indexes(self):
        """Ensures all indexes are created across the 8 collections independently."""
        # 1. products
        try:
            products = self._db[config.COLLECTION_PRODUCTS]
            products.create_index([("product_id", ASCENDING)], unique=True)
            products.create_index([("price", ASCENDING)])
            products.create_index([("brand", ASCENDING)])
            products.create_index([("usage_type", ASCENDING)])
            products.create_index([("usage_type", ASCENDING), ("price", ASCENDING)])
            products.create_index([("brand", ASCENDING), ("price", ASCENDING)])
        except Exception as e:
            logger.debug("Products index notice: %s", e)

        # 2. faqs
        try:
            faqs = self._db[config.COLLECTION_FAQS]
            faqs.create_index([("faq_id", ASCENDING)], unique=True)
            faqs.create_index([("category", ASCENDING)])
            if not self._is_mock:
                faqs.create_index([("question", TEXT), ("keywords", TEXT)])
        except Exception as e:
            logger.debug("FAQs index notice: %s", e)

        # 3. store_policies
        try:
            policies = self._db[config.COLLECTION_POLICIES]
            policies.create_index([("policy_id", ASCENDING)], unique=True)
            policies.create_index([("category", ASCENDING)])
            if not self._is_mock:
                policies.create_index([("title", TEXT), ("description", TEXT), ("keywords", TEXT)])
        except Exception as e:
            logger.debug("Policies index notice: %s", e)

        # 4. conversations
        try:
            convs = self._db[config.COLLECTION_CONVERSATIONS]
            # Safely drop legacy conflicting session_id index if present
            try:
                for idx in convs.list_indexes():
                    idx_name = idx.get("name", "")
                    if idx_name == "session_id_1" or "session_id" in idx.get("key", {}):
                        convs.drop_index(idx_name)
                        logger.info("Dropped legacy index %s on conversations", idx_name)
            except Exception as e:
                logger.debug("Legacy index cleanup notice: %s", e)

            convs.create_index([("conversation_id", ASCENDING)], unique=True)
            convs.create_index([("updated_at", DESCENDING)])
        except Exception as e:
            logger.debug("Conversations index notice: %s", e)

        # 5. messages
        try:
            msgs = self._db[config.COLLECTION_MESSAGES]
            msgs.create_index([("conversation_id", ASCENDING), ("created_at", ASCENDING)])
        except Exception as e:
            logger.debug("Messages index notice: %s", e)

        # 6. recommendations
        try:
            recs = self._db[config.COLLECTION_RECOMMENDATIONS]
            recs.create_index([("conversation_id", ASCENDING), ("position", ASCENDING)])
            recs.create_index([("created_at", DESCENDING)])
        except Exception as e:
            logger.debug("Recommendations index notice: %s", e)

        # 7. import_history
        try:
            history = self._db[config.COLLECTION_IMPORT_HISTORY]
            history.create_index([("imported_at", DESCENDING)])
        except Exception as e:
            logger.debug("Import history index notice: %s", e)

        # 8. knowledge_base (PDF chunks)
        try:
            kb = self._db[config.COLLECTION_KNOWLEDGE_BASE]
            kb.create_index([("chunk_id", ASCENDING)], unique=True)
            kb.create_index([("filename", ASCENDING)])
            kb.create_index([("category", ASCENDING)])
            if not self._is_mock:
                kb.create_index([("chunk_text", TEXT), ("category", TEXT), ("filename", TEXT)])
        except Exception as e:
            logger.debug("Knowledge base index notice: %s", e)

        logger.info("MongoDB indexes verified successfully.")


def get_db():
    """Convenience accessor for the global database handle."""
    return DatabaseManager().db


def get_db_manager() -> DatabaseManager:
    """Returns the singleton DatabaseManager instance."""
    return DatabaseManager()
