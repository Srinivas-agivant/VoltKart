# Feature Specification: Fix Session Duplicate Key & Single Perfect Match Output

**Feature Branch**: `003-fix-session-and-single-match`

**Created**: 2026-11-19

**Status**: Draft

**Input**: User description: "fix this also (http://localhost:8501/#stMain) DuplicateKeyError collection: voltkart_db.conversations index: session_id_1 dup key: { session_id: null } and also for each question generate only one best possible ouput based on the perfect match"

---

## 1. Problem Statement & Background

Two key issues were identified during live storefront usage:
1. **DuplicateKeyError on `session_id_1`**: When creating a new conversation in MongoDB (`voltkart_db.conversations`), MongoDB throws `DuplicateKeyError: E11000 duplicate key error ... index: session_id_1 dup key: { session_id: null }`. This occurs because a legacy unique index `session_id_1` exists on the collection, while new conversation records only set `conversation_id`.
2. **Multiple Unfocused Support Outputs**: When a customer asks a support query (e.g. *"do u offer free shipping"*), the system currently returns multiple unrelated FAQ entries (e.g. delivery time, free shipping, and delivery tracking) rather than synthesizing a single direct, authoritative answer focused strictly on the user's specific inquiry.
3. **Model Version Deprecation (404/503)**: `gemini-2.5-flash` was deprecated by Google AI Studio, causing API calls to fall back to local generation. The active supported model `gemini-3.5-flash-lite` should be used with automatic cascade fallbacks.

---

## 2. User Scenarios & Testing *(mandatory)*

### User Story 1 - Frictionless Conversation Creation & Session Persistence (Priority: P1)

As a storefront customer or administrator, I want to start a new chat session or switch conversations without encountering `DuplicateKeyError`, so that my conversation history is reliably saved and retrieved in MongoDB.

**Why this priority**: Crashing on conversation creation prevents any interaction with the AI assistant.

**Independent Test**: Trigger conversation creation via `conv_svc.create_conversation()` repeatedly against a MongoDB database with a legacy `session_id_1` unique index. The operation must succeed cleanly, generate a unique session identifier, and persist without errors.

**Acceptance Scenarios**:
1. **Given** a MongoDB collection with an existing `session_id_1` unique index, **When** a user clicks "➕ New Chat" or initializes the assistant, **Then** `create_conversation` completes successfully without `DuplicateKeyError`.
2. **Given** `DatabaseManager.ensure_indexes()`, **When** the database initializes, **Then** any conflicting legacy `session_id_1` index on `conversations` is safely dropped and superseded by `conversation_id`.

---

### User Story 2 - Single Best Output on Perfect Support Match (Priority: P1)

As a customer inquiring about store policies or shipping, I want the assistant to generate only **one single, best possible output** that directly answers my question based on the perfect database match, rather than listing multiple unrelated store questions or dumping Q&A lists.

**Why this priority**: Returning multiple unrelated FAQs clutters the UI and causes confusion (e.g., asking about free shipping returned questions about delivery times and tracking).

**Independent Test**: Ask *"do u offer free shipping"*. The response must output only the direct policy statement regarding free shipping without listing other delivery FAQs.

**Acceptance Scenarios**:
1. **Given** a customer query like *"do u offer free shipping"*, **When** retrieved from MongoDB, **Then** the single highest-scoring matching record (`FAQ-006`: Free Express Shipping) is identified and answered directly.
2. **Given** either Gemini API mode or local fallback mode, **When** generating the support response, **Then** only the single direct answer is rendered without extraneous `Q: ...` blocks.

---

### User Story 3 - Resilient Gemini Model Pipeline (Priority: P2)

As a user interacting with the AI engine, I want the system to communicate with the active `gemini-3.5-flash-lite` endpoint and automatically handle model unavailability so that responses remain powered by Gemini without failing.

**Why this priority**: Fixes the 404 client error caused by the retired `gemini-2.5-flash` model endpoint.

**Independent Test**: Run live inference with `gemini-3.5-flash-lite`. The model must parse intent and synthesize grounded single-answer outputs.

**Acceptance Scenarios**:
1. **Given** `GEMINI_MODEL=gemini-3.5-flash-lite`, **When** intent classification or response generation runs, **Then** the API call completes successfully.
2. **Given** a 404 or 503 error on a specific model, **When** invoking Gemini, **Then** the service attempts active alternative models before falling back to local deterministic generation.

---

## 3. Requirements

### Functional Requirements
- **FR-001**: `backend/conversation_service.py` must populate both `conversation_id` and `session_id` with unique UUIDs on every conversation creation.
- **FR-002**: `database.py` must inspect `conversations` indexes during `ensure_indexes()` and drop any legacy `session_id_1` index.
- **FR-003**: `backend/retrieval_service.py` must rank retrieved FAQs, policies, and knowledge chunks by calculating an exact phrase and keyword match score against the user query, placing the single best match at index 0.
- **FR-004**: `backend/gemini_service.py` must instruct the LLM to output only the single best answer for the customer query, and `_generate_local_fallback` must output only the single best matching record's answer/description.
- **FR-005**: Update `config.py` and `.env` to use `gemini-3.5-flash-lite` as the primary model.
- **FR-006**: Support `DATABASE_NAME` and `MONGODB_DATABASE` aliases for cross-compatibility with user scripts.

### Non-Functional Requirements
- **NFR-001**: 100% test pass rate across all existing unit tests in `pytest tests/`.
- **NFR-002**: Zero hallucination on unlisted policies or out-of-scope products.
