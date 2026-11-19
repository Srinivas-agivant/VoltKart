# Feature Specification: Catalog & Chat UX Fix

**Feature Branch**: `005-catalog-chat-ux-fix`

**Created**: 2026-11-19

**Status**: Draft

**Input**: User description: "Fix the catalog items perfectly in the specified box. Make sure the search engine works. In home page give AI chat bot assistant right side below should be stable even when it is scrolled. In the AI chat make sure the messages given or suggested should be correctly aligned. Make proper UI/UX."

## User Scenarios & Testing *(mandatory)*

### User Story 1 – Product Catalog Cards Render Properly Inside Deal Shelves (Priority: P1)

A shopper visits the VoltKart homepage and sees laptop deal shelves ("Deals on Gaming Laptops", "Deals on Student & Everyday Laptops", etc.). Each shelf is an orange container holding exactly 4 white product cards. Every card shows the laptop image, the exact database model name, the deal price with M.R.P. and discount badge, and a one-line specs summary. Cards are visually contained within the orange shelf — no raw HTML source code is ever displayed.

**Why this priority**: The storefront catalog is the core commercial surface. If cards render as raw HTML text instead of visual product tiles, the application is unusable.

**Independent Test**: Load the homepage with 25 laptops in the database. Verify every shelf renders styled product cards (image, name, price, specs) with no visible `<div>` tags or markup.

**Acceptance Scenarios**:

1. **Given** the database contains 25 laptop products, **When** a shopper opens the homepage, **Then** laptop deal shelves display with properly rendered white product cards inside orange containers — no raw HTML or markup is visible.
2. **Given** a shelf contains more than 4 laptops, **When** the shopper clicks the pagination arrow, **Then** the next set of 4 cards appears within the same shelf container.
3. **Given** a laptop record in the database has the name "AeroBook 14", **When** that laptop appears on a card, **Then** the card title reads exactly "AeroBook 14" — not a generated or placeholder name.

---

### User Story 2 – Search Engine Filters Products Dynamically (Priority: P1)

A shopper types a search query (laptop name, brand, processor, RAM, or storage keyword) into the header search bar. The catalog immediately filters to show only matching laptops. A clear button removes the query and restores the full catalog.

**Why this priority**: Search is the primary product discovery mechanism. Without it, customers cannot find specific models in a 25-item catalog.

**Independent Test**: Type "gaming" in the search bar. Verify only laptops whose name, brand, processor, graphics, RAM, or storage fields contain "gaming" are displayed. Clear the search and verify all 25 laptops reappear.

**Acceptance Scenarios**:

1. **Given** the full catalog is displayed, **When** the shopper types "GameForce" in the search bar, **Then** only laptops with "GameForce" in their name, brand, or specs are shown.
2. **Given** a search is active, **When** the shopper clicks the clear (✖) button, **Then** the search input is emptied and the full catalog is restored.
3. **Given** the shopper enters a query that matches no products, **When** the catalog filters, **Then** a helpful empty-state message is shown (e.g., "No laptops match your search").
4. **Given** the shopper types "intel" in the search bar, **When** the catalog filters, **Then** laptops whose processor field contains "Intel" are shown, demonstrating spec-level search beyond just name and brand.

---

### User Story 3 – Floating AI Chatbot Stays Fixed on Scroll (Priority: P1)

The AI chatbot icon (circular 💬 button) and, when open, the chat panel, remain anchored at the bottom-right corner of the viewport at all times — including when the shopper scrolls through the product catalog. The chatbot never jumps, disappears behind content, or shifts position.

**Why this priority**: The chatbot is the main AI assistance surface. If it scrolls away with the page, the shopper cannot access help while browsing products.

**Independent Test**: Open the homepage with a full catalog. Scroll down through all deal shelves. Verify the floating chat icon remains visible and clickable at the bottom-right corner throughout the scroll. Open the chat panel and scroll the page again — verify the panel stays fixed.

**Acceptance Scenarios**:

1. **Given** the chatbot is closed (icon mode), **When** the shopper scrolls down through the catalog, **Then** the circular 💬 icon remains pinned at bottom-right of the viewport.
2. **Given** the chatbot panel is open, **When** the shopper scrolls the page behind it, **Then** the chat panel stays fixed at bottom-right and does not shift or overlap with the scrollbar.
3. **Given** the chat panel is open, **When** the shopper clicks the close (✖) button, **Then** the panel closes and the circular icon reappears at the same fixed position.

---

### User Story 4 – Chat Messages Are Correctly Aligned and Readable (Priority: P2)

Inside the AI chatbot panel, customer messages (user) appear right-aligned or clearly distinguished, and AI assistant messages (bot) appear left-aligned or clearly distinguished. Suggested quick-action chips are properly aligned and do not overlap with the message timeline. The welcome message is displayed immediately upon opening the chat.

**Why this priority**: Misaligned messages make conversations confusing and reduce trust in the AI assistant.

**Independent Test**: Open the chatbot. Verify the welcome message is left-aligned (assistant style). Type a question. Verify the user message is right-aligned (customer style) and the AI response appears below it left-aligned. Check that suggestion chips are horizontally laid out without overlapping.

**Acceptance Scenarios**:

1. **Given** the chatbot opens for the first time, **When** the panel is displayed, **Then** the welcome message "Hi! Welcome to VoltKart. I'm your AI shopping assistant. How can I help you today?" appears as an assistant-role message (left-aligned or visually distinct from user messages).
2. **Given** the user sends a message, **When** the response appears, **Then** the user's message is visually distinct (right side or user bubble) and the assistant's reply is visually distinct (left side or assistant bubble).
3. **Given** the conversation has more messages than fit in the visible area, **When** new messages appear, **Then** the message timeline scrolls to show the latest message.
4. **Given** suggestion chips are displayed, **When** the user views the chat panel, **Then** chips are horizontally arranged without overlapping with the input field or the message timeline.

---

### User Story 5 – Polished UI/UX Across the Storefront (Priority: P2)

The overall visual presentation of the storefront is clean, professional, and consistent: navigation bar is properly aligned, the hero banner renders correctly, filters and sorting work smoothly, the footer is well-formatted, and there is no visual jank (misaligned columns, broken layout, unstyled elements).

**Why this priority**: A cohesive, professional appearance is essential for hackathon demonstration quality and customer trust.

**Independent Test**: Navigate through Home, About Us, and Contact pages. Verify all visual elements are styled, aligned, and responsive. No raw HTML, broken images, or layout shifts are present.

**Acceptance Scenarios**:

1. **Given** the shopper is on the Home page, **When** they view the navigation bar, **Then** ⚡ VoltKart branding, Home/About Us/Contact links, and the search input are horizontally aligned and visually balanced.
2. **Given** the shopper scrolls to the bottom, **When** the footer is visible, **Then** VoltKart copyright, helpline, and support info are displayed in a clean two-column layout.
3. **Given** the shopper opens the filter expander, **When** they adjust brand, price, RAM, or usage filters, **Then** the catalog updates immediately and the count label reflects the filtered total.

---

### Edge Cases

- What happens when the database contains zero products? The homepage shows a helpful warning prompting the user to seed data via Store Management.
- What happens when the chatbot's Gemini API key is invalid or rate-limited? The local fallback generator produces deterministic grounded responses without crashing.
- What happens when a product record is missing the `name` field? The storefront skips that record gracefully (it is not displayed as "None" or empty).
- What happens when the shopper types a very long search query? The search input does not overflow its container; excess text is clipped or scrolled.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Product catalog cards MUST render as fully styled visual tiles (image, name, price, specs) inside orange deal shelf containers — raw HTML markup MUST NEVER be visible to the user.
- **FR-002**: The header search bar MUST dynamically filter the displayed laptops by name, brand, processor, graphics, RAM, and storage fields using case-insensitive substring matching.
- **FR-003**: The search clear button (✖) MUST reset the search input and restore the full unfiltered catalog.
- **FR-004**: The floating AI chatbot icon MUST remain anchored at the bottom-right of the viewport using CSS `position: fixed` and MUST NOT scroll with the page content.
- **FR-005**: The floating AI chatbot panel (when open) MUST remain anchored at the bottom-right of the viewport using CSS `position: fixed` and MUST NOT scroll with the page content.
- **FR-006**: User messages in the chat MUST be visually distinct from assistant messages (different alignment, background color, or bubble style).
- **FR-007**: The chat message timeline MUST auto-scroll to show the most recent message when a new message is added.
- **FR-008**: Suggestion chips in the chatbot MUST be horizontally arranged without overlapping the input field or message timeline.
- **FR-009**: Product card names MUST display the exact model name from the MongoDB database — no generated, hardcoded, or placeholder names.
- **FR-010**: All HTML content rendered via Streamlit MUST use `st.html()` (preferred) or properly constructed single-line strings passed to `st.markdown(unsafe_allow_html=True)` to prevent indentation-based code block rendering.
- **FR-011**: The navigation bar (branding, links, search) MUST be horizontally aligned and visually balanced.
- **FR-012**: The brand, price range, RAM, and usage filters MUST update the catalog count and displayed products immediately upon selection.

### Key Entities

- **Product (Laptop)**: The core catalog entity retrieved from MongoDB. Key display attributes: name (exact from DB), brand, price, processor, RAM, storage, graphics, battery life, weight, warranty, usage type, product ID.
- **Deal Shelf**: A visual grouping of up to 4 product cards under a category title (e.g., "Deals on Gaming Laptops") inside an orange container.
- **Chat Message**: A single turn in the conversation. Has a role (user or assistant), content text, optional product list, and intent type.
- **Suggestion Chip**: A quick-action button displayed in the chat panel that pre-fills a common query.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of product cards render as styled visual tiles on the homepage — zero instances of raw HTML markup visible to the user.
- **SC-002**: Search returns matching products within 1 second of the user pressing Enter, covering name, brand, processor, graphics, RAM, and storage fields.
- **SC-003**: The floating chatbot icon and panel remain at the bottom-right viewport position during 100% of scroll interactions on the homepage.
- **SC-004**: User and assistant messages are visually distinguishable with consistent alignment in every conversation turn.
- **SC-005**: All 20+ automated tests pass without regression after the UI/UX fixes are applied.
- **SC-006**: The storefront loads with all visual elements properly styled on first page load — no flash of unstyled content or layout shift.

## Assumptions

- The existing MongoDB database already contains 25 laptop products with the dual-field schema (`name`/`model`, `price`/`price_inr`, `brand`/`store`, `usage_type`/`usage_category`).
- The existing backend services (Gemini AI, retrieval, conversation, intent) are working correctly and do not need modification — only the frontend rendering needs fixing.
- The Streamlit version in use supports `st.html()` for injecting raw HTML without markdown interference.
- The floating chatbot's CSS `position: fixed` strategy is compatible with the user's browser (modern Chrome, as seen in the screenshot).
- Product images use Unsplash URLs with inline SVG fallbacks — no local image files need to be managed.
