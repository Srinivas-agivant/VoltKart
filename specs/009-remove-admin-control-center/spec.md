# Feature Specification: Remove Admin Control Center

**Feature Branch**: `009-remove-admin-control-center`

**Created**: 2026-11-19

**Status**: Draft

**Input**: User description: "remove the admin control center"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Pure Customer-Facing Storefront (Priority: P1)

As a VoltKart shopper browsing laptops, I want a clean, distraction-free e-commerce experience without any administrative tools, back-office controls, or management buttons visible on the storefront, so that the store feels completely authentic, professional, and trustworthy.

**Why this priority**: Directly satisfies the user's explicit request to eliminate the admin control center from the storefront, keeping the UI focused strictly on consumer laptop browsing and AI purchasing assistance.

**Independent Test**: Load the storefront at `http://localhost:8501`. Verify that no "⚙️ Store Management" button or admin navigation links appear in the footer, header, or body, and that query parameters like `?admin=true` do not expose any back-office control panel.

**Acceptance Scenarios**:

1. **Given** a shopper visits `http://localhost:8501`, **When** they scroll to the bottom of the page, **Then** only customer service details, legal copyright, warranty information, and toll-free helpline are displayed in the footer with zero admin or store management buttons.
2. **Given** a visitor navigates to `http://localhost:8501/?admin=true`, **When** the page renders, **Then** the application stays on the primary storefront without switching to or exposing an administrative data upload or database management dashboard.

---

### User Story 2 - Preserved Automated Data Integrity & Seeding (Priority: P2)

As a store operator or automated test runner, I want catalog data to remain automatically seeded and accessible through standard CLI and test harnesses, so that removing the admin web UI does not impair catalog availability or test suites.

**Why this priority**: Ensures zero regressions in store catalog functionality, MongoDB connectivity, and existing automated test suites.

**Independent Test**: Run test suite (`pytest -v tests/`). Verify all 22 tests pass and that automatic seeding on launch continues to populate products and policies if the database is unpopulated.

**Acceptance Scenarios**:

1. **Given** a fresh or empty database, **When** the application starts up, **Then** catalog products, FAQs, and store policies are automatically loaded and displayed on the storefront without needing manual admin intervention.
2. **Given** existing test suites (`tests/test_import.py`), **When** tests execute, **Then** backend validation and ingestion services continue to function flawlessly.

---

### Edge Cases

- **Direct Admin URL Access**: What happens when a user attempts to access `?admin=true` or an admin route? The system should ignore the parameter and seamlessly present the standard storefront view without raising errors or showing broken containers.
- **Empty Database Fallback**: How does the storefront behave if MongoDB is unseeded? The background auto-seeder (`auto_seed_default_catalog()`) handles initialization silently; if all data sources are missing, a helpful customer notice is displayed advising the user that the catalog is updating.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST NOT render the "⚙️ Store Management" button or any administrative toggle in the storefront footer or layout.
- **FR-002**: System MUST NOT render the Admin Control Center / Store Management Center view within the customer-facing web application.
- **FR-003**: System MUST remove the `admin_mode` state switching logic from the main application flow, ensuring all visits default exclusively to the laptop storefront.
- **FR-004**: System MUST maintain all existing product catalog browsing, dynamic search, multi-filter attributes, deal shelves, and the viewport-fixed floating AI assistant without regression.
- **FR-005**: System MUST preserve backend file processing, validation, and ingestion services (`FileProcessor`, `DataValidator`, `DataImporter`, `KnowledgeBaseService`) and CLI tooling (`import_data.py`) so programmatic imports and unit tests remain operational.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of visible storefront UI elements are dedicated exclusively to customer shopping, product search, policies, and AI assistance (zero administrative controls visible).
- **SC-002**: Passing 100% of the automated test suite (22/22 tests passing) with zero regressions in catalog retrieval or data validation.
- **SC-003**: Customer page load completes cleanly without secondary conditional render branches or admin mode re-renders.

## Assumptions

- Auto-seeding mechanism (`auto_seed_default_catalog()`) remains in `app.py` to ensure the storefront is always fully populated on first startup without requiring manual CSV upload.
- Admin dashboard components in `frontend/admin_dashboard.py` can remain in the codebase as a standalone module for developer/internal use without being mounted to the main web app flow.
- No authentication or role-based access control was requested; complete removal of the customer-facing admin toggle satisfies the requirement.
