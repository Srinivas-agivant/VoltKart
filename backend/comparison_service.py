"""Product comparison orchestration service."""

from typing import Any, Optional
from backend.gemini_service import GeminiService
from backend.retrieval_service import RetrievalService


class ComparisonService:
    """Resolves ordinal laptop references ('first two') and builds comparative evaluations."""

    def __init__(
        self,
        retrieval_service: Optional[RetrievalService] = None,
        gemini_service: Optional[GeminiService] = None,
    ):
        self.retrieval_service = retrieval_service or RetrievalService()
        self.gemini_service = gemini_service or GeminiService()

    def process_comparison(
        self,
        user_query: str,
        conversation_id: str,
        intent_data: dict[str, Any],
        history: Optional[list[dict]] = None,
    ) -> dict[str, Any]:
        """Resolves target products from previous conversation turns and generates grounded verdicts."""
        targets = intent_data.get("comparison_targets") or {}
        positions = targets.get("positions") or [1, 2]
        product_names = targets.get("product_names") or []

        # 1. Resolve exact products from MongoDB
        products_to_compare = self.retrieval_service.resolve_comparison_products(
            conversation_id=conversation_id,
            positions=positions,
            product_names=product_names,
        )

        # 2. Generate Grounded AI Verdict
        response_text = self.gemini_service.generate_grounded_response(
            user_query=user_query,
            intent="compare",
            retrieved_docs=products_to_compare,
            history=history,
            context_notes=f"Comparison between {len(products_to_compare)} products.",
        )

        return {
            "response_text": response_text,
            "products": products_to_compare,
            "intent": "compare",
            "retrieved_ids": [p.get("product_id") for p in products_to_compare],
        }
