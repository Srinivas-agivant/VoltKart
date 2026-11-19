"""Tests for product recommendation, budget filtering, and deterministic ranking."""

import mongomock
import pytest

from backend.retrieval_service import RetrievalService
from backend.gemini_service import GeminiService
from backend.recommendation_service import RecommendationService


@pytest.fixture
def populated_mock_db():
    db = mongomock.MongoClient()["test_db"]
    sample_products = [
        {
            "product_id": "VK-01",
            "name": "VoltBook Air 13",
            "brand": "VoltKart",
            "price": 38999.0,
            "processor": "Intel i3",
            "ram": "8GB",
            "ram_gb": 8,
            "storage": "256GB SSD",
            "storage_gb": 256,
            "battery_hours": 9.5,
            "usage_type": "student",
        },
        {
            "product_id": "VK-02",
            "name": "VoltBook Pro 15",
            "brand": "VoltKart",
            "price": 54999.0,
            "processor": "Intel i5",
            "ram": "16GB",
            "ram_gb": 16,
            "storage": "512GB SSD",
            "storage_gb": 512,
            "battery_hours": 7.5,
            "usage_type": "coding",
        },
        {
            "product_id": "VK-03",
            "name": "VoltStrike Gaming 15",
            "brand": "VoltKart",
            "price": 62999.0,
            "processor": "Intel i5",
            "ram": "16GB",
            "ram_gb": 16,
            "storage": "512GB SSD",
            "storage_gb": 512,
            "battery_hours": 5.5,
            "usage_type": "gaming",
        },
        {
            "product_id": "VK-04",
            "name": "VoltStrike Pro",
            "brand": "VoltKart",
            "price": 84999.0,
            "processor": "AMD Ryzen 7",
            "ram": "16GB",
            "ram_gb": 16,
            "storage": "1TB SSD",
            "storage_gb": 1024,
            "battery_hours": 5.0,
            "usage_type": "gaming",
        },
    ]
    db["products"].insert_many(sample_products)
    return db


def test_budget_filtering_and_ranking(populated_mock_db):
    """Verify that laptops exceeding budget are excluded and top candidates are ranked."""
    retrieval = RetrievalService(db=populated_mock_db)
    recs = retrieval.get_recommendations({"budget_max": 60000.0, "usage_type": "coding"}, limit=3)

    assert len(recs) > 0
    # Highest budget items (84999, 62999) must not be in recs
    for p in recs:
        assert p["price"] <= 60000.0

    # VoltBook Pro 15 (54999, coding) should be ranked first
    assert recs[0]["product_id"] == "VK-02"
    assert "recommendation_reason" in recs[0]


def test_no_matching_products(populated_mock_db):
    """Verify empty result when criteria cannot be fulfilled."""
    retrieval = RetrievalService(db=populated_mock_db)
    recs = retrieval.get_recommendations({"budget_max": 20000.0}, limit=3)
    assert len(recs) == 0


def test_zero_hallucination_on_empty_products():
    """Verify that when no products are retrieved, Gemini service states unavailability."""
    gemini = GeminiService(api_key="")  # Local fallback
    ans = gemini.generate_grounded_response(
        user_query="Show me laptops under 20k",
        intent="recommend",
        retrieved_docs=[],
    )
    assert "unfortunately no laptops match" in ans.lower() or "unavailable" in ans.lower()
