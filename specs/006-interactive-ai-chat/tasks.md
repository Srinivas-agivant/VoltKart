# Implementation Tasks: Interactive AI Shopping Assistant

## Phase 1: Setup & Prerequisite Verification

- [X] T01: Verify MongoDB connection, collection counts, and test environment. `tests/test_chat.py`

## Phase 2: Tests First (TDD)

- [X] T02: Add unit test for session reset and interactive pending prompt state in `tests/test_chat.py`.
- [X] T03: Add unit test verifying precise support policy answer extraction from multi-sentence chunks in `tests/test_faq.py`.

## Phase 3: Core Implementation

- [X] T04: Enhance `backend/gemini_service.py` fallback and prompt logic to extract the precise single matching answer from multi-sentence FAQ/policy chunks.
- [X] T05: Enhance `frontend/components.py` with interactive chips, quick-action follow-up buttons, and compact laptop cards with click-to-query actions.
- [X] T06: Enhance `frontend/floating_chat.py` with session reset ("🔄 New Chat") button, pending prompt handling, and reactive follow-up loop.

## Phase 4: Integration, Polish & Verification

- [X] T07: Run full pytest test suite and ensure 100% pass rate.
- [X] T08: Verify Python compilation and inspect UI responsiveness.
