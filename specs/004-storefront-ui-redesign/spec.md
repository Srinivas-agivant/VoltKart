# Feature Specification: VoltKart Storefront UI/UX Redesign

**Feature Branch**: `004-storefront-ui-redesign`

**Created**: 2026-11-19

**Status**: Draft

**Input**: User description: "VoltKart UI/UX Redesign – Storefront Improvement. Remove unnecessary sidebar elements (system hub, db/ai status, chat sessions). Simplify navigation bar (remove LAPTOP/STORE badges, remove Admin Center from navbar, keep Home, Laptops, About Us, Contact). Add search icon & dynamic search widget in navigation area. Redesign hero section with 'Find Your Perfect Laptop' heading and modern dark navy gradient. Improve product search & multi-faceted filters (brand, price slider, RAM, processor, sorting). Ensure Floating AI Assistant is strictly anchored at a CONSTANT FIXED POSITION at bottom-right corner using CSS position: fixed, visible during scroll. Preserve all existing backend, MongoDB, Gemini AI, PDF upload, and admin capabilities."

---

## 1. Executive Summary & Problem Statement

The previous VoltKart interface retained internal diagnostic widgets, a prominent left sidebar with database/AI status telemetry, session management buttons, and admin links in the primary customer header. This made the experience feel like an administrative dashboard rather than a sleek, modern consumer electronics e-commerce storefront.

Additionally, the floating AI assistant was previously rendered in the regular document flow above the footer rather than using a viewport-anchored `position: fixed; z-index: 99999` overlay, causing it to displace page content and scroll with product cards.

This feature specification details the complete frontend redesign of VoltKart into a professional laptop e-commerce destination with:
1. **Full-Width Canvas**: Total removal of the diagnostic left sidebar to utilize 100% of the viewport width.
2. **Streamlined Navigation Bar**: Clean brand identity (`⚡ VoltKart`), simplified 4-link menu (`Home`, `Laptops`, `About Us`, `Contact`), and an integrated dynamic search input with search icon.
3. **Elevated Hero Section**: Premium dark navy/slate gradient banner with bold typography and clear value proposition.
4. **Enhanced Hardware Filter & Product Grid**: Multi-attribute filtering (brand, price slider, RAM, processor, sorting) rendering responsive cards with hardware specifications and expandable details.
5. **True Fixed Floating AI Assistant**: A bottom-right circular button and chat window anchored with CSS `position: fixed`, maintaining continuous accessibility while scrolling.
6. **Preserved Core Services**: Unaltered database persistence, Gemini grounded RAG pipelines, multi-page PDF ingestion, and discrete access to the Admin Center.

---

## 2. User Scenarios & Testing *(mandatory)*

### User Story 1 - Clean, Distraction-Free Shopping Navigation (Priority: P1)

As an online shopper, I want to browse a clean e-commerce header featuring only essential store navigation links and a dynamic search widget without administrative clutter or database status badges, so that I can focus entirely on discovering laptops.

**Why this priority**: First impressions and navigational clarity determine user engagement and shopping friction.

**Independent Test**: Navigate to the homepage. Verify the sidebar is absent/collapsed, the top navbar displays `⚡ VoltKart`, `Home`, `Laptops`, `About Us`, and `Contact`, and the search widget dynamically filters the product grid in real-time.

**Acceptance Scenarios**:
1. **Given** any storefront page, **When** the page renders, **Then** the left sidebar, "VoltKart System Hub", "Database: Connected", "AI Engine", and session management buttons are completely hidden.
2. **Given** the top navbar, **When** inspected, **Then** the badges (`LAPTOP`, `STORE`) and the `Admin Center` link are removed from customer view.
3. **Given** the search widget in the header area, **When** a user types a query like `"ThinkPad"` or `"RTX"`, **Then** the product grid immediately updates with matching database records, and a clear button resets the search.

---

### User Story 2 - Modern Hero Banner & Multi-Attribute Catalog Exploration (Priority: P1)

As a customer looking for a specific laptop, I want an inspiring hero banner and comprehensive hardware filters (brand, budget slider, RAM, processor, usage type, sort order), so that I can quickly narrow down the catalog to laptops matching my exact requirements.

**Why this priority**: Core value proposition of the VoltKart retail storefront.

**Independent Test**: Use the multi-faceted filter to select `Brand: Lenovo`, `Price: ₹40,000 - ₹70,000`, `RAM: 16GB`, and `Sort: Price: Low to High`. Verify only matching MongoDB laptops are rendered in order.

**Acceptance Scenarios**:
1. **Given** the homepage hero section, **When** rendered, **Then** it presents the heading *"Find Your Perfect Laptop"* and subtitle *"Explore premium laptops for coding, college, gaming and business. Find the right technology for your needs."* on a dark navy gradient background.
2. **Given** the laptop product cards, **When** displayed, **Then** each card cleanly presents the brand, model name, price in ₹, CPU, RAM, storage, battery life, and an interactive "View Details" expander.
3. **Given** multiple filter combinations, **When** applied, **Then** matching products are filtered dynamically from MongoDB without reloading or crashing.

---

### User Story 3 - Viewport-Fixed Floating AI Assistant (Priority: P1)

As a shopper navigating or scrolling through product listings, I want the VoltKart AI Assistant chat icon to remain permanently fixed at the bottom-right corner of my screen at all times, so that I can open and close the assistant whenever I need guidance without losing my scroll position.

**Why this priority**: Mandatory customer requirement ensuring the assistant is seamlessly accessible throughout the entire shopping journey.

**Independent Test**: Scroll down a long list of 25 laptop cards. Verify the floating circular button stays anchored in the bottom-right corner and opens a chat overlay above the icon that also stays anchored.

**Acceptance Scenarios**:
1. **Given** any page or scroll position, **When** the user scrolls up or down, **Then** the floating chatbot trigger button stays rigidly positioned at the bottom-right using CSS `position: fixed`.
2. **Given** the chat trigger is clicked, **When** the chat window opens, **Then** it displays as a fixed overlay above the trigger at the bottom-right with a clear close/minimize button, standardized greeting, conversational timeline, and input field.
3. **Given** an open chat session, **When** the user asks a recommendation, policy, or comparison query, **Then** the assistant synthesizes a grounded answer from MongoDB without page layout shifts.

---

### User Story 4 - Discrete Admin Capabilities Preservation (Priority: P2)

As a store administrator, I want to access the PDF Knowledge Base manager, CSV/Excel catalog ingestion, and audit logs through a discrete URL parameter or footer link, so that store management remains functional without exposing admin controls in the primary customer navbar.

**Why this priority**: Preserves document ingestion and catalog seeding while keeping the storefront consumer-focused.

**Independent Test**: Access the application with `?admin=true` or click the discrete footer link `"⚙️ Store Management"`. Verify the full Admin Control Center (CSV ingestion, PDF chunking, document deletion, and audit logs) renders seamlessly.

**Acceptance Scenarios**:
1. **Given** normal customer browsing, **When** viewing the navbar, **Then** no admin buttons are visible.
2. **Given** an admin navigating via discrete route or footer link, **When** loaded, **Then** the full Admin Control Center with all tabs is rendered and functional.

---

## 3. Technical Requirements & Design Specifications

### 3.1 Layout & Sidebar Elimination
- Set `st.set_page_config(layout="wide", initial_sidebar_state="collapsed")`.
- Inject CSS to completely hide `section[data-testid="stSidebar"]` on the storefront view, reclaiming 100% of screen width.
- Remove all diagnostic telemetry, status indicators, and duplicate chat triggers from the sidebar.

### 3.2 Top Header & Navigation
- Layout: 2-column or 3-column flex container:
  - Left: `⚡ VoltKart` brand mark (font size 1.8rem, bold, navy `#0f172a`, lightning bolt).
  - Center: Horizontal navigation links: `Home`, `Laptops`, `About Us`, `Contact`.
  - Right: Search input widget with search icon prefix, placeholder `"Search laptops by name, brand or specifications..."`, and dynamic state clearing.

### 3.3 Hero Section
- Styling: Deep navy/slate gradient (`linear-gradient(135deg, #090d16 0%, #0f172a 50%, #1e293b 100%)`).
- Typography: Heading `Find Your Perfect Laptop` (font-size 2.5rem, weight 800, sky-blue accent `#38bdf8`), Subtitle `Explore premium laptops for coding, college, gaming and business. Find the right technology for your needs.` (`#cbd5e1`).
- Padding: 48px 36px, border radius 16px, subtle drop shadow.

### 3.4 Product Catalog & Filter Bar
- Filters:
  - Brand multiselect (populated dynamically from distinct brands in MongoDB).
  - Price Range Slider (min and max dynamically computed from database records).
  - RAM Size multiselect (8GB, 16GB, 32GB).
  - Processor filter / text query.
  - Sorting selectbox: `Featured`, `Price: Low to High`, `Price: High to Low`, `RAM: High to Low`.
- Product Cards Grid:
  - 3-column responsive card layout.
  - White background, 1px border (`#e2e8f0`), rounded corners (12px), soft shadow (`0 4px 6px -1px rgba(0,0,0,0.05)`), hover transition (`transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1)`).
  - Displays: Brand badge, Model title, Price (`₹XX,XXX`), CPU, RAM, Storage, Battery Life.
  - Expandable `"🔍 View Details"` for display size, weight, warranty, and SKU.

### 3.5 Floating AI Assistant (CSS Position: Fixed)
- Inject CSS:
  ```css
  /* Fixed Bottom-Right Trigger Button */
  .floating-chat-trigger {
      position: fixed !important;
      bottom: 24px !important;
      right: 24px !important;
      z-index: 999999 !important;
  }
  /* Fixed Bottom-Right Chat Window Overlay */
  .floating-chat-panel {
      position: fixed !important;
      bottom: 85px !important;
      right: 24px !important;
      width: 420px !important;
      max-width: 90vw !important;
      height: 560px !important;
      max-height: 80vh !important;
      background: #ffffff !important;
      border-radius: 16px !important;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.1) !important;
      border: 1px solid #e2e8f0 !important;
      z-index: 999999 !important;
      overflow: hidden !important;
      display: flex !important;
      flex-direction: column !important;
  }
  ```
- Toggle action smoothly mounts/unmounts the chat container without disrupting the underlying scroll position.
- Retains existing `ConversationService`, `IntentService`, `RecommendationService`, `ComparisonService`, and `FaqService` pipelines.

### 3.6 Footer & Discrete Admin Access
- Professional e-commerce footer with store copyright, contact email (`support@voltkart.com`), helpline (`1800-VOLT-KART`), and a discrete link or toggle to open the **Admin Control Center**.

---

## 4. Non-Functional Requirements
- **Performance**: Sub-50ms frontend re-render times for local filter updates.
- **Responsiveness**: Fluid layout on screens ranging from 375px mobile viewports to 2560px 4K displays.
- **Reliability**: 100% preservation of database queries, 16/16 test passing rate, zero regressions in RAG retrieval.
- **Zero Hallucination**: Strict database grounding maintained across all chatbot answers.
