# Tasks: Grid Side Scroll Button & Clean AI Assistant Shadow

**Input**: Design documents from `specs/010-grid-scroll-clean-assistant/`

**Prerequisites**: plan.md, spec.md, checklists/requirements.md

## Phase 1: Setup

- [x] T001 Review shelf grid layout in `frontend/storefront.py` and floating launcher shadow styles in `frontend/floating_chat.py`

## Phase 2: Foundational

- [x] T002 Verify category laptop chunking and pagination indexing logic for dynamic grid rendering

## Phase 3: User Story 1 - Functional Side Scroll Buttons Directly on Deal Grid (Priority: P1) 🎯 MVP

**Goal**: Place interactive, prominent side scroll buttons directly on the deal shelf grid alongside product cards

**Independent Test**: Load storefront, click `›` on the right side of Gaming Laptops deal shelf, verify the next batch of laptops displays, and verify `‹` appears to scroll back.

- [x] T003 [US1] Redesign `render_amazon_deal_shelf` in `frontend/storefront.py` to embed on-grid side scroll navigation buttons (`‹` on left and `›` on right, or a dedicated right side navigation column) directly alongside the cards within the deal shelf
- [x] T004 [US1] Add custom CSS for `.deal-shelf-scroll-btn` in `frontend/storefront.py`: elevated white rounded pill/card matching product card height, centered chevron, and smooth hover elevation
- [x] T005 [US1] Wire pagination state (`shelf_page_{shelf_key}`) to update on click and rerun smoothly

## Phase 4: User Story 2 - Clean AI Assistant Without Red Background Shade/Glow (Priority: P2)

**Goal**: Remove all red halo/shade artifacts from around the floating AI assistant button

**Independent Test**: Visually inspect the bottom-right corner; verify the chat launcher has no red aura, halo, or reddish blur.

- [x] T006 [US2] Update CSS in `frontend/floating_chat.py` to replace all `rgba(225, 29, 72, ...)` box-shadows with neutral dark shadows (`rgba(0, 0, 0, 0.15)`)
- [x] T007 [US2] Update JavaScript DOM locker in `frontend/floating_chat.py` to use neutral `rgba(0, 0, 0, 0.15)` box-shadow

## Phase 5: Verification & Polish

- [x] T008 Run Python syntax check and execute pytest suite (`pytest -v tests/`) to ensure all 22 tests pass
