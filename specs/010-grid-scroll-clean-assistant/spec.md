# Feature Specification: Grid Side Scroll Button & Clean AI Assistant Shadow

**Feature Branch**: `010-grid-scroll-clean-assistant`

**Created**: 2026-11-19

**Status**: Draft

**Input**: User description: "keep side scrool button on the grid to see other laptops too.and also remove that background red shade near ai assistent."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Functional Side Scroll Buttons Directly on Deal Grid (Priority: P1)

As a shopper browsing laptop deals on VoltKart, I want prominent, intuitive side scroll navigation buttons (`‹` and `›`) positioned directly alongside the product cards on the shelf grid so that I can immediately browse additional laptops in that category without having to search for controls elsewhere.

**Why this priority**: Directly satisfies the user's primary requirement to keep the side scroll button on the grid to view more laptops, matching familiar e-commerce carousel standards (e.g., Amazon).

**Independent Test**: Load the storefront with categories containing more than 3 laptops (e.g., Gaming Laptops, Student Laptops, Creator Laptops). Verify that a functional right scroll button (`›`) is visibly positioned directly on the grid. Click the button to verify the next set of laptops smoothly displays. When on page 2+, verify a left scroll button (`‹`) appears to scroll back.

**Acceptance Scenarios**:

1. **Given** a laptop deal shelf with more than 3 items, **When** viewing the shelf on desktop, **Then** a clean, elevated side scroll button (`›`) is displayed directly on the right side of the 3 cards within the deal shelf.
2. **Given** a user clicks the right side scroll button (`›`), **When** the click registers, **Then** the shelf immediately transitions to show the next batch of laptops from that category.
3. **Given** a shelf is on a subsequent page (page 2+), **When** viewing the grid, **Then** a left side scroll button (`‹`) is available on the left side to navigate back to previous laptops.
4. **Given** a category with 3 or fewer laptops, **When** rendering the shelf, **Then** no scroll buttons are rendered and cards display cleanly without empty spacing.

---

### User Story 2 - Clean AI Assistant Without Red Background Shade/Glow (Priority: P2)

As a customer browsing the store, I want the floating AI assistant button at the bottom-right of the screen to appear sharp, clean, and modern without any blurry red background shade, glow, or aura bleeding into the surrounding canvas.

**Why this priority**: Eliminates visual clutter and unwanted red shading around the floating chatbot, creating a crisp and polished aesthetic.

**Independent Test**: Inspect the bottom-right corner of the viewport where the AI assistant launcher hovers. Verify there is no red-colored blur, radial shade, or tinted halo behind or around the button. The button must cast only a subtle, neutral shadow (`rgba(0,0,0,...)`).

**Acceptance Scenarios**:

1. **Given** the customer is viewing any page on the storefront, **When** looking at the bottom-right floating chat launcher, **Then** there is zero red background shade, red radial aura, or reddish shadow cast onto the surrounding page.
2. **Given** the customer hovers their cursor over the chat launcher, **When** the hover state triggers, **Then** the button elevates with a clean, neutral shadow without emitting a red blur or red halo.

---

### Edge Cases

- **Single Page Categories**: If a deal category has 3 or fewer products, the side scroll buttons are omitted so the cards take up the full balanced grid width.
- **Last Page Scrolling**: Clicking the right scroll button on the final page wraps around seamlessly to page 1 (or disables gracefully).
- **Mobile Viewports (<768px)**: On narrow screens, the grid and scroll controls adjust gracefully to prevent overlapping product cards or clipping content.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST render functional side scroll buttons (`‹` and `›`) directly on the deal shelf grid for any category containing more than 3 laptops.
- **FR-002**: Clicking the right side scroll button (`›`) MUST advance the shelf pagination to the next page of laptops and refresh the displayed cards.
- **FR-003**: Clicking the left side scroll button (`‹`) MUST reverse the shelf pagination to the previous page of laptops.
- **FR-004**: Side scroll buttons MUST be styled with high visual clarity: elevated white rounded container, crisp chevron icon, smooth hover state, and vertically aligned with the product cards.
- **FR-005**: System MUST remove all red-tinted box shadows (`rgba(225, 29, 72, ...)`) from the floating AI assistant launcher button and its wrapper containers in both CSS stylesheets and JavaScript DOM lockers.
- **FR-006**: The floating AI assistant launcher MUST use a clean, neutral shadow (dark translucent `rgba(0, 0, 0, 0.12 - 0.18)`) with zero red bleeding or color halos into the surrounding light canvas.
- **FR-007**: Storefront catalog data, MongoDB grounding, and automated test suite (22/22) MUST continue to operate without regression.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of deal shelves with >3 laptops display interactive side scroll buttons directly on the grid.
- **SC-002**: 0 red shade or red halo artifacts visible around the floating AI assistant in both static and hovered states.
- **SC-003**: User can cycle through all catalog laptops in any category using only the on-grid side scroll controls.
- **SC-004**: 100% of existing unit and integration tests (22/22) pass without error.

## Assumptions

- Each deal shelf displays up to 3 cards per view, and side scroll controls paginate through subsequent chunks of 3 laptops.
- The specifications expander below the shelf remains intact for deep spec comparisons while pagination controls are promoted directly onto the deal grid.
