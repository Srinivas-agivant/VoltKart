# Feature Specification: VoltKart - AI Customer Support & Product Recommendation Agent

**Feature Branch**: `001-voltkart-agent`

**Created**: 2026-11-19

**Status**: Draft

**Input**: User description: "VoltKart - AI Customer Support and Product Recommendation Agent. An intelligent chatbot for a fictional online laptop store allowing administrators to upload datasets (CSV/Excel) containing laptops, FAQs, and policies, and enabling customers to interact through a conversational interface with grounded recommendations, comparisons, and policy answers."

## Clarifications

### Session 2026-11-19
- Q: Duplicate Record Ingestion Strategy → A: Option A (Admin Mode Selection: "Skip existing duplicates" by default or "Update/replace existing records", reporting exact counts for inserted, updated, and skipped records).
- Q: Gemini API Failure & Fallback Strategy → A: Option A (Direct MongoDB keyword/regex retrieval fallback with a graceful degraded banner when Gemini encounters rate limits or errors, ensuring zero dead-ends).
- Q: Dynamic Column Mapping Strategy → A: Option A (Smart auto-mapping using predefined column aliases with Streamlit selectbox overrides for ambiguous headers, followed by validation preview).
- Q: Product Recommendation Ranking Heuristic → A: Option A (Deterministic Python scoring based on budget proximity and feature weighting before passing top 2–3 items to Gemini for personalized explanation generation).
- Q: Multi-Turn Conversation Management in Streamlit UI → A: Option A (Sidebar session history displaying past conversations with a "+ New Chat" button, reloading messages and recommendation positions from MongoDB into session state).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Personalized Laptop Recommendations (Priority: P1)

A shopper visits the VoltKart storefront looking for a laptop suited to their specific needs (e.g., "I need a lightweight laptop for college under Rs. 60,000 with strong battery life"). The assistant understands the shopper's constraints, searches the catalog for matching laptops, and presents 2–3 best-matched recommendations. Each recommendation includes clear specifications, price, and a personalized explanation of why it fits the shopper's criteria.

**Why this priority**: Recommendations directly drive product discovery, customer decision-making, and store sales. This is the core shopping value proposition of VoltKart.

**Independent Test**: Provide customer requirements specifying budget, usage type, and key hardware preferences. Verify the assistant returns 2–3 verified catalog laptops with accurate specs and explicit justification, and never invents uncataloged models.

**Acceptance Scenarios**:

1. **Given** a customer query with a budget limit and specific use case (e.g., student, coding, gaming), **When** the query is submitted, **Then** the system presents 2 to 3 matching laptops from the store catalog with clear pricing, core specs, and a tailored recommendation rationale.
2. **Given** a customer query whose criteria match no catalog laptops (e.g., ultra-high-end gaming specs under a very low budget), **When** the query is submitted, **Then** the system clearly communicates that no exact matches exist and suggests adjusting budget or hardware preferences without hallucinating non-existent models.
3. **Given** a recommendation response, **When** presented to the user, **Then** each recommended product displays its name, brand, price, processor, RAM, storage, display size/resolution, graphics, weight, battery life, and warranty.

---

### User Story 2 - Store Policy & FAQ Customer Support (Priority: P1)

A shopper asks questions about store operations, such as return windows, refund procedures, warranty coverage, shipping times, or payment methods. The assistant retrieves relevant store policy documents and FAQs and provides a direct, easy-to-read answer. If a policy is not defined in the store records (such as an unlisted EMI option), the assistant honestly states that the information is unavailable rather than guessing.

**Why this priority**: Reliable customer support builds buyer trust and prevents post-purchase disputes. Strict adherence to verified policies protects store credibility.

**Independent Test**: Ask policy questions that are documented in the store knowledge base (e.g., "What is the return policy?") and unlisted questions (e.g., "Do you offer international shipping?"). Verify documented policies are answered accurately and unlisted policies are gracefully declined.

**Acceptance Scenarios**:

1. **Given** an inquiry about a documented store policy (e.g., 7-day return policy), **When** the customer asks, **Then** the assistant provides an accurate explanation matching store policy documentation.
2. **Given** an inquiry about an undocumented service or policy (e.g., zero-cost EMI or trade-in program not offered), **When** the customer asks, **Then** the assistant states that the store does not currently provide or have information on that service.
3. **Given** a combined inquiry (e.g., "Can I return a gaming laptop within 10 days?"), **When** the customer asks, **Then** the assistant explains the specific category return rules based strictly on stored policy records.

---

### User Story 3 - Admin Catalog & Knowledge Base Ingestion (Priority: P2)

A store administrator needs to update the store catalog, FAQs, or store policies by uploading tabular data files (spreadsheets or comma-separated files). The administrator selects the dataset type, previews uploaded columns, maps columns if necessary, reviews validation results for invalid or missing data, and confirms the import. The system inserts valid records, prevents duplicate imports, and reports exact import counts.

**Why this priority**: Store data changes regularly. A self-service ingestion workflow ensures the assistant always operates on current, accurate catalog and policy data without requiring code changes.

**Independent Test**: Upload sample product catalog files containing valid rows, duplicate rows, and invalid rows (e.g., negative prices or missing required names). Verify validation catches errors and reports correct import counts.

**Acceptance Scenarios**:

1. **Given** a valid spreadsheet containing new laptop models, **When** the administrator uploads and confirms the import, **Then** the records are added to the store catalog and immediately become available for customer recommendations.
2. **Given** an uploaded file with alternative column headers (e.g., "Cost" or "MRP" instead of "Price"), **When** uploaded, **Then** the system automatically maps recognized aliases and provides interactive dropdown overrides for any ambiguous columns before validating the data.
3. **Given** an uploaded file containing duplicate records previously imported, **When** processed, **Then** the system adheres to the selected mode (skipping duplicates by default or updating existing on administrator choice) and reports accurate counts for inserted, updated, and skipped records.
4. **Given** an upload containing missing mandatory fields or invalid data types (e.g., non-numeric price), **When** validated, **Then** invalid rows are flagged with descriptive error feedback and valid rows can still be processed.

---

### User Story 4 - Multi-Turn Product Comparison & Follow-Up Context (Priority: P2)

After receiving recommendations, a shopper asks follow-up questions referencing previous turns, such as "Compare the first two laptops", "Show me something lighter", or "Which one has better battery life?". The assistant recalls the active conversation context, identifies which specific products were referenced, retrieves their detailed specifications, and provides a side-by-side comparison table along with an objective verdict.

**Why this priority**: Real shopping conversations are conversational and iterative. Shoppers need to compare trade-offs before committing to a purchase.

**Independent Test**: Request recommendations, then ask "Compare the first two" followed by "Which one is better for battery life?". Verify the assistant correctly resolves "the first two" to the actual previous recommendations and displays structured comparisons.

**Acceptance Scenarios**:

1. **Given** a conversation where 3 laptops were recommended, **When** the user asks "Compare the first two", **Then** the assistant displays a structured side-by-side comparison of both laptops across price, performance, memory, storage, display, graphics, weight, and battery life.
2. **Given** a comparison request, **When** comparing the attributes, **Then** the assistant delivers an objective summary highlighting which laptop excels in specific dimensions (e.g., battery vs. processing speed) based solely on catalog specs.
3. **Given** a follow-up refinement (e.g., "Are there any cheaper options among these?"), **When** asked, **Then** the assistant references the previously discussed options and provides appropriate alternatives.

---

### User Story 5 - Store Scope Enforcement & Out-of-Scope Inquiries (Priority: P3)

A shopper asks about products or services not sold by VoltKart (e.g., smartphones, smartwatches, household appliances, or general trivia). The assistant politely explains that VoltKart is an exclusive laptop retailer and redirects the user to explore available laptop models or laptop-related services.

**Why this priority**: Keeps the customer focused on available store inventory and prevents the assistant from engaging in irrelevant or uncontrolled topics.

**Independent Test**: Ask questions about mobile phones or general trivia. Verify the assistant responds with polite scope boundaries and invites laptop inquiries.

**Acceptance Scenarios**:

1. **Given** a question about non-laptop consumer electronics (e.g., "Do you sell iPhone 15 Pro?"), **When** the shopper asks, **Then** the assistant politely states that VoltKart exclusively specializes in laptops and offers to assist with laptop options.
2. **Given** an open-ended unrelated question (e.g., "What is the capital of France?"), **When** the shopper asks, **Then** the assistant redirects the conversation back to laptop recommendations and store support.

---

### Edge Cases

- **Zero Matching Products**: When a customer's query specifies mutually contradictory criteria (e.g., budget under Rs. 20,000 with a dedicated high-end GPU), the system must not fabricate a non-existent laptop or recommend vastly out-of-budget options without explicit notice. It must state that no laptops match and highlight which criteria are restrictive.
- **Corrupted or Incompatible Ingestion Files**: When an administrator uploads a corrupted file, empty file, or unsupported file format, the system must reject the file gracefully with a clear human-readable error rather than failing unhandled.
- **Premature Comparison Request**: If a customer starts a new session and immediately says "Compare the first two laptops" before any recommendations were generated, the system must recognize that no products have been recommended yet and prompt the user for their requirements.
- **Ambiguous Multi-Intent Messages**: If a user submits a compound query (e.g., "What is your warranty policy, and can you show me a Dell laptop under Rs. 50,000?"), the system must identify both intents, retrieve both policy and catalog records, and provide a coordinated response addressing both aspects.
- **Service Availability & Rate Limit Interruptions**: If the external AI service times out, returns malformed output, or encounters rate limits (HTTP 429), the system must seamlessly fall back to direct keyword and filter querying against MongoDB (matching budget digits, brand names, or policy keywords), presenting matching catalog cards or FAQ answers under an informational degraded mode notice without crashing or losing session context.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a dedicated conversational customer storefront interface featuring branded header, sidebar conversation history with a "+ New Chat" button, chat timeline, suggestion chips, and responsive input.
- **FR-002**: System MUST interpret customer inquiries to extract structured shopping requirements (including target budget, preferred brand, intended usage, processor type, minimum RAM, storage capacity, display size, weight preference, and battery requirements).
- **FR-003**: System MUST retrieve matching laptop catalog records from the persistent store based on extracted requirements, score candidates using a deterministic Python ranking heuristic (prioritizing budget proximity and spec feature match), and select the top 2–3 best-fit options.
- **FR-004**: System MUST display recommended products with full specification details (Product Name, Brand, Price, Processor, RAM, Storage, Display, Graphics, Weight, Battery Life, Warranty) and an explicit recommendation reason.
- **FR-005**: System MUST maintain multi-turn conversation memory across sessions in persistent storage, enabling customers to reference previously recommended laptops by relative position (e.g., "the first one", "the second laptop", "both of them") and reload past conversations from the sidebar into active session state.
- **FR-006**: System MUST generate structured side-by-side comparison tables when customers request a comparison between two or more catalog products.
- **FR-007**: System MUST answer store policy and customer service questions (returns, refunds, warranty, shipping, payments) strictly using verified store FAQ and policy records.
- **FR-008**: System MUST enforce a non-negotiable zero-hallucination constraint: factual claims, product specifications, prices, stock availability, and store policies MUST originate from verified stored records. If information is not in store records, the system MUST state that it is unavailable.
- **FR-009**: System MUST support administrator file uploads in `.csv`, `.xlsx`, and `.xls` formats for dataset categories: Laptops, FAQs, and Store Policies.
- **FR-010**: System MUST provide smart column auto-mapping using predefined aliases with interactive dropdown selectbox overrides during file upload to support varying source header names.
- **FR-011**: System MUST validate uploaded records for mandatory fields, numeric constraints, and proper formatting before saving to the persistent store.
- **FR-012**: System MUST detect duplicate records using stable record identifiers (`product_id`, `faq_id`, `policy_id`) and provide an administrative mode toggle ("Skip duplicates" by default, or "Update/replace existing records"), reporting exact counts for inserted, updated, and skipped records in the ingestion audit log.
- **FR-013**: System MUST record ingestion audit metadata, including source filename, record counts (total, successful, failed), and import timestamp.
- **FR-014**: System MUST politely decline and redirect customer queries regarding products outside the store's laptop domain.
- **FR-015**: System MUST provide a "+ New Chat" button and clear chat action to instantly reset the active session state and start a fresh conversation with a new identifier.
- **FR-016**: System MUST execute a direct database keyword/regex retrieval fallback with an informational notice if the external language model experiences timeouts, unparseable output, or rate limits.

### Key Entities *(include if feature involves data)*

- **Product**: Represents a laptop available in the store catalog. Key attributes: Product Identifier, Name, Brand, Price, Processor, RAM, Storage, Display, Graphics, Weight, Battery Life, Warranty, Intended Usage Category, Specifications dictionary, Source File, and Creation/Update Timestamps.
- **FAQ**: Represents a common customer support inquiry and official answer. Key attributes: FAQ Identifier, Category, Question, Answer, Keywords list, Source File, and Creation Timestamp.
- **Store Policy**: Represents an official store operating policy. Key attributes: Policy Identifier, Category (e.g., Return, Warranty, Shipping), Title, Detailed Description, Keywords list, Source File, and Creation Timestamp.
- **Conversation Session**: Represents an active customer chat session. Key attributes: Conversation Identifier, Session Title, Creation Timestamp, and Last Updated Timestamp.
- **Message Turn**: Represents an individual message in a conversation. Key attributes: Message Identifier, Conversation Reference, Role (Customer or Assistant), Message Content, Detected Intent, Referenced Product/Policy Identifiers, and Timestamp.
- **Recommendation Record**: Tracks recommendations delivered in a turn for context continuity. Key attributes: Conversation Reference, Product Reference, Display Position (e.g., 1, 2, 3), Personalized Reason, and Timestamp.
- **Ingestion Audit Log**: Represents an administrator upload batch. Key attributes: Batch Identifier, Source Filename, Dataset Category, Total Records Count, Inserted Records Count, Updated Records Count, Skipped Duplicates Count, Failed Records Count, Import Status, and Timestamp.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of factual laptop attributes, prices, and store policies stated by the assistant match stored catalog records (0% fabricated specifications or hallucinated store policies across all tested interactions).
- **SC-002**: Product recommendation queries return 2–3 relevant, catalog-grounded laptop recommendations with complete specification cards in under 3.5 seconds end-to-end.
- **SC-003**: 100% of multi-turn comparison queries (e.g., "Compare the first two") accurately resolve the referenced items from preceding recommendation turns.
- **SC-004**: Administrative file ingestion validates, deduplicates, and imports a 100-record dataset in under 15 seconds with comprehensive error reporting on malformed rows.
- **SC-005**: 100% of out-of-scope inquiries (e.g., smartphones, smartwatches, general trivia) are politely redirected to laptop inquiries without generating fake non-laptop listings.
- **SC-006**: First-time users can successfully navigate from an initial budget query to comparing two recommended laptops in fewer than 3 conversational turns.

## Assumptions

- **Synthetic Data**: In compliance with hackathon standards, all catalog items, customer names, order references, and store policies are synthetic.
- **Language Scope**: The initial release is designed and tested for English-language shopping and support interactions.
- **Catalog Domain**: VoltKart specializes exclusively in laptop computers, laptop accessories, and related store policies. Non-laptop products are out of scope.
- **Administrative Access**: File ingestion is conducted in a designated administrative view within the application; complex multi-user role-based permissions are deferred beyond the MVP.
- **Direct Store Operations**: Real-time payment gateway processing and live courier API tracking are simulated through catalog policy explanations for the hackathon MVP.
