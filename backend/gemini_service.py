"""Gemini AI integration module implementing the Two-Stage Decoupled LLM workflow."""

import json
import logging
from typing import Any, Optional
from google import genai
from google.genai import types

import config
from models.schemas import IntentResult

logger = logging.getLogger("voltkart.gemini")


class GeminiService:
    """Wrapper for Google Gemini API enforcing structured intent output and grounded response generation."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or config.GEMINI_API_KEY
        self.model_name = model_name or config.GEMINI_MODEL
        self.client = None

        if self.api_key and self.api_key != "your_gemini_api_key_here":
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info("Initialized Gemini client with model %s", self.model_name)
            except Exception as e:
                logger.warning("Failed to initialize Gemini client: %s", e)
                self.client = None
        else:
            logger.info("No Gemini API key supplied; operating in deterministic fallback mode.")

    def is_available(self) -> bool:
        """Returns True if the Gemini client is configured."""
        return self.client is not None

    def classify_intent(self, user_query: str, history: Optional[list[dict]] = None) -> dict[str, Any]:
        """Stage 1: Uses Gemini to classify customer intent and extract structured shopping filters.

        Returns:
            dict matching IntentResult schema, or fallback dictionary on failure.
        """
        if not self.client:
            return {"intent": "fallback", "confidence": 0.0}

        history_summary = ""
        if history:
            formatted_turns = [f"{turn.get('role', 'user')}: {turn.get('content', '')}" for turn in history[-4:]]
            history_summary = "Previous Conversation Context:\n" + "\n".join(formatted_turns) + "\n\n"

        prompt = f"""{history_summary}Analyze the following customer message for VoltKart (a specialized laptop store):
Customer Message: "{user_query}"

Classify into one of these intents:
1. 'recommend': Customer looking for laptop recommendations, budget constraints, usage needs, or spec preferences.
2. 'support': Customer asking about store policies (returns, refunds, warranty, shipping, COD) or general FAQs.
3. 'compare': Customer asking to compare laptops (e.g. "compare the first two", "compare VoltBook Pro and IdeaPad 3").
4. 'out_of_scope': Customer asking about non-laptop items (smartphones, TVs, tablets, clothes, general knowledge).
5. 'general': Greetings, thanks, or general pleasantries.

Extract structured parameters into JSON adhering to this structure:
{{
  "intent": "recommend" | "support" | "compare" | "out_of_scope" | "general",
  "requirements": {{
    "budget_max": number or null (e.g. 60000),
    "budget_min": number or null,
    "brand": string or null (e.g. "HP", "Lenovo", "Dell", "VoltKart", "Apple"),
    "usage_type": "student" | "coding" | "gaming" | "business" | "general" or null,
    "min_ram_gb": integer or null (e.g. 16),
    "min_storage_gb": integer or null (e.g. 512),
    "processor_preference": string or null,
    "battery_preference": string or null,
    "weight_preference": string or null
  }},
  "support_query": {{
    "category": "return" | "refund" | "warranty" | "shipping" | "payment" | "general" or null,
    "search_keywords": ["keyword1", "keyword2"]
  }},
  "comparison_targets": {{
    "positions": [1, 2],
    "product_names": ["model 1", "model 2"]
  }},
  "confidence": 0.95
}}
"""
        models_to_try = [self.model_name, "gemini-3.5-flash-lite", "gemini-3.8-flash"]
        unique_models = list(dict.fromkeys(models_to_try))

        last_err = None
        for candidate_model in unique_models:
            try:
                response = self.client.models.generate_content(
                    model=candidate_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.1,
                    ),
                )
                data = json.loads(response.text)
                validated = IntentResult(**data)
                if candidate_model != self.model_name:
                    self.model_name = candidate_model
                return validated.model_dump()
            except Exception as e:
                last_err = e
                logger.warning("Gemini intent classification on %s failed (%s); trying fallback models.", candidate_model, e)

        return {"intent": "fallback", "error": str(last_err), "confidence": 0.0}

    def generate_grounded_response(
        self,
        user_query: str,
        intent: str,
        retrieved_docs: list[dict],
        history: Optional[list[dict]] = None,
        context_notes: str = "",
    ) -> str:
        """Stage 2: Synthesizes a natural, helpful response strictly grounded on retrieved_docs.

        Enforces zero hallucination: if records are empty, explains that information is unavailable.
        """
        if not self.client:
            # Deterministic Python template generator when API key is unset
            return self._generate_local_fallback(user_query, intent, retrieved_docs, context_notes)

        # Prepare clean JSON of retrieved database records (stripping ObjectIds)
        clean_docs = []
        for doc in retrieved_docs:
            d = {k: v for k, v in doc.items() if k not in ["_id", "content_hash"]}
            clean_docs.append(d)

        docs_json = json.dumps(clean_docs, indent=2, default=str)

        history_summary = ""
        if history:
            formatted_turns = [f"{turn.get('role', 'user')}: {turn.get('content', '')}" for turn in history[-4:]]
            history_summary = "Recent Conversation History:\n" + "\n".join(formatted_turns) + "\n\n"

        system_instruction = """You are VoltKart Assistant, a helpful, honest customer support and laptop recommendation expert.

CRITICAL NON-NEGOTIABLE GROUNDING RULES:
1. Single Best Direct Answer Rule: Generate ONLY ONE best possible output answering the customer query directly based on the single best matching verified record. Never output multiple unrelated Q&A pairs, never list multiple FAQs, and never repeat other questions from store records unless explicitly asked.
2. Grounding Rule: Use ONLY the provided verified database records. Do NOT invent product models, prices, specifications, warranty periods, or store policies.
3. Unavailability Rule: If the supplied records list is empty or does not contain the answer, explicitly state that the information or matching product is unavailable in VoltKart's catalog. Offer relevant alternatives or ask the user to adjust their criteria.
4. Pricing & Specs Rule: When stating any price or specification, quote the exact figures from the records.
5. Scope Rule: If the user asks about smartphones, TVs, tablets, or non-laptop items, politely explain that VoltKart exclusively sells laptops and related accessories.
6. Tone: Be professional, friendly, clear, and direct. Format responses cleanly.
"""

        user_content = f"""{history_summary}Customer Query: "{user_query}"
Classified Intent: {intent}
{f"Context Notes: {context_notes}" if context_notes else ""}

VERIFIED DATABASE RECORDS RETRIEVED FROM MONGODB:
{docs_json}

Provide your grounded response following all critical grounding rules."""

        models_to_try = [self.model_name, "gemini-3.5-flash-lite", "gemini-3.8-flash"]
        unique_models = list(dict.fromkeys(models_to_try))

        for candidate_model in unique_models:
            try:
                response = self.client.models.generate_content(
                    model=candidate_model,
                    contents=user_content,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.2,
                    ),
                )
                if candidate_model != self.model_name:
                    self.model_name = candidate_model
                return response.text.strip()
            except Exception as e:
                logger.warning("Gemini model %s call failed (%s); trying alternatives.", candidate_model, e)

        return self._generate_local_fallback(user_query, intent, retrieved_docs, context_notes)

    def _generate_local_fallback(
        self, user_query: str, intent: str, retrieved_docs: list[dict], context_notes: str = ""
    ) -> str:
        """Deterministic local response generator used when Gemini API is unavailable or rate-limited."""
        if intent == "recommend":
            if not retrieved_docs:
                return (
                    "I searched our catalog, but unfortunately no laptops match your exact criteria. "
                    "Try increasing your budget or relaxing your hardware requirements."
                )
            lines = [f"Here are {len(retrieved_docs)} matching laptops from our verified catalog:\n"]
            for i, p in enumerate(retrieved_docs, start=1):
                reason = p.get("recommendation_reason", "Strong fit for your specifications.")
                lines.append(
                    f"**{i}. {p.get('name')}** - ₹{p.get('price', 0):,.0f}\n"
                    f"- **Processor**: {p.get('processor')}\n"
                    f"- **RAM & Storage**: {p.get('ram')} | {p.get('storage')}\n"
                    f"- **Display & Graphics**: {p.get('display')} | {p.get('graphics')}\n"
                    f"- **Battery & Weight**: {p.get('battery_life')} | {p.get('weight')}\n"
                    f"- **Why this fits**: {reason}\n"
                )
            return "\n".join(lines)

        elif intent == "support":
            if not retrieved_docs:
                return (
                    "I checked our store knowledge base, but information regarding this query is currently unavailable. "
                    "Please contact our customer support team at support@voltkart.com or toll-free at 1800-VOLT-KART."
                )
            # Generate ONLY ONE best possible output based on the perfect match
            best_doc = retrieved_docs[0]
            if "answer" in best_doc:
                return best_doc.get("answer", "").strip()
            elif "description" in best_doc:
                return best_doc.get("description", "").strip()
            elif "chunk_text" in best_doc:
                return self._extract_best_answer_from_chunk(user_query, best_doc.get("chunk_text", ""))
            return "Here is the verified information from our store records."

        elif intent == "compare":
            if not retrieved_docs:
                return "I couldn't find the products you wanted to compare. Please ask for recommendations first."
            lines = [f"### Comparing {len(retrieved_docs)} Laptops:\n"]
            for p in retrieved_docs:
                lines.append(
                    f"**{p.get('name')}** (₹{p.get('price', 0):,.0f}): "
                    f"{p.get('processor')}, {p.get('ram')}, {p.get('storage')}, {p.get('battery_life')}"
                )
            return "\n".join(lines)

        elif intent == "out_of_scope":
            return (
                "VoltKart specializes exclusively in laptop computers, workstations, and laptop accessories. "
                "We do not sell smartphones, tablets, or other consumer electronics. "
                "Can I help you find a great laptop today?"
            )

        return (
            "Welcome to VoltKart! I am your AI assistant for laptop recommendations and store support. "
            "How can I help you today? You can ask for laptops within a budget, compare models, or check store policies."
        )

    def _extract_best_answer_from_chunk(self, query: str, chunk_text: str) -> str:
        """Extracts the single most relevant Q&A block or answer from a multi-item knowledge chunk."""
        import re

        clean_text = chunk_text.strip()
        if not clean_text:
            return "Here is the verified information from our store records."

        # Split on lines beginning with 'Q:' or blank lines
        blocks = [b.strip() for b in re.split(r"(?=(?:^|\n)\s*Q:)", clean_text, flags=re.IGNORECASE) if b.strip()]
        if not blocks or len(blocks) == 1:
            # Fallback to paragraph splitting if no Q: blocks
            blocks = [p.strip() for p in re.split(r"(?:\r?\n){2,}", clean_text) if p.strip()]

        if not blocks:
            return clean_text

        query_words = set(re.findall(r"\w+", query.lower())) - {"do", "you", "u", "the", "a", "an", "is", "are", "what"}
        if not query_words:
            query_words = set(re.findall(r"\w+", query.lower()))

        scored_blocks: list[tuple[float, str]] = []
        for b in blocks:
            b_words = set(re.findall(r"\w+", b.lower()))
            overlap = len(query_words & b_words)
            scored_blocks.append((overlap, b))

        scored_blocks.sort(key=lambda x: x[0], reverse=True)
        best_block = scored_blocks[0][1]

        # Extract answer part if structured as 'Q: ...? <Answer>'
        q_match = re.search(r"Q:\s*.*?\?\s*(.+)", best_block, re.DOTALL | re.IGNORECASE)
        if q_match:
            return q_match.group(1).strip()

        return best_block.strip()
