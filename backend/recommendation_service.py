"""Product recommendation orchestration service."""

from typing import Any, Optional
from backend.gemini_service import GeminiService
from backend.retrieval_service import RetrievalService
from backend.conversation_service import ConversationService


class RecommendationService:
    """Orchestrates structured recommendation queries, ranking, and grounded response synthesis."""

    def __init__(
        self,
        retrieval_service: Optional[RetrievalService] = None,
        gemini_service: Optional[GeminiService] = None,
        conversation_service: Optional[ConversationService] = None,
    ):
        self.retrieval_service = retrieval_service or RetrievalService()
        self.gemini_service = gemini_service or GeminiService()
        self.conversation_service = conversation_service or ConversationService()

    def process_recommendation(
        self,
        user_query: str,
        conversation_id: str,
        intent_data: dict[str, Any],
        history: Optional[list[dict]] = None,
    ) -> dict[str, Any]:
        """Filters catalog products, ranks top candidates in Python, and generates grounded explanations."""
        requirements = intent_data.get("requirements") or {}

        # 1. Retrieve & Rank Products from MongoDB
        recommended_products = self.retrieval_service.get_recommendations(requirements, limit=3)

        # 2. Save Positions in Conversation Memory for Relative Follow-Up Referencing
        if recommended_products and conversation_id:
            self.conversation_service.save_recommendations(conversation_id, recommended_products)

        # 3. Generate Grounded AI Explanation using ONLY retrieved products
        response_text = self.gemini_service.generate_grounded_response(
            user_query=user_query,
            intent="recommend",
            retrieved_docs=recommended_products,
            history=history,
            context_notes=f"Target requirements: {requirements}",
        )

        return {
            "response_text": response_text,
            "products": recommended_products,
            "intent": "recommend",
            "retrieved_ids": [p.get("product_id") for p in recommended_products],
        }
