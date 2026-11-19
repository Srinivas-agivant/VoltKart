# Feature Specification: VoltKart Storefront, Floating AI Chatbot & PDF Knowledge Base

**Feature Branch**: `002-storefront-pdf-chatbot`

**Created**: 2026-11-19

**Status**: Draft

**Input**: User description: "Update existing completed VoltKart project. Preserve all existing working features, database connections, and services. Build a modern e-commerce storefront homepage for laptops with search, multi-faceted filters, and product cards. Add a floating bottom-right VoltKart AI Chatbot widget available across the storefront. Add an admin section for multi-page PDF knowledge base ingestion (FAQs, policies, product docs) with text extraction, chunking, and metadata tracking in MongoDB. Ground AI responses in both structured catalog and unstructured PDF knowledge base chunks."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - E-Commerce Storefront Browsing & Filtering (Priority: P1)

A shopper visits the VoltKart homepage to browse and purchase laptop computers. The homepage presents a branded navigation bar (Home, Laptops, About Us, Contact) and a hero banner ("Find Your Perfect Laptop"). Shoppers can search laptops in real-time by model name or brand, and filter the catalog using multi-faceted controls (Brand selection, interactive Price Range slider, RAM capacity, and Processor family). Products are presented in responsive, visually polished product cards showing images/badges, name, brand, formatted price in INR, and core specifications (CPU, RAM, Storage, Graphics, Battery). Shoppers can click "View Details" on any laptop to view full technical specifications.

**Why this priority**: An engaging, interactive storefront transforms VoltKart from a backend chat tool into a complete e-commerce destination where customers can independently explore inventory.

**Independent Test**: Load the storefront homepage, perform a search query (e.g., "ThinkPad" or "HP"), apply a price and RAM filter (e.g., $\le$ ₹60,000, 16GB RAM), and click "View Details". Verify only matching laptops from the live MongoDB database are displayed and full specs open cleanly.

**Acceptance Scenarios**:

1. **Given** the storefront homepage is loaded, **When** viewed by a customer, **Then** it renders a branded header, navigation links (Home, Laptops, About Us, Contact), a hero section with "Find Your Perfect Laptop", and a grid of laptop product cards retrieved dynamically from MongoDB.
2. **Given** a customer typing in the search bar, **When** they type a brand (e.g., "Asus") or model name, **Then** the product grid immediately updates to display only matching laptops.
3. **Given** multi-faceted sidebar/top filters (Brand, Price Range, RAM, Processor), **When** a shopper adjusts filter values, **Then** the catalog displays only laptops matching all selected filter criteria simultaneously.
4. **Given** a product card, **When** the shopper clicks "View Details", **Then** an expanded view displays comprehensive hardware specifications (processor, RAM, storage, display resolution, graphics chip, weight, battery life, warranty terms).
5. **Given** catalog data, **When** rendered, **Then** only laptop products are displayed; non-laptop electronics (phones, TVs) are strictly excluded.

---

### User Story 2 - Floating AI Assistant Chatbot (Priority: P1)

While browsing any section of the VoltKart storefront, a customer sees a floating chat trigger button anchored at the bottom-right corner of their screen. Clicking the trigger opens a floating conversational panel titled "VoltKart AI Assistant". The chat opens with a warm welcome: *"Hi! Welcome to VoltKart. I'm your AI shopping assistant. How can I help you today?"*. The customer can ask questions about laptop specifications, request personalized recommendations, compare laptops, or check store policies. The customer can minimize or close the chat window at any time without losing their ongoing session dialogue.

**Why this priority**: A persistent floating widget provides contextual assistance without forcing the customer to leave the shopping page.

**Independent Test**: Click the floating chat trigger at the bottom-right corner. Verify the window opens with the standard greeting, submit a recommendation question, verify the response appears in conversational timeline format, minimize the window, reopen it, and confirm the conversation history is preserved.

**Acceptance Scenarios**:

1. **Given** any storefront page, **When** viewed, **Then** an interactive floating chat button is displayed at the bottom-right corner.
2. **Given** the floating chat icon, **When** clicked, **Then** an overlay chat window opens displaying "VoltKart AI Assistant" and the initial greeting: *"Hi! Welcome to VoltKart. I'm your AI shopping assistant. How can I help you today?"*.
3. **Given** an open chat window, **When** the customer submits a query, **Then** the assistant streams or displays the grounded response in conversational dialogue format.
4. **Given** an active chat conversation, **When** the customer minimizes or closes the chat window and reopens it during the same session, **Then** the dialogue history and previously recommended products remain fully intact.

---

### User Story 3 - PDF Knowledge Base Ingestion & Management (Priority: P2)

A store administrator uploads official PDF documents (e.g., FAQs, Product Documentation, Return Policies, Warranty Policies, Shipping Guidelines, or general store literature) in the Admin Control Center. The administrator selects the document category, uploads a multi-page PDF, and initiates ingestion. The system extracts text from all pages, divides the text into overlapping chunks (e.g., 500 characters with 100-character overlap), generates a unique chunk ID and content hash, and stores the chunks with rich metadata (filename, category, page number, upload date) in the MongoDB `knowledge_base` collection. Administrators can view, inspect, and delete or replace previously uploaded documents.

**Why this priority**: Official store policies and detailed technical documentation frequently exist in PDF format. Automated extraction and chunking enable RAG-style factual grounding without manual data entry.

**Independent Test**: In the Admin Dashboard, navigate to the Document Ingestion section, select "Return Policy", upload a multi-page PDF document, and click "Extract & Store". Verify the system reports total pages and chunks created, stores the chunks in MongoDB `knowledge_base`, and displays the document in the uploaded documents list with an option to delete it.

**Acceptance Scenarios**:

1. **Given** a multi-page PDF file uploaded by an administrator, **When** processed, **Then** the system extracts text across all pages, handles multi-page continuity, and splits the content into overlapping chunks.
2. **Given** extracted text chunks, **When** stored in MongoDB, **Then** each chunk record stores `chunk_id`, `filename`, `category`, `page_number`, `chunk_text`, `content_hash`, and `created_at`.
3. **Given** a PDF document that was already ingested, **When** uploaded again with the same content, **Then** duplicate chunk ingestion is prevented.
4. **Given** the Knowledge Base manager view, **When** an administrator reviews uploaded documents, **Then** it lists all distinct document filenames with page counts and provides an action to delete or replace the document and its associated chunks.

---

### User Story 4 - Grounded Search Across Catalog & Knowledge Base (Priority: P2)

When a customer asks a question through the floating chatbot regarding store policies, return windows, warranty terms, or technical laptop specifications, the system conducts a hybrid retrieval search against both structured collections (`products`, `faqs`, `store_policies`) and the unstructured `knowledge_base` PDF chunks. The top-matching verified text excerpts are retrieved and provided to the language model. The assistant generates a factual, natural-language response based strictly on those records. If the requested information is absent from store documents, the assistant honestly explains that the store documents do not contain that information.

**Why this priority**: Guarantees complete information grounding across both structured tables and unstructured documents while strictly upholding the non-negotiable zero-hallucination policy.

**Independent Test**: Query a specific policy contained only in an ingested PDF document (e.g., "What are the rules for returning a damaged laptop packaging?"). Verify the answer is generated strictly from the PDF chunk text, and confirm unlisted questions (e.g., "Do you offer international warranty in Europe?") return an honest "information unavailable" message.

**Acceptance Scenarios**:

1. **Given** a customer query relating to store policy or technical documentation, **When** processed, **Then** the system searches MongoDB `knowledge_base` and policy collections and retrieves the most relevant text chunks.
2. **Given** retrieved knowledge base chunks, **When** passed to the language model, **Then** the response is synthesized strictly using the retrieved excerpts without inventing terms.
3. **Given** an inquiry about a topic absent from both the catalog and knowledge base, **When** submitted, **Then** the assistant states honestly that the information is unavailable in store documents.

---

### User Story 5 - Multi-Turn Recommendations, Comparisons & Follow-Up Context (Priority: P2)

A customer interacting with the floating chatbot asks for tailored laptop recommendations (e.g., *"I need a laptop for college under ₹60,000 with good battery life"*). The assistant recommends 2–3 matching laptops from MongoDB, explaining why each fits their needs. The customer can ask conversational follow-up questions referencing previous turns (e.g., *"Compare the first two"*, *"Anything lighter?"*, *"Which has better battery life?"*). The assistant maintains context, retrieves actual database specifications, and presents comparison matrices and advice.

**Why this priority**: Conversational continuity is critical for guiding shoppers through complex hardware comparisons and trade-offs.

**Independent Test**: Ask for laptops under ₹60,000 in the floating chat, then ask "Compare the first two", followed by "Anything lighter?". Verify the assistant correctly references the previously recommended items and provides accurate specification comparisons.

**Acceptance Scenarios**:

1. **Given** customer requirements (budget, usage, specs), **When** submitted, **Then** the assistant retrieves matching laptops from MongoDB and recommends 2–3 models with full specs and explanations.
2. **Given** an active conversation, **When** the customer asks "Compare the first two", **Then** the assistant generates a side-by-side comparison table using verified database attributes.
3. **Given** follow-up refinement questions (e.g., "Anything lighter?", "Which has better battery?"), **When** asked, **Then** the assistant evaluates the previously discussed laptops and recommends alternatives based on the new constraint.

---

### Edge Cases

- **Scanned or Image-Only PDFs**: If an uploaded PDF has no embedded text (e.g. scanned image pages), the system must detect that zero characters were extracted, alert the administrator with a clear notice, and refuse to save empty chunks.
- **Password-Protected or Corrupted PDFs**: The system must catch encryption or corrupt PDF exceptions cleanly, display a friendly error message, and prevent application crashes.
- **Simultaneous Search and Multi-Faceted Filters**: When a customer enters both a search keyword and adjusts price/RAM filters, the storefront grid must apply the conjunction (AND logic) of all active filters.
- **Zero Matching Storefront Results**: If filter combinations result in 0 matching laptops, the product grid must display a clean, helpful message ("No laptops match your selected filters") along with a one-click "Reset All Filters" button.
- **Mobile / Narrow Viewport Responsiveness**: The floating chatbot trigger and overlay window must fit cleanly on standard screen sizes without overflowing or blocking primary navigation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide an e-commerce storefront homepage featuring VoltKart branding, logo, navigation bar (Home, Laptops, About Us, Contact), and a hero section with the heading "Find Your Perfect Laptop".
- **FR-002**: System MUST render laptop products in responsive, card-based layouts dynamically populated from the MongoDB `products` collection.
- **FR-003**: System MUST provide real-time search functionality on the storefront to filter laptops by name or brand.
- **FR-004**: System MUST provide multi-faceted filtering options on the storefront for brand, price range, RAM capacity, and processor family.
- **FR-005**: System MUST include a "View Details" action on each product card that reveals comprehensive technical specifications (CPU, RAM, storage, display, graphics, weight, battery life, warranty).
- **FR-006**: System MUST restrict storefront listings strictly to laptop computers, excluding non-laptop electronic categories.
- **FR-007**: System MUST provide a floating AI chatbot widget anchored at the bottom-right corner of the storefront interface.
- **FR-008**: System MUST open a chat window upon clicking the floating icon with the standard welcome greeting: *"Hi! Welcome to VoltKart. I'm your AI shopping assistant. How can I help you today?"*.
- **FR-009**: System MUST allow users to minimize or close the floating chatbot window without losing active conversation history or recommendation state.
- **FR-010**: System MUST maintain multi-turn conversational context in the floating chat, enabling shoppers to ask follow-up questions ("Compare the first two", "Anything lighter?").
- **FR-011**: System MUST support administrative PDF document uploads for categories: FAQs, Product Catalogue, Return Policy, Warranty Policy, Shipping Policy, and Other Store Information.
- **FR-012**: System MUST extract text from uploaded multi-page PDFs using a Python PDF processing library.
- **FR-013**: System MUST split extracted PDF text into overlapping chunks and store each chunk in the MongoDB `knowledge_base` collection with metadata (chunk ID, filename, category, page number, upload timestamp, content hash).
- **FR-014**: System MUST prevent duplicate PDF chunk imports using content hashing.
- **FR-015**: System MUST allow administrators to view, inspect, and delete or replace previously uploaded PDF documents and their stored chunks.
- **FR-016**: System MUST retain existing CSV, XLSX, and XLS product data upload, validation, and dynamic column mapping workflows.
- **FR-017**: System MUST retrieve relevant text chunks from `knowledge_base` and records from `faqs`, `store_policies`, and `products` when answering user queries.
- **FR-018**: System MUST enforce strict zero-hallucination grounding: if information is absent from database records and knowledge base chunks, the assistant MUST state that the store documents do not contain that information.

### Key Entities *(include if feature involves data)*

- **Product**: Represents a laptop in the catalog (Product ID, Name, Brand, Price, Processor, RAM, Storage, Display, Graphics, Weight, Battery Life, Warranty, Usage Type, Specifications).
- **Knowledge Base Chunk**: Represents an extracted text segment from a store PDF document (Chunk ID, Filename, Category, Page Number, Chunk Text, Character Count, Content Hash, Created At).
- **Store Document Summary**: Aggregates metadata for an uploaded PDF (Filename, Category, Total Pages, Total Chunks, Upload Date).
- **FAQ & Store Policy**: Represents structured Q&A pairs and official policy articles.
- **Conversation Session & Messages**: Tracks customer chat turns, detected intents, referenced records/chunks, and timestamps.
- **Recommendation Record**: Tracks ordinal recommendation positions (1, 2, 3) for multi-turn relative referencing.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of product cards and specifications displayed on the storefront are retrieved dynamically from MongoDB (`voltkart_db`).
- **SC-002**: Multi-faceted filter adjustments and keyword searches update the storefront product grid in under 500 milliseconds.
- **SC-003**: 100% of factual answers generated by the floating chatbot (prices, specs, policies) match verified MongoDB catalog or knowledge base records (0% fabricated policies or specifications).
- **SC-004**: Multi-page PDF documents up to 20 pages are extracted, chunked, and stored in MongoDB in under 10 seconds with detailed chunk count reporting.
- **SC-005**: 100% of multi-turn relative comparison queries (e.g. "Compare the first two") accurately resolve the referenced laptops from preceding recommendation turns in the floating widget.
- **SC-006**: The floating chatbot widget is accessible across all storefront sections and maintains conversation state across minimize and maximize operations within a session.

## Assumptions

- **PDF Structure**: Uploaded PDFs contain digital text layers; scanned image-only PDFs require digital versions or will be rejected gracefully.
- **Styling**: Visual theme uses a professional navy blue (`#0f172a`), clean white (`#ffffff`), and light slate/grey (`#f8fafc`) aesthetic with modern card borders and typography.
- **Existing Assets**: The 25 synthetic laptops and sample policy datasets already created will remain active and seed the new storefront view.
- **PDF Extraction Engine**: Uses `pypdf` (lightweight, pure Python, zero system binary dependencies) for robust multi-page extraction.
