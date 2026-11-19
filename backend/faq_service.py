"""Customer support FAQ and store policy resolver service."""

from typing import Any, Optional
from backend.gemini_service import GeminiService
from backend.retrieval_service import RetrievalService


class FaqService:
    """Retrieves verified store FAQs and policies and synthesizes grounded answers."""

    def __init__(
        self,
        retrieval_service: Optional[RetrievalService] = None,
        gemini_service: Optional[GeminiService] = None,
    ):
        self.retrieval_service = retrieval_service or RetrievalService()
        self.gemini_service = gemini_service or GeminiService()

    def process_support(
        self,
        user_query: str,
        intent_data: dict[str, Any],
        history: Optional[list[dict]] = None,
    ) -> dict[str, Any]:
        """Queries FAQs and policies in MongoDB, strictly adhering to zero-hallucination policy."""
        support_info = intent_data.get("support_query") or {}
        category = support_info.get("category")

        # 1. Retrieve matching documents from MongoDB
        retrieved_docs = self.retrieval_service.get_support_answers(query=user_query, category=category)

        # 2. Synthesize grounded answer
        response_text = self.gemini_service.generate_grounded_response(
            user_query=user_query,
            intent="support",
            retrieved_docs=retrieved_docs,
            history=history,
            context_notes="Customer support policy inquiry.",
        )

        doc_ids = [d.get("faq_id") or d.get("policy_id") for d in retrieved_docs if d.get("faq_id") or d.get("policy_id")]

        return {
            "response_text": response_text,
            "documents": retrieved_docs,
            "intent": "support",
            "retrieved_ids": doc_ids,
        }
