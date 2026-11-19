"""Data retrieval service executing PyMongo queries and deterministic ranking."""

import re
from typing import Any, Optional
import config
from database import get_db


SUPPORT_SYNONYMS: dict[str, set[str]] = {
    "shipping": {"delivery", "courier", "dispatch", "ship", "freight"},
    "delivery": {"shipping", "courier", "dispatch", "ship", "freight"},
    "free": {"zero", "complimentary", "included", "no charge"},
    "cost": {"charges", "fee", "price", "pricing", "charge", "rate"},
    "charges": {"cost", "fee", "price", "pricing", "charge", "rate"},
    "fee": {"charges", "cost", "price", "rate"},
    "return": {"refund", "replacement", "exchange", "send back"},
    "refund": {"return", "replacement", "exchange", "money back"},
    "warranty": {"guarantee", "protection", "voltcare", "coverage"},
    "cod": {"cash on delivery", "pay on delivery"},
}


class RetrievalService:
    """Manages Python-driven queries against MongoDB for products, FAQs, and policies."""

    def __init__(self, db=None):
        self.db = db if db is not None else get_db()

    def get_recommendations(self, requirements: Optional[dict[str, Any]] = None, limit: int = 3) -> list[dict]:
        """Queries products in MongoDB based on budget and spec filters, applying deterministic Python scoring."""
        if requirements is None:
            requirements = {}

        query_filter: dict[str, Any] = {}

        # 1. Budget Filter
        budget_max = requirements.get("budget_max")
        budget_min = requirements.get("budget_min")
        if budget_max is not None or budget_min is not None:
            price_sub: dict[str, Any] = {}
            if budget_max is not None:
                price_sub["$lte"] = float(budget_max)
            if budget_min is not None:
                price_sub["$gte"] = float(budget_min)
            query_filter["price"] = price_sub

        # 2. Brand Filter
        brand = requirements.get("brand")
        if brand:
            query_filter["brand"] = {"$regex": f"^{re.escape(brand)}$", "$options": "i"}

        # 3. Usage Type Filter
        usage_type = requirements.get("usage_type")
        if usage_type and usage_type != "general":
            query_filter["usage_type"] = usage_type

        # 4. RAM and Storage Filters
        min_ram = requirements.get("min_ram_gb")
        if min_ram:
            query_filter["ram_gb"] = {"$gte": int(min_ram)}

        min_storage = requirements.get("min_storage_gb")
        if min_storage:
            query_filter["storage_gb"] = {"$gte": int(min_storage)}

        products_coll = self.db[config.COLLECTION_PRODUCTS]
        candidates = list(products_coll.find(query_filter, {"_id": 0}))

        # If strict filter returned empty and usage_type or brand was set, relax usage/brand while maintaining budget
        if not candidates and (usage_type or brand):
            relaxed_filter = {}
            if "price" in query_filter:
                relaxed_filter["price"] = query_filter["price"]
            if min_ram:
                relaxed_filter["ram_gb"] = {"$gte": int(min_ram)}
            candidates = list(products_coll.find(relaxed_filter, {"_id": 0}))

        # If still empty and no filter, return top laptops
        if not candidates and not query_filter:
            candidates = list(products_coll.find({}, {"_id": 0}).limit(10))

        if not candidates:
            return []

        # Deterministic Python Scoring
        scored_candidates = []
        target_budget = float(budget_max) if budget_max else None

        for p in candidates:
            score = 0.0
            p["name"] = p.get("name") or p.get("model") or "VoltKart Laptop"
            p["price"] = float(p.get("price") or p.get("price_inr") or 0.0)
            price = p["price"]

            # Budget proximity score (rewards maximizing hardware value within budget)
            if target_budget and price <= target_budget and target_budget > 0:
                proximity_ratio = price / target_budget
                score += 40.0 * proximity_ratio

            # RAM score
            ram_gb = p.get("ram_gb", 8)
            if min_ram and ram_gb >= min_ram:
                score += 25.0
            elif ram_gb >= 16:
                score += 15.0

            # Storage score
            storage_gb = p.get("storage_gb", 256)
            if storage_gb >= 1024:
                score += 20.0
            elif storage_gb >= 512:
                score += 10.0

            # Usage type match
            if usage_type and p.get("usage_type") == usage_type:
                score += 25.0

            # Battery bonus
            if p.get("battery_hours", 0) >= 8.0:
                score += 10.0

            # Generate individualized recommendation rationale
            reasons = []
            if target_budget:
                reasons.append(f"Fits within your ₹{target_budget:,.0f} budget at ₹{price:,.0f}")
            if usage_type:
                reasons.append(f"optimized for {usage_type}")
            if ram_gb >= 16:
                reasons.append(f"{ram_gb}GB high-speed memory")
            if p.get("battery_hours", 0) >= 8.0:
                reasons.append(f"extended {p.get('battery_life')} battery")

            rationale = "; ".join(reasons) if reasons else "Balanced performance and reliable build."
            p["recommendation_reason"] = rationale
            scored_candidates.append((score, p))

        # Sort descending by score
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_candidates[:limit]]

    def get_support_answers(self, query: str, category: Optional[str] = None) -> list[dict]:
        """Retrieves matching FAQ and store policy documents from MongoDB, ranking best match first."""
        lower_q = query.lower().strip()
        query_words = [w for w in re.findall(r"\w+", lower_q) if len(w) > 2]
        expanded_query_words = set(query_words)
        for w in query_words:
            expanded_query_words |= SUPPORT_SYNONYMS.get(w, set())

        expanded_cats = set()
        if category:
            cat_l = category.lower()
            expanded_cats = {cat_l} | SUPPORT_SYNONYMS.get(cat_l, set())

        scored_candidates: list[tuple[float, dict]] = []

        faqs_coll = self.db[config.COLLECTION_FAQS]
        policies_coll = self.db[config.COLLECTION_POLICIES]
        kb_coll = self.db[config.COLLECTION_KNOWLEDGE_BASE]

        def _score_doc(doc: dict) -> float:
            score = 0.0
            q_text = doc.get("question", "").lower()
            ans_text = doc.get("answer", "").lower()
            title_text = doc.get("title", "").lower()
            desc_text = doc.get("description", "").lower()
            chunk_text = doc.get("chunk_text", "").lower()
            doc_cat = doc.get("category", "").lower()

            raw_kw = doc.get("keywords", [])
            if isinstance(raw_kw, str):
                keywords = [k.strip().lower() for k in raw_kw.replace(";", ",").split(",") if k.strip()]
            elif isinstance(raw_kw, list):
                keywords = [str(k).strip().lower() for k in raw_kw if str(k).strip()]
            else:
                keywords = []

            # 1. Exact phrase in question or title (+60)
            if q_text and lower_q in q_text:
                score += 60.0
            if title_text and lower_q in title_text:
                score += 60.0

            # 2. Keyword exact matches in query (+40 each)
            for kw in keywords:
                if kw and (kw in lower_q or lower_q in kw):
                    score += 40.0
                elif kw and all(part in expanded_query_words for part in kw.split()):
                    score += 30.0

            # 3. Word matches in question/title (+15 direct, +10 synonym)
            for w in query_words:
                if w in q_text or w in title_text:
                    score += 15.0
            for w in expanded_query_words:
                if w not in query_words and (w in q_text or w in title_text):
                    score += 10.0

            # 4. Free shipping / delivery bonus
            if "free" in query_words and ("free" in q_text or any("free" in kw for kw in keywords)):
                score += 35.0

            # 5. Category match (+15)
            if doc_cat:
                if doc_cat in query_words or (category and doc_cat in expanded_cats):
                    score += 15.0

            # 6. Content match in answer / description / chunk (+5 per word)
            content = ans_text or desc_text or chunk_text
            for w in query_words:
                if w in content:
                    score += 5.0

            return score

        # 1. Search policies
        all_policies = list(policies_coll.find({}, {"_id": 0}))
        for pol in all_policies:
            s = _score_doc(pol)
            if s >= 35.0:
                scored_candidates.append((s, pol))

        # 2. Search FAQs
        all_faqs = list(faqs_coll.find({}, {"_id": 0}))
        for faq in all_faqs:
            s = _score_doc(faq)
            if s >= 35.0:
                scored_candidates.append((s, faq))

        # 3. Search Knowledge Base (PDF Chunks)
        all_chunks = list(kb_coll.find({}, {"_id": 0}).limit(100))
        for chk in all_chunks:
            s = _score_doc(chk)
            if s >= 35.0:
                scored_candidates.append((s, chk))

        # Sort descending by score
        scored_candidates.sort(key=lambda x: x[0], reverse=True)

        # Deduplicate results by ID while preserving ranking
        unique_results = []
        seen_ids = set()
        for score_val, r in scored_candidates:
            rid = r.get("faq_id") or r.get("policy_id") or r.get("chunk_id")
            if rid not in seen_ids:
                seen_ids.add(rid)
                unique_results.append(r)

        return unique_results[:3]

    def resolve_comparison_products(
        self,
        conversation_id: str,
        positions: Optional[list[int]] = None,
        product_names: Optional[list[str]] = None,
    ) -> list[dict]:
        """Resolves target products to compare using positions or named models."""
        products_coll = self.db[config.COLLECTION_PRODUCTS]
        resolved_products: list[dict] = []

        # Case 1: Resolve by ordinal positions from conversation recommendations
        if positions and conversation_id:
            recs_coll = self.db[config.COLLECTION_RECOMMENDATIONS]
            # Find recommendations for this conversation ordered by latest first
            recs = list(
                recs_coll.find({"conversation_id": conversation_id, "position": {"$in": positions}})
                .sort("created_at", -1)
            )

            # Map positions to unique latest product_id
            pos_to_id: dict[int, str] = {}
            for r in recs:
                pos = r.get("position")
                if pos in positions and pos not in pos_to_id:
                    pos_to_id[pos] = r.get("product_id")

            for pos in sorted(positions):
                pid = pos_to_id.get(pos)
                if pid:
                    prod = products_coll.find_one({"product_id": pid}, {"_id": 0})
                    if prod:
                        resolved_products.append(prod)

        # Case 2: Resolve by product names
        if product_names:
            for name in product_names:
                clean_name = name.strip()
                if clean_name:
                    prod = products_coll.find_one(
                        {"name": {"$regex": re.escape(clean_name), "$options": "i"}}, {"_id": 0}
                    )
                    if prod and prod not in resolved_products:
                        resolved_products.append(prod)

        # If only 1 or 0 resolved, and conversation had recommendations, default to first 2
        if len(resolved_products) < 2 and conversation_id:
            recs_coll = self.db[config.COLLECTION_RECOMMENDATIONS]
            recent_recs = list(
                recs_coll.find({"conversation_id": conversation_id})
                .sort("created_at", -1)
                .limit(3)
            )
            for r in recent_recs:
                pid = r.get("product_id")
                prod = products_coll.find_one({"product_id": pid}, {"_id": 0})
                if prod and prod not in resolved_products:
                    resolved_products.append(prod)
                if len(resolved_products) == 2:
                    break

        return resolved_products
