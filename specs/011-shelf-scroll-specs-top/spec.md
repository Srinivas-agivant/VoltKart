# Feature Specification: Side Scroll Button & Top Specifications Expander

**Feature Branch**: `011-shelf-scroll-specs-top`

**Created**: 2026-11-19

**Status**: Draft

**Input**: User description: "remove that page and the count just add side button for scroll next keep the detailed info slidebar on top of evry catalog"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Clean Minimalist Shelf Header & Dedicated Right Scroll Button (Priority: P1)

As a shopper browsing laptop deal shelves, I want a clean, uncluttered shelf header containing only the category title (with no "Page X of Y" or laptop count badges), and a prominent, functional side scroll button (`›`) positioned on the right of the cards to smoothly page through laptops.

**Why this priority**: Directly addresses the user's explicit request to remove the page and count badges from the shelf header and guarantee a visible, functional side button to scroll next.

**Independent Test**: Load the storefront. Observe any deal shelf (e.g., Gaming Laptops, Office & Business Laptops). Verify that:
1. The top header of the orange shelf contains only the category title without any "Page 1 of 2" or "(6 Laptops)" badge.
2. A sleek white circular or rounded button with a bold right chevron (`›`) appears on the right side of the 3 cards.
3. Clicking `›` advances immediately to the next set of laptops.

**Acceptance Scenarios**:

1. **Given** a deal shelf with more than 3 laptops, **When** examining the orange header bar, **Then** only the category title is displayed (no page numbers or count pills).
2. **Given** a deal shelf with more than 3 laptops, **When** looking at the card area, **Then** an elevated white side scroll button (`›`) is clearly visible on the right edge of the grid.
3. **Given** the user clicks the side scroll button (`›`), **When** clicked, **Then** the shelf transitions to display the next batch of laptops (cycling back to the beginning on the final page).

---

### User Story 2 - Detailed Specifications Placed on Top of Every Catalog Shelf (Priority: P2)

As a customer comparing laptop hardware, I want the "Detailed Specifications" expander bar to sit directly above each catalog shelf rather than hidden below it, so that I can inspect full technical specifications before or alongside browsing the cards.

**Why this priority**: Elevates specification transparency and matches the user's explicit request to place the detailed info slidebar/expander on top of each catalog section.

**Independent Test**: Inspect the layout of each deal category. Verify the `🔍 Detailed Specifications` expander is positioned above the orange deal container, giving immediate access to CPU, RAM, GPU, storage, battery, and warranty details for all laptops in that category.

**Acceptance Scenarios**:

1. **Given** a user is viewing any laptop category, **When** scanning the section, **Then** the Detailed Specifications expander bar is placed directly above the orange deal shelf.
2. **Given** the user clicks the expander on top of the catalog, **When** it opens, **Then** the detailed specifications for the current laptops are cleanly presented with brand, SKU, CPU, RAM, storage, display, battery, and warranty.

---

### Edge Cases

- **Categories with 3 or Fewer Laptops**: No side scroll button is rendered on the right; the 3 cards expand symmetrically to fill the full shelf width.
- **Last Page Wrap**: Clicking `›` on the last page of laptops smoothly loops back to the first 3 laptops.
- **Filtered / Search Results**: When active filters or search terms are applied, the filtered shelves also place the Detailed Specifications bar on top and display the side scroll button on the right if results exceed 3.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST remove the "Page X of Y" badge and laptop count tag from the header of all category deal shelves.
- **FR-002**: System MUST render a prominent, elevated side scroll button (`›`) positioned on the right side of the deal cards for every shelf with more than 3 laptops.
- **FR-003**: Clicking the right side scroll button (`›`) MUST advance to the next set of laptops for that category, wrapping back to the start when reaching the end.
- **FR-004**: System MUST position the "Detailed Specifications" expander bar directly ABOVE each deal shelf container (on top of every catalog).
- **FR-005**: All existing laptop data, price calculation, image rendering, and 22/22 unit tests MUST remain operational without regression.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 0 page number or count badges displayed within deal shelf headers.
- **SC-002**: 100% of deal shelves with >3 laptops display a functional right scroll button (`›`) beside the cards.
- **SC-003**: 100% of deal categories feature their Detailed Specifications expander bar positioned above the deal shelf container.
- **SC-004**: 100% test pass rate across the existing test suite (22/22).

## Assumptions

- Specifications expander defaults to collapsed (`expanded=False`) so it does not obstruct the initial card view while remaining instantly accessible on top.
- The side scroll button uses container-relative sizing with smooth hover effects to blend naturally with the Amazon-style orange shelf.
