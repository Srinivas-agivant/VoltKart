"""Conversation history and multi-turn session persistence service for VoltKart."""

from datetime import datetime, timezone
import uuid
from typing import Any, Optional
import config
from database import get_db


class ConversationService:
    """Manages chat sessions, turns, and recommendation position tracking in MongoDB."""

    def __init__(self, db=None):
        self.db = db if db is not None else get_db()

    def create_conversation(self, title: str = "New Shopping Chat") -> str:
        """Creates a new conversation session and returns its conversation_id."""
        conv_id = str(uuid.uuid4())
        now_utc = datetime.now(timezone.utc)
        doc = {
            "conversation_id": conv_id,
            "session_id": conv_id,  # Provides unique session_id to satisfy legacy indexes
            "title": title,
            "created_at": now_utc,
            "updated_at": now_utc,
        }
        coll = self.db[config.COLLECTION_CONVERSATIONS]
        try:
            coll.insert_one(doc)
        except Exception as e:
            if "duplicate key error" in str(e).lower() and "session_id" in str(e).lower():
                try:
                    coll.drop_index("session_id_1")
                    coll.insert_one(doc)
                except Exception:
                    pass
            else:
                raise
        return conv_id

    def update_conversation_title(self, conversation_id: str, title: str):
        """Updates the descriptive title of a conversation based on initial query."""
        self.db[config.COLLECTION_CONVERSATIONS].update_one(
            {"conversation_id": conversation_id},
            {"$set": {"title": title[:40], "updated_at": datetime.now(timezone.utc)}},
        )

    def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        intent: Optional[str] = None,
        retrieved_ids: Optional[list[str]] = None,
    ):
        """Appends a message turn to the messages collection."""
        now_utc = datetime.now(timezone.utc)
        msg_doc = {
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "intent": intent,
            "retrieved_record_ids": retrieved_ids or [],
            "created_at": now_utc,
        }
        self.db[config.COLLECTION_MESSAGES].insert_one(msg_doc)
        self.db[config.COLLECTION_CONVERSATIONS].update_one(
            {"conversation_id": conversation_id},
            {"$set": {"updated_at": now_utc}},
        )

    def save_recommendations(self, conversation_id: str, products: list[dict]):
        """Records the ordinal positions (1, 2, 3) of recommended laptops."""
        now_utc = datetime.now(timezone.utc)
        recs_coll = self.db[config.COLLECTION_RECOMMENDATIONS]
        for idx, prod in enumerate(products, start=1):
            rec_doc = {
                "conversation_id": conversation_id,
                "product_id": prod.get("product_id"),
                "position": idx,
                "recommendation_reason": prod.get("recommendation_reason", ""),
                "created_at": now_utc,
            }
            recs_coll.insert_one(rec_doc)

    def get_conversation_history(self, conversation_id: str, limit: int = 15) -> list[dict]:
        """Retrieves chronological messages for an active conversation."""
        msgs = list(
            self.db[config.COLLECTION_MESSAGES]
            .find({"conversation_id": conversation_id}, {"_id": 0})
            .sort("created_at", 1)
            .limit(limit)
        )
        return msgs

    def list_recent_conversations(self, limit: int = 20) -> list[dict]:
        """Returns conversation summaries for the Streamlit sidebar."""
        return list(
            self.db[config.COLLECTION_CONVERSATIONS]
            .find({}, {"_id": 0})
            .sort("updated_at", -1)
            .limit(limit)
        )

    def get_last_recommended_products(self, conversation_id: str) -> list[dict]:
        """Retrieves full product records for the most recent recommendation turn."""
        recs = list(
            self.db[config.COLLECTION_RECOMMENDATIONS]
            .find({"conversation_id": conversation_id}, {"_id": 0})
            .sort("created_at", -1)
            .limit(3)
        )
        if not recs:
            return []
        pids = [r["product_id"] for r in recs if "product_id" in r]
        return list(self.db[config.COLLECTION_PRODUCTS].find({"product_id": {"$in": pids}}, {"_id": 0}))
