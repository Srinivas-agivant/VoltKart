# Implementation Plan: Interactive AI Shopping Assistant

**Branch**: `006-interactive-ai-chat` | **Date**: 2026-11-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/006-interactive-ai-chat/spec.md`

## Summary

Make the VoltKart AI floating chat deeply interactive, reactive, and conversational:
1. Provide responsive suggestion chips that immediately submit grounded queries.
2. Provide interactive in-chat laptop action buttons ("🔍 Specs", "📊 Compare") inside recommended product tiles.
3. Provide contextual follow-up quick-action prompts (e.g., "📊 Compare Top 2", "🔋 Longest Battery?", "💰 Cheaper Options?").
4. Add chat session controls (clear/restart conversation button, smooth close/open toggle).
5. Support multi-turn contextual references and clean, direct single-answer extraction for policy inquiries.

## Technical Context

**Language/Version**: Python 3.10+ (current environment: Python 3.15)
**Primary Dependencies**: Streamlit, PyMongo, google-genai, Pandas, Pydantic
**Storage**: MongoDB (Atlas) - `voltkart_db` collections (`products`, `conversations`, `faqs`, `policies`, `knowledge_base`)
**Testing**: pytest (`tests/test_chat.py`, `tests/test_faq.py`, `tests/test_recommendation.py`, `tests/test_storefront_ui.py`)
**Target Platform**: Web browsers (desktop, laptop)
**Project Type**: Streamlit Web Application
**Performance Goals**: <2s interactive response time for suggestion chips and in-chat actions
**Constraints**: Zero hallucination, strict MongoDB grounding, Streamlit-first architecture, no page disruption

## Constitution Check

- **I. Frontend Architecture (Streamlit-First)**: PASS - Built entirely within Streamlit components and CSS.
- **II. Backend Processing (Pure Python)**: PASS - All logic in pure Python backend services.
- **III. Primary Storage (MongoDB via PyMongo)**: PASS - Queries live MongoDB collections directly.
- **IV. LLM Integration (Google Gemini API)**: PASS - Intent and response generation via `google-genai` SDK with deterministic local fallbacks.
- **VII. Strict Database Grounding**: PASS - All specifications, prices, and policies sourced from MongoDB.
- **VIII. Zero-Hallucination Policy**: PASS - Strict extraction of verified records; unavailability explained honestly.
- **X. Conversation Memory**: PASS - Multi-turn conversation preserved in Streamlit session state and MongoDB `conversations`.

## Project Structure

### Documentation (this feature)

```text
specs/006-interactive-ai-chat/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Technical analysis and design decisions
├── data-model.md        # Session and conversation entities
├── checklists/
│   └── requirements.md  # Quality checklist
└── tasks.md             # Implementation tasks
```

### Source Code

```text
frontend/
├── floating_chat.py     # Floating chat widget, session state, interactive controls & prompt loop
├── components.py        # Compact in-chat cards with interactive buttons, suggestion chips, comparison
backend/
├── conversation_service.py # Session persistence, title updates, turn history
├── recommendation_service.py # Recommendation filtering & ranking
├── comparison_service.py     # Comparison logic & multi-turn product extraction
├── faq_service.py            # Support & store policy resolution
├── gemini_service.py         # Grounded generation, single-answer extraction
tests/
├── test_chat.py         # Multi-turn memory & conversation tests
└── test_storefront_ui.py # UI component & catalog tests
```
