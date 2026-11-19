---
description: "Tasks for Session Duplicate Key Fix and Single Perfect Match Output"
---

# Tasks: Fix Session Duplicate Key & Single Perfect Match Output

## Phase 1: Database Index & Session Creation Fixes
- [X] `T201` In `database.py`, isolate each collection index block in its own `try/except` and drop legacy `session_id_1` indexes on `conversations`.
- [X] `T202` In `backend/conversation_service.py`, set `"session_id": conv_id` on every conversation creation and handle index conflicts.
- [X] `T203` Add automated test `test_create_conversation_handles_legacy_session_id_index` in `tests/test_chat.py`.

## Phase 2: Active Model Endpoint & Cross-Compatibility
- [X] `T204` Update `.env` and `config.py` to use `gemini-3.5-flash-lite` and accept `DATABASE_NAME` or `MONGODB_DATABASE`.
- [X] `T205` Add dynamic model fallback cascade (`gemini-3.5-flash-lite`, `gemini-3.8-flash`) in `backend/gemini_service.py`.

## Phase 3: Single Best Match Output Generation
- [X] `T206` In `backend/retrieval_service.py`, add `SUPPORT_SYNONYMS` and relevance scoring with a minimum threshold ($35.0$).
- [X] `T207` In `backend/gemini_service.py`, enforce the Single Best Direct Answer Rule in the system prompt.
- [X] `T208` In `backend/gemini_service.py`, update `_generate_local_fallback` for `support` to output only the single best match's answer.
- [X] `T209` Add automated test `test_single_best_output_perfect_match` in `tests/test_faq.py`.

## Phase 4: Tabular Column Mapping & Verification
- [X] `T210` Expand `COLUMN_ALIASES` in `backend/file_processor.py` for `store`, `price_inr`, `estimated_battery_hours`, `weight_kg`, `usage_category`.
- [X] `T211` Update `import_data.py` to use the standard validation and ingestion pipeline.
- [X] `T212` Execute test suite and verify 100% pass rate (`pytest tests/`).
