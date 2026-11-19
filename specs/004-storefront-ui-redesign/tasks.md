---
description: "Tasks for VoltKart Storefront UI/UX Redesign"
---

# Tasks: VoltKart Storefront UI/UX Redesign

## Phase 1: Core Layout & Sidebar Removal
- [X] `T301` Configure full-width layout and inject CSS in `app.py` to completely hide the left telemetry/session sidebar (`section[data-testid="stSidebar"]`).
- [X] `T302` Remove diagnostic badges (`Database: Connected`, `AI Engine: Active`, session buttons, recent chat lists) from customer-facing views in `app.py`.

## Phase 2: Simplified Header & Integrated Search Widget
- [X] `T303` Simplify the top navigation bar in `app.py` to display `⚡ VoltKart`, `Home`, `Laptops`, `About Us`, and `Contact` (remove `LAPTOP`/`STORE` badges and `Admin Center`).
- [X] `T304` Implement compact dynamic search input with `🔍` icon prefix, placeholder `"Search laptops by name, brand or specifications..."`, and query clearing button in header.

## Phase 3: Hero Section & Multi-Attribute Catalog Exploration
- [X] `T305` Redesign hero section in `frontend/storefront.py` with heading `"Find Your Perfect Laptop"`, official description, dark navy gradient styling, and responsive typography.
- [X] `T306` Implement multi-attribute filter bar (brand multiselect, price range slider, RAM multiselect, processor filter, and sorting) in `frontend/storefront.py`.
- [X] `T307` Refactor product cards in `frontend/storefront.py` with 3-column responsive layout, hardware specs (CPU, RAM, storage, battery), and expandable `"🔍 View Details"` drawer.

## Phase 4: Viewport-Fixed Floating AI Assistant
- [X] `T308` Refactor `frontend/floating_chat.py` with custom CSS `position: fixed; bottom: 24px; right: 24px; z-index: 999999` to ensure the circular chatbot icon remains permanently anchored during scrolling.
- [X] `T309` Implement fixed overlay chat panel positioned above the trigger button (`bottom: 24px; right: 24px; position: fixed; z-index: 999999`) with close/minimize button, standardized greeting, conversational timeline, and message input.

## Phase 5: Discrete Store Management & Verification
- [X] `T310` Add discrete admin access link in footer (`"⚙️ Store Management"`) or query parameter toggle to preserve PDF Knowledge Base and CSV ingestion.
- [X] `T311` Execute test suite and verify all unit tests pass (`pytest tests/`).
