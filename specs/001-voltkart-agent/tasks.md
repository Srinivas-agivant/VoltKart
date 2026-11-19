---
description: "Task list for VoltKart AI Customer Support & Product Recommendation Agent"
---

# Tasks: VoltKart AI Agent

**Input**: Design documents from `/specs/001-voltkart-agent/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/, research.md, quickstart.md

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Parallelizable task
- **[Story]**: Associated user story (US1: Recommendations, US2: Support/FAQ, US3: Admin Ingestion, US4: Multi-Turn Comparison, US5: Scope Enforcement)

---

## Phase 1: Setup & Shared Infrastructure

- [X] `T001` Initialize project dependencies in `requirements.txt` (`streamlit`, `pymongo`, `pandas`, `openpyxl`, `google-genai`, `pydantic`, `python-dotenv`, `pytest`)
- [X] `T002` [P] Create `.env.example` and `.gitignore` for Python, Streamlit, and environment secrets
- [X] `T003` Implement application configuration loader in `config.py` loading `MONGODB_URI`, `DATABASE_NAME`, `GEMINI_API_KEY`, and `GEMINI_MODEL` with validation

---

## Phase 2: Foundational Data & Storage

- [X] `T004` Define Pydantic models in `models/schemas.py` for `Product`, `FAQ`, `StorePolicy`, `IntentResult`, and `ImportSummary`
- [X] `T005` Implement PyMongo database client, collection accessors, and index creation in `database.py` for all 7 collections
- [X] `T006` [P] Generate 25 synthetic fictional laptop catalog records in `data/sample_products.csv`
- [X] `T007` [P] Generate 15 synthetic customer support FAQs in `data/sample_faqs.csv`
- [X] `T008` [P] Generate synthetic return, warranty, and shipping policies in `data/sample_policies.csv`

---

## Phase 3: User Story 3 - Admin Data Ingestion & Validation (P2)

- [X] `T009` [US3] Implement `FileProcessor` in `backend/file_processor.py` for `.csv`, `.xlsx`, and `.xls` parsing with dynamic column alias mapping
- [X] `T010` [US3] Implement `DataValidator` in `backend/data_validator.py` for row cleaning, numeric coercion, Pydantic validation, and MD5 content hashing
- [X] `T011` [US3] Implement `DataImporter` in `backend/data_importer.py` supporting "skip" vs "update" duplicate handling and audit logging in `import_history`
- [X] `T012` [US3] Implement Streamlit admin view in `frontend/admin_dashboard.py` with file uploader, category selector, column mapping dropdowns, preview table, and import summary cards
- [X] `T013` [US3] Create automated ingestion tests in `tests/test_import.py` verifying CSV/Excel parsing, validation error handling, and duplicate skips

---

## Phase 4: User Story 1 - Personalized Laptop Recommendations (P1)

- [X] `T014` [US1] Implement `GeminiService` in `backend/gemini_service.py` for Stage 1 JSON intent extraction and Stage 2 grounded response synthesis with timeout and exception handling
- [X] `T015` [US1] Implement `IntentService` in `backend/intent_service.py` with structured schema enforcement and regex keyword fallback on Gemini failure
- [X] `T016` [US1] Implement `RetrievalService` in `backend/retrieval_service.py` to filter products by budget/specs and apply deterministic Python scoring
- [X] `T017` [US1] Implement `RecommendationService` in `backend/recommendation_service.py` coordinating intent parsing, PyMongo retrieval, ranking, and grounded Gemini explanation generation
- [X] `T018` [US1] Implement product recommendation card UI in `frontend/components.py` displaying price, specs, warranty, and recommendation rationale
- [X] `T019` [US1] Create recommendation tests in `tests/test_recommendation.py` testing budget filtering, deterministic ranking, and no-match scenarios

---

## Phase 5: User Story 2 - Store Policy & FAQ Support (P1)

- [X] `T020` [US2] Implement `FaqService` in `backend/faq_service.py` to query MongoDB `faqs` and `store_policies` via text search and category filters
- [X] `T021` [US2] Enforce strict anti-hallucination prompt in `GeminiService.generate_grounded_response` so unlisted questions return honest "information unavailable" responses
- [X] `T022` [US2] Create FAQ and policy tests in `tests/test_faq.py` verifying documented policy retrieval and non-hallucination on unlisted queries

---

## Phase 6: User Story 4 - Multi-Turn Comparison & Follow-Up Context (P2)

- [X] `T023` [US4] Implement `ConversationService` in `backend/conversation_service.py` to persist conversations, message turns, and recommended product positions in MongoDB
- [X] `T024` [US4] Implement `ComparisonService` in `backend/comparison_service.py` to resolve ordinal positions ("compare the first two") against MongoDB and build side-by-side spec comparison tables
- [X] `T025` [US4] Implement comparison table UI component in `frontend/components.py` rendering attributes side-by-side with an objective verdict
- [X] `T026` [US4] Implement chat timeline in `frontend/chat_interface.py` with multi-turn message history, suggestion chips, and responsive input
- [X] `T027` [US4] Create conversation tests in `tests/test_chat.py` verifying session persistence and relative ordinal reference resolution

---

## Phase 7: User Story 5 - Store Scope Enforcement & UI Integration (P3)

- [X] `T028` [US5] Implement out-of-scope intent handling in `backend/intent_service.py` politely redirecting non-laptop queries to laptop inquiries
- [X] `T029` Build main Streamlit application entry point in `app.py` with branded header, sidebar navigation, "+ New Chat" button, and conversation session switcher
- [X] `T030` Wire error banners and degraded mode notices for rate-limited API fallback in `frontend/chat_interface.py`

---

## Phase 8: Polish, Test Suite Execution & Documentation

- [X] `T031` Run and pass the complete automated test suite (`pytest tests/`)
- [X] `T032` Ingest synthetic datasets (`data/sample_products.csv`, `data/sample_faqs.csv`, `data/sample_policies.csv`) into MongoDB
- [X] `T033` Write comprehensive `README.md` with architecture diagrams, setup instructions, and demo script
