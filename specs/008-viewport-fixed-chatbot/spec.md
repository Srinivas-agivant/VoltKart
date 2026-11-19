# Feature Specification: Viewport-Fixed Hover AI Assistant Widget

**Feature Branch**: `008-viewport-fixed-chatbot`

**Created**: 2026-11-19

**Status**: Draft

**Input**: User description: "the ai assistant is down and small also when scrolled it is being scolled.but i want that bot should hover of the screen right side below without any change even when changed"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Constant Viewport-Anchored Launcher Icon (Priority: P1)

Shoppers on VoltKart must have immediate, one-click access to the AI shopping assistant from anywhere on the storefront at any time. When browsing, scrolling through catalogs, or changing pages, the assistant launcher icon must hover in a fixed position at the bottom-right of the viewport. It must never scroll off-screen, never appear at the bottom-left, never render as an unstyled button, and maintain a prominent, round circular badge appearance (60–65px diameter) with glowing depth.

**Why this priority**: A shopping assistant that scrolls off-screen or renders out of view is inaccessible to shoppers while they are actually evaluating products.

**Independent Test**: Load the storefront on any page, scroll from the top hero banner down through all deal shelves to the footer, and verify that the circular chat icon remains floating at the exact same bottom-right screen coordinates throughout the entire scroll.

**Acceptance Scenarios**:
1. **Given** the customer is at the top of the page, **When** they scroll down to the bottom, **Then** the assistant launcher icon remains stationary at the bottom-right corner of the browser viewport.
2. **Given** the customer switches navigation tabs (Home, About Us, Contact), **Then** the launcher icon remains visible at the exact same bottom-right position without flashing or relocating.
3. **Given** the launcher icon is displayed, **When** inspected visually, **Then** it renders as a circular, elevated, vibrant button with an assistant icon, not as an unstyled rectangular button in normal document flow.

---

### User Story 2 - Smooth Bottom-Right Chat Window Overlay (Priority: P1)

When the customer clicks the floating launcher, an interactive chat window expands directly above the bottom-right corner of the screen. The open window must also remain fixed in place during page scrolling, providing immediate conversation access while allowing the customer to review products behind or beside the panel.

**Why this priority**: The conversation panel must remain stable and anchored while the user types or reads recommendations.

**Independent Test**: Click the floating launcher, verify the chat window opens at bottom-right, scroll the storefront background, and confirm the chat window stays anchored to the viewport.

**Acceptance Scenarios**:
1. **Given** the launcher icon is clicked, **When** the chat window opens, **Then** it anchors to the bottom-right corner of the screen (`position: fixed`) with a clear z-index above all other page elements.
2. **Given** the chat window is open, **When** the user scrolls the page, **Then** the chat window stays stationary on screen without jumping or disappearing.
3. **Given** the user clicks the close (`✖`) button, **When** the panel closes, **Then** the circular floating launcher icon immediately reappears in the same bottom-right position.

---

### Edge Cases

- **Mobile Viewports (<640px)**: The floating launcher remains pinned to the bottom-right (`bottom: 16px`, `right: 16px`) and the open chat window scales to fit the mobile screen (`max-width: calc(100vw - 32px)`).
- **Page Resizing**: Resizing the browser window recalculates viewport coordinates so the widget stays docked at bottom-right.
- **Scroll Inertia / Touch Scrolling**: On touchpads and mobile screens, fixed positioning does not jitter or lag during rapid scrolling.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The AI assistant launcher icon MUST hover persistently at the bottom-right corner of the browser viewport (`position: fixed`) across all pages and scroll positions.
- **FR-002**: The launcher icon MUST render as a prominent circular action button with a diameter of 60–65px, elevated drop shadow, and distinct assistant iconography (`💬`).
- **FR-003**: The launcher MUST NOT appear in normal page document flow or scroll with page content.
- **FR-004**: Clicking the launcher MUST open the floating chat panel anchored at the bottom-right corner of the viewport.
- **FR-005**: The open chat panel MUST remain viewport-fixed during scrolling with a z-index of at least `999999`.
- **FR-006**: The open chat panel MUST provide an immediate close control that restores the circular floating launcher without losing session conversation state.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Launcher icon coordinates remain 100% constant relative to the viewport during vertical scrolling from 0% to 100% of page height.
- **SC-002**: 0 instances of the launcher appearing in normal page flow, at bottom-left, or unstyled.
- **SC-003**: Chat panel opens and closes in under 0.3 seconds upon user click without page reload or loss of conversation memory.

## Assumptions

- Users access the application via modern standards-compliant web browsers supporting CSS `position: fixed` and `:has()` selectors.
- The assistant operates as a client-side overlay on top of the Streamlit storefront.
