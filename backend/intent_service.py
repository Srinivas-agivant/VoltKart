"""Intent classification service coordinating Gemini Stage 1 and deterministic regex fallback."""

import re
from typing import Any, Optional

from backend.gemini_service import GeminiService
from models.schemas import IntentResult, RequirementsFilter, SupportQueryFilter, ComparisonTargets


class IntentService:
    """Classifies user intent and extracts structured parameters using Gemini with regex fallback."""

    def __init__(self, gemini_service: Optional[GeminiService] = None):
        self.gemini_service = gemini_service or GeminiService()

    def parse_intent(self, user_query: str, history: Optional[list[dict]] = None) -> dict[str, Any]:
        """Main intent classification entry point."""
        # 1. Fast pre-check for blatant out-of-scope non-laptop queries
        lower_q = user_query.lower()
        non_laptop_keywords = ["phone", "smartphone", "iphone", "samsung galaxy", "android", "ipad", "tablet", "television", "tv", "smartwatch", "refrigerator"]
        if any(w in lower_q for w in non_laptop_keywords) and "laptop" not in lower_q:
            return {
                "intent": "out_of_scope",
                "requirements": None,
                "support_query": None,
                "comparison_targets": None,
                "confidence": 1.0,
            }

        # 2. Attempt Gemini Stage 1 structured intent extraction
        if self.gemini_service.is_available():
            result = self.gemini_service.classify_intent(user_query, history)
            if result.get("intent") != "fallback":
                return result

        # 3. Deterministic Regex / Rule-based Fallback
        return self._regex_intent_parser(user_query)

    def _regex_intent_parser(self, query: str) -> dict[str, Any]:
        """Rule-based extractor used when Gemini is unconfigured or rate-limited."""
        lower_q = query.lower()

        # Check compare
        if any(w in lower_q for w in ["compare", "vs", "versus", "difference", "better between"]):
            positions = []
            if "first two" in lower_q or "top two" in lower_q or "1 and 2" in lower_q:
                positions = [1, 2]
            elif "first and third" in lower_q or "1 and 3" in lower_q:
                positions = [1, 3]
            elif "second and third" in lower_q or "2 and 3" in lower_q:
                positions = [2, 3]
            else:
                pos_matches = re.findall(r"\b(first|second|third|1st|2nd|3rd)\b", lower_q)
                pos_map = {"first": 1, "1st": 1, "second": 2, "2nd": 2, "third": 3, "3rd": 3}
                positions = [pos_map[p] for p in pos_matches if p in pos_map]

            return {
                "intent": "compare",
                "requirements": None,
                "support_query": None,
                "comparison_targets": {"positions": positions, "product_names": []},
                "confidence": 0.85,
            }

        # Check support
        support_categories = {
            "return": ["return", "exchange", "replacement"],
            "refund": ["refund", "money back"],
            "warranty": ["warranty", "guarantee", "repair", "service center", "voltcare"],
            "shipping": ["shipping", "delivery", "dispatch", "arrive", "charges", "courier", "cod", "cash on delivery"],
            "payment": ["payment", "upi", "card", "emi", "net banking"],
        }
        for cat, keywords in support_categories.items():
            if any(k in lower_q for k in keywords):
                return {
                    "intent": "support",
                    "requirements": None,
                    "support_query": {"category": cat, "search_keywords": [k for k in keywords if k in lower_q]},
                    "comparison_targets": None,
                    "confidence": 0.85,
                }

        # Check recommend
        recommend_indicators = [
            "laptop", "suggest", "recommend", "show", "buy", "under", "budget", "best", "gaming", "coding", "student", "college", "work", "gb", "ram", "ssd"
        ]
        if any(ind in lower_q for ind in recommend_indicators):
            reqs = RequirementsFilter()

            # Extract budget
            # Matches "under 60000", "under 60k", "below 75,000", "budget 50000"
            budget_match = re.search(r"(?:under|below|budget|within|around)\s*(?:rs\.?|inr|₹)?\s*(\d+)(?:\s*(k|thousand))?", lower_q)
            if budget_match:
                amount = float(budget_match.group(1))
                if budget_match.group(2) or amount < 500:
                    amount *= 1000
                reqs.budget_max = amount

            # Extract brand
            for b in ["apple", "dell", "hp", "lenovo", "asus", "voltkart"]:
                if b in lower_q:
                    reqs.brand = b.capitalize() if b != "hp" else "HP"
                    break

            # Extract usage
            if any(w in lower_q for w in ["game", "gaming", "gpu"]):
                reqs.usage_type = "gaming"
            elif any(w in lower_q for w in ["code", "coding", "developer", "programming", "python"]):
                reqs.usage_type = "coding"
            elif any(w in lower_q for w in ["student", "college", "study", "school"]):
                reqs.usage_type = "student"
            elif any(w in lower_q for w in ["business", "office", "work"]):
                reqs.usage_type = "business"

            # Extract RAM
            ram_match = re.search(r"(\d+)\s*(?:gb|gigabyte)?\s*ram", lower_q)
            if ram_match:
                reqs.min_ram_gb = int(ram_match.group(1))

            return {
                "intent": "recommend",
                "requirements": reqs.model_dump(),
                "support_query": None,
                "comparison_targets": None,
                "confidence": 0.8,
            }

        return {
            "intent": "general",
            "requirements": None,
            "support_query": None,
            "comparison_targets": None,
            "confidence": 0.7,
        }
