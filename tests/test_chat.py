"""Tests for conversation state, multi-turn history, and relative product reference resolution."""

import mongomock
import pytest

from backend.conversation_service import ConversationService
from backend.retrieval_service import RetrievalService


@pytest.fixture
def chat_mock_db():
    db = mongomock.MongoClient()["test_chat_db"]
    products = [
        {"product_id": "P1", "name": "Laptop Alpha", "price": 40000.0, "ram": "8GB", "storage": "256GB SSD"},
        {"product_id": "P2", "name": "Laptop Beta", "price": 55000.0, "ram": "16GB", "storage": "512GB SSD"},
        {"product_id": "P3", "name": "Laptop Gamma", "price": 70000.0, "ram": "16GB", "storage": "1TB SSD"},
    ]
    db["products"].insert_many(products)
    return db


def test_conversation_persistence(chat_mock_db):
    """Verify session creation and message turn persistence."""
    conv_svc = ConversationService(db=chat_mock_db)
    cid = conv_svc.create_conversation(title="Test Coding Chat")
    assert cid is not None

    conv_svc.save_message(cid, "user", "Suggest coding laptop under 60k", intent="recommend")
    conv_svc.save_message(cid, "assistant", "Here is Laptop Beta", intent="recommend", retrieved_ids=["P2"])

    history = conv_svc.get_conversation_history(cid)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"
    assert history[1]["retrieved_record_ids"] == ["P2"]


def test_relative_reference_resolution(chat_mock_db):
    """Verify that 'compare the first two' resolves to positions 1 and 2 from previous recommendations."""
    conv_svc = ConversationService(db=chat_mock_db)
    retrieval_svc = RetrievalService(db=chat_mock_db)

    cid = conv_svc.create_conversation("Recommendation Test")
    # Simulate saving 3 recommendations
    recs = [
        {"product_id": "P1", "recommendation_reason": "Value"},
        {"product_id": "P2", "recommendation_reason": "Performance"},
        {"product_id": "P3", "recommendation_reason": "Storage"},
    ]
    conv_svc.save_recommendations(cid, recs)

    # Resolve positions [1, 2] ("the first two")
    resolved = retrieval_svc.resolve_comparison_products(conversation_id=cid, positions=[1, 2])
    assert len(resolved) == 2
    pids = [p["product_id"] for p in resolved]
    assert "P1" in pids
    assert "P2" in pids
    assert "P3" not in pids


def test_create_conversation_handles_legacy_session_id_index(chat_mock_db):
    """Verify create_conversation succeeds even when a unique index on session_id exists."""
    import config
    convs = chat_mock_db[config.COLLECTION_CONVERSATIONS]
    convs.create_index([("session_id", 1)], unique=True)
    conv_svc = ConversationService(db=chat_mock_db)

    cid1 = conv_svc.create_conversation("Chat 1")
    cid2 = conv_svc.create_conversation("Chat 2")
    assert cid1 != cid2
    assert convs.count_documents({}) >= 2


def test_interactive_session_reset(chat_mock_db):
    """Verify that resetting a session creates a clean new conversation without legacy messages."""
    conv_svc = ConversationService(db=chat_mock_db)
    cid1 = conv_svc.create_conversation("Active Chat")
    conv_svc.save_message(cid1, "user", "Hello")
    assert len(conv_svc.get_conversation_history(cid1)) == 1

    # Simulate reset: create a new session
    cid2 = conv_svc.create_conversation("Storefront Chat")
    assert cid2 != cid1
    assert len(conv_svc.get_conversation_history(cid2)) == 0
