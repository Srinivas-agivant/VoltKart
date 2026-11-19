# Implementation Plan: Fix Session Duplicate Key & Single Perfect Match Output

**Branch**: `003-fix-session-and-single-match` | **Date**: 2026-11-19 | **Status**: Implemented & Verified

## Summary of Changes

1. **Fix `DuplicateKeyError` on `session_id_1`**:
   - `database.py`: In `ensure_indexes()`, isolate index creation per collection in individual `try...except` blocks and drop conflicting legacy `session_id_1` indexes on `conversations`.
   - `backend/conversation_service.py`: Include `"session_id": conv_id` in every inserted conversation document to guarantee uniqueness across all legacy and current indexes, with fallback index dropping if a collision occurs.

2. **Single Best Match Output Generation**:
   - `backend/retrieval_service.py`: Implemented `SUPPORT_SYNONYMS` (e.g. shipping $\leftrightarrow$ delivery, cost $\leftrightarrow$ charges, refund $\leftrightarrow$ return) and enhanced multi-factor relevance scoring with a minimum relevance threshold ($35.0$) to rank the single most relevant FAQ or policy at index 0.
   - `backend/gemini_service.py`: Updated system prompt grounding rules with the "Single Best Direct Answer Rule" instructing the model to answer only the user's specific question directly.
   - `backend/gemini_service.py`: Updated `_generate_local_fallback` for support queries to output strictly the single best matching answer/description without dumping unrelated Q&A pairs.

3. **Active Model Resilience**:
   - Updated `.env` and `config.py` to use `gemini-3.5-flash-lite`.
   - Implemented dynamic fallback model cascade (`gemini-3.5-flash-lite`, `gemini-3.8-flash`) in `backend/gemini_service.py` to protect against retired model endpoints.

4. **Expanded Tabular Mapping**:
   - `backend/file_processor.py`: Added aliases `store` $\to$ `brand`, `price_inr` $\to$ `price`, `estimated_battery_hours` $\to$ `battery_life`, `weight_kg` $\to$ `weight`, `usage_category` $\to$ `usage_type`.
   - `import_data.py`: Refactored to leverage `DataImporter` and `FileProcessor` with automated validation and deduplication.
