# Tasks: Side Scroll Button & Top Specifications Expander

**Input**: Design documents from `specs/011-shelf-scroll-specs-top/`

**Prerequisites**: plan.md, spec.md, checklists/requirements.md

## Phase 1: Setup

- [x] T001 Review `render_amazon_deal_shelf` in `frontend/storefront.py`

## Phase 2: User Story 1 - Clean Minimalist Shelf Header & Dedicated Right Scroll Button (Priority: P1) 🎯 MVP

**Goal**: Remove page and count badges from shelf header and ensure a clean, prominent right scroll button (`›`) on the grid

**Independent Test**: Load storefront, observe deal shelf header contains only category title, and click `›` on the right side of the cards to cycle laptops.

- [x] T002 [US1] Remove `page_info` / `deal-shelf-page-tag` markup from `shelf_header_html` in `frontend/storefront.py`
- [x] T003 [US1] Ensure the right scroll button (`›`) is reliably rendered in the 4th column of `st.columns([1, 1, 1, 0.28])` with smooth wrap-around pagination
- [x] T004 [US1] Refine CSS styling for the on-grid scroll button to guarantee high visibility, elevation, and centered vertical alignment

## Phase 3: User Story 2 - Detailed Specifications Placed on Top of Every Catalog Shelf (Priority: P2)

**Goal**: Position the Detailed Specifications expander bar directly above each catalog shelf

**Independent Test**: Verify the `🔍 Detailed Specifications` expander sits above the orange deal shelf container.

- [x] T005 [US2] Move `st.expander(f"🔍 Detailed Specifications for {title}", expanded=False)` to render directly ABOVE `shelf_box_{shelf_key}` container in `frontend/storefront.py`

## Phase 4: Verification & Polish

- [x] T006 Compile check all Python files and run pytest suite (`pytest -v tests/`) to verify all 22 tests pass
- [x] T007 Eliminate nested container backgrounds and red box-shadows around floating AI assistant launcher in `frontend/floating_chat.py`
