# Implementation Plan: VoltKart Storefront UI/UX Redesign

**Branch**: `004-storefront-ui-redesign` | **Date**: 2026-11-19 | **Status**: Planned

## 1. Architecture & Design Decisions

### 1.1 Full-Width Layout & Complete Sidebar Removal
- Set `st.set_page_config(layout="wide", initial_sidebar_state="collapsed")`.
- Inject CSS hiding `section[data-testid="stSidebar"]` completely on customer-facing views, freeing up the entire screen width for product discovery.
- Remove all internal diagnostic telemetry (`VoltKart System Hub`, `Database: Connected (Live)`, `AI Engine: Gemini Active`, chat session list, and new chat buttons) from customer view.

### 1.2 Streamlined Header with Integrated Dynamic Search
- Simplify the top navigation bar into a modern horizontal flex row:
  - **Left**: Minimalist brand logo `⚡ VoltKart` (deep navy `#0f172a`, bold, lightning symbol; remove `LAPTOP` and `STORE` badges).
  - **Center**: Clean horizontal menu: `Home`, `Laptops`, `About Us`, `Contact`.
  - **Right**: Compact search input with search icon `🔍`, placeholder `"Search laptops by name, brand or specifications..."`, and instant clear option (`✖`).
- Dynamic search queries laptop names, brands, processors, RAM, and specifications from MongoDB.

### 1.3 Modernized Hero Section
- Heading: `"Find Your Perfect Laptop"`
- Subtitle: `"Explore premium laptops for coding, college, gaming and business. Find the right technology for your needs."`
- Theme: Dark navy/slate gradient (`linear-gradient(135deg, #090d16 0%, #0f172a 50%, #1e293b 100%)`) with sky-blue accents (`#38bdf8`), rounded corners (16px), and subtle drop shadows.
- Avoid excessive whitespace and ensure full responsiveness across viewports.

### 1.4 Product Filtering & Responsive 3-Column Card Grid
- Multi-faceted filter bar:
  - Brand multiselect (populated dynamically from MongoDB).
  - Price range slider (₹ min to max).
  - RAM size multiselect (8GB, 16GB, 32GB).
  - Processor filter.
  - Sorting: `Featured`, `Price: Low to High`, `Price: High to Low`, `RAM: High to Low`.
- Product Cards:
  - White container with `#e2e8f0` border, 12px rounded corners, soft shadow, hover lift effect.
  - Laptop visual icon/badge, brand badge, model title, formatted price in ₹.
  - Specifications: CPU, RAM, Storage, GPU, Battery Life.
  - Expandable `"🔍 View Details"` drawer for display, weight, warranty, and SKU.

### 1.5 Viewport-Fixed Floating AI Assistant (CSS Position: Fixed)
- Mandatory requirement:
  - Floating circular trigger button anchored strictly at `position: fixed; bottom: 24px; right: 24px; z-index: 999999`.
  - Permanently visible while scrolling page content without moving or overlapping key buttons.
  - When toggled, mounts a fixed chat overlay anchored at `position: fixed; bottom: 95px; right: 24px; width: 420px; max-height: 580px; z-index: 999999`.
  - Floating panel contains brand header, minimize/close button, welcome greeting, conversational timeline, product recommendation cards, comparison tables, and message input.
  - Preserves session state and conversation continuity.

### 1.6 Discrete Store Management Access
- Remove `Admin Center` from the primary customer navigation bar.
- Provide discrete access via query parameter `?admin=true` or discrete footer link `"⚙️ Store Management"` to preserve full PDF Knowledge Base management, CSV/Excel ingestion, and audit logs.

---

## 2. File Modification Strategy

1. **`frontend/storefront.py`**:
   - Update `render_storefront` to support hero section redesign, integrated search query filtering, enhanced brand/RAM/processor multi-attribute filters, sorting, and responsive product cards with hover effects.
2. **`frontend/floating_chat.py`**:
   - Refactor into a true fixed floating widget using custom CSS injection (`position: fixed !important; bottom: 24px; right: 24px; z-index: 999999`).
   - Implement fixed circular launcher button and fixed popup overlay card.
3. **`app.py`**:
   - Remove sidebar components and telemetry.
   - Implement top navigation header with integrated search input and clear button.
   - Add discrete footer with store copyright, support contact, and `"⚙️ Store Management"` admin toggle.
4. **`tests/test_storefront_ui.py`**:
   - Add unit/integration tests verifying filter logic, search filtering, and conversation persistence.
