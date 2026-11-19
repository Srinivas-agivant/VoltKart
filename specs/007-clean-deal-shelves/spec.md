# Feature Specification: Clean Deal Shelves & Removal of Non-Functional Elements

**Feature Branch**: `007-clean-deal-shelves`

**Created**: 2026-11-19

**Status**: Draft

**Input**: User description: "remove the explore in that and also remove the button which is inside that is not working"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Symmetrical 3-Card Deal Shelf Without Inactive Elements (Priority: P1)

Shoppers browsing VoltKart laptop categories want a clean, distraction-free shelf view where every visible control is functional. In the current interface, the shelf header displays an unlinked "Explore more" text and an inactive static right chevron button (`›`) inside the card grid. Removing these non-functional decorative elements allows the 3 product cards to distribute evenly across the full shelf width and eliminates confusion about non-responsive UI elements.

**Why this priority**: Displaying static elements that appear interactive but do not respond to clicks causes user frustration and reduces perceived website quality.

**Independent Test**: Load the home storefront, inspect any deal category shelf (e.g., Gaming Laptops, Student Laptops), and verify that:
1. No "Explore more" text appears in the shelf header.
2. No inactive chevron button appears inside the shelf grid.
3. Exactly 3 product cards span the full grid width with equal spacing and crisp borders.

**Acceptance Scenarios**:
1. **Given** a user is viewing any laptop category deal shelf, **When** examining the shelf header, **Then** only the shelf category title is displayed without any "Explore more" link.
2. **Given** a user is viewing the card grid, **When** examining the right side of the third product card, **Then** no static right chevron (`›`) button is rendered.
3. **Given** the inactive arrow is removed, **When** viewing on desktop, **Then** the 3 cards expand symmetrically in a 3-column grid (`repeat(3, 1fr)`) filling the container width.

---

### User Story 2 - Clear Functional Pagination Below the Shelf (Priority: P2)

When a category contains more than 3 laptops, users navigate between pages of 3 laptops using the dedicated functional navigation buttons (`◀` and `▶`).

**Why this priority**: Users must still be able to browse all laptops in each category easily.

**Independent Test**: Click `▶` on a category with more than 3 laptops and verify the next set of 3 laptops loads with smooth rerun.

**Acceptance Scenarios**:
1. **Given** a category with more than 3 products, **When** the user clicks `▶`, **Then** the shelf displays the next 3 products.
2. **Given** a category on page 2, **When** the user clicks `◀`, **Then** the shelf returns to the previous 3 products.

---

### Edge Cases

- **Categories with 3 or fewer laptops**: Shelf renders all available laptops without pagination buttons or empty slots.
- **Search and Filter Shelves**: Filtered result shelves also adhere to the clean 3-card layout without "Explore more" or inactive chevron.
- **Mobile Viewports (<640px)**: The 3-card grid stacks responsively to 1 card per row while maintaining clean borders and headers.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST remove the "Explore more" link/label from the header of all category deal shelves.
- **FR-002**: The system MUST remove the static non-functional chevron button (`.deal-carousel-arrow`) from inside the deal shelf grid.
- **FR-003**: The deal shelf grid MUST render exactly 3 columns (`repeat(3, 1fr)`) on desktop screens, distributing cards evenly across the full container width.
- **FR-004**: Each deal card MUST maintain its distinct border, rounded corners, drop shadow, and hover effect.
- **FR-005**: The functional pagination controls (`◀` and `▶`) MUST remain intact and operational for categories exceeding 3 products.

### Key Entities

- **Deal Shelf**: A visual container grouping laptops by usage category with an orange gradient background, category title, and a 3-card product grid.
- **Product Deal Card**: An elevated white card displaying product image, model name, price, discount badge, specifications, and border.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 0 non-functional or unclickable elements present within the deal shelf container.
- **SC-002**: 100% of deal shelves display 3 evenly spaced, bordered cards across full shelf width on standard desktop viewports.
- **SC-003**: Pagination through all catalog laptops in each category functions without layout shifts or horizontal clipping.

## Assumptions

- The existing functional `◀` and `▶` pagination buttons below the shelf remain the primary pagination mechanism.
- All product records continue to be retrieved from MongoDB with exact model names.
