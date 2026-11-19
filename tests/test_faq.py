"""Tests for customer support FAQ and policy retrieval with strict grounding."""

import mongomock
import pytest

from backend.retrieval_service import RetrievalService
from backend.gemini_service import GeminiService


@pytest.fixture
def policy_mock_db():
    db = mongomock.MongoClient()["test_db"]
    policies = [
        {
            "policy_id": "POL-001",
            "category": "return",
            "title": "7-Day Return Policy",
            "description": "VoltKart offers a 7-day hassle-free return window for factory-sealed boxes.",
            "keywords": ["return", "exchange", "replacement"],
        },
        {
            "policy_id": "POL-002",
            "category": "warranty",
            "title": "1-Year Onsite Warranty",
            "description": "All laptops include 1-year official onsite warranty.",
            "keywords": ["warranty", "repair"],
        },
    ]
    faqs = [
        {
            "faq_id": "FAQ-001",
            "category": "Shipping",
            "question": "What are the shipping charges?",
            "answer": "VoltKart provides 100% Free Express Shipping on all laptop orders.",
            "keywords": ["shipping", "free", "delivery charges"],
        }
    ]
    db["store_policies"].insert_many(policies)
    db["faqs"].insert_many(faqs)
    return db


def test_documented_policy_retrieval(policy_mock_db):
    """Verify return policy is retrieved correctly."""
    retrieval = RetrievalService(db=policy_mock_db)
    docs = retrieval.get_support_answers("What is your return policy?", category="return")
    assert len(docs) > 0
    assert docs[0]["policy_id"] == "POL-001"
    assert "7-day" in docs[0]["description"].lower()


def test_zero_hallucination_on_unlisted_policy(policy_mock_db):
    """Verify that unlisted policies (e.g. EMI) are not fabricated."""
    retrieval = RetrievalService(db=policy_mock_db)
    docs = retrieval.get_support_answers("Do you have zero-cost EMI?")
    # No EMI policy exists in test database
    assert len(docs) == 0

    gemini = GeminiService(api_key="")
    answer = gemini.generate_grounded_response(
        user_query="Do you offer EMI?",
        intent="support",
        retrieved_docs=docs,
    )
    assert "unavailable" in answer.lower()


def test_single_best_output_perfect_match(policy_mock_db):
    """Verify that only ONE best possible output is generated for a query based on the perfect match."""
    retrieval = RetrievalService(db=policy_mock_db)
    docs = retrieval.get_support_answers("do u offer free shipping")
    assert len(docs) > 0
    assert docs[0]["faq_id"] == "FAQ-001"

    gemini = GeminiService(api_key="")
    answer = gemini.generate_grounded_response(
        user_query="do u offer free shipping",
        intent="support",
        retrieved_docs=docs,
    )
    # Must directly return the single perfect match without dumping multiple questions or 'Q:'
    assert "100% Free Express Shipping" in answer
    assert "Q:" not in answer


def test_chunk_text_isolates_specific_question_answer():
    """Verify that multi-question PDF chunks extract only the specific matching answer."""
    chunk_doc = {
        "chunk_id": "CHK-001",
        "chunk_text": (
            "Q: How long does delivery take? Standard delivery is estimated to take 3-7 business days after order confirmation.\n\n"
            "Q: Do you offer free shipping? Yes. Standard shipping is free for all laptop orders in this fictional VoltKart store.\n\n"
            "Q: Can I track my delivery? Order tracking details are not included in this demo."
        ),
    }
    gemini = GeminiService(api_key="")
    answer = gemini.generate_grounded_response(
        user_query="do u offer free shipping",
        intent="support",
        retrieved_docs=[chunk_doc],
    )
    # Must only return the shipping answer, not the delivery duration or tracking answers
    assert "Standard shipping is free" in answer
    assert "3-7 business days" not in answer
    assert "Order tracking" not in answer
