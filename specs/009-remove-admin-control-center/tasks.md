# Tasks: Remove Admin Control Center

**Input**: Design documents from `specs/009-remove-admin-control-center/`

**Prerequisites**: plan.md, spec.md, checklists/requirements.md

## Phase 1: Setup

**Purpose**: Identify all administrative UI hooks in the main application flow

- [x] T001 Review `app.py` for all references to `admin_mode`, `render_admin_dashboard`, and `footer_admin_toggle`

---

## Phase 2: Foundational

**Purpose**: Ensure catalog data seeding and background resilience remain completely independent of the admin UI

- [x] T002 Verify `auto_seed_default_catalog()` remains active and independent in `app.py`

---

## Phase 3: User Story 1 - Pure Customer-Facing Storefront (Priority: P1) 🎯 MVP

**Goal**: Deliver a pure, authentic customer storefront with zero administrative buttons or back-office control panels

**Independent Test**: Load `http://localhost:8501` and verify footer contains only customer support/legal info and that `?admin=true` does not trigger an admin panel.

- [x] T003 [US1] Remove `admin_mode` state initialization and admin control center view branch in `app.py`
- [x] T004 [US1] Remove `⚙️ Store Management` button and footer column split in `app.py`
- [x] T005 [US1] Remove unneeded `from frontend.admin_dashboard import render_admin_dashboard` import in `app.py`

**Checkpoint**: Storefront is 100% customer-facing.

---

## Phase 4: User Story 2 - Automated Data Integrity & Seeding (Priority: P2)

**Goal**: Guarantee catalog auto-seeding, data validation, and test harness execution remain 100% operational

**Independent Test**: Run `python -m pytest -v tests/` and verify all 22 tests pass.

- [x] T006 [US2] Verify backend ingestion services and CLI script (`import_data.py`) continue to pass all tests

---

## Phase 5: Verification & Polish

- [x] T007 Run Python syntax compilation and execute full test suite (`pytest -v tests/`) to ensure 22/22 tests pass
