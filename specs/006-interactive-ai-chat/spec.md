# Feature Specification: Interactive AI Shopping Assistant

**Feature Branch**: `006-interactive-ai-chat`

**Created**: 2026-11-19

**Status**: Draft

**Input**: User description: "make sure the ai chat is interactive"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - One-Click Interactive Inquiries & Prompt Chips (Priority: P1)

Shoppers on VoltKart want immediate, friction-free assistance without having to manually formulate or type lengthy technical specifications. When a customer opens the AI assistant or views the prompt area, they can click ready-made prompt chips (such as student laptops under ₹50,000, coding laptops under ₹70,000, gaming laptops, or return policies) and instantly receive tailored, verified recommendations or policy answers in the conversation timeline.

**Why this priority**: First-time visitors and mobile or quick-browse customers rely on prompt chips to understand what the assistant can do and get instant value with a single click.

**Independent Test**: Open the assistant on the storefront, click the "🎒 Student < ₹50k" prompt chip, and verify that the user query is submitted automatically, displaying verified student laptops with specs and pricing within 2 seconds.

**Acceptance Scenarios**:
1. **Given** the assistant is open, **When** the user clicks any suggestion chip, **Then** the chip's text is submitted as the customer's query, displayed in the chat log, and answered with grounded store data.
2. **Given** a response is rendered, **When** the user clicks a different suggestion chip, **Then** a new turn is appended with the corresponding results without wiping previous turns.
3. **Given** the user is viewing the chat panel, **When** they type a custom query into the input field and press send, **Then** the custom query is processed and answered identically in quality to pre-set chips.

---

### User Story 2 - Multi-Turn Contextual Follow-Ups & Memory (Priority: P1)

Shoppers frequently evaluate laptops across several conversational turns. After the assistant suggests two or three laptops, the customer can ask context-dependent follow-up questions (such as "Which one has the best battery life?", "Compare the first two", "Do any of them have 16GB of RAM?", or "Are there any cheaper alternatives?"). The assistant remembers the previous laptops discussed and answers accurately based on verified store specifications.

**Why this priority**: A truly interactive assistant must maintain continuity; without memory, the customer is forced to re-type full model names and budget criteria every single turn.

**Independent Test**: Ask for "laptops under ₹60,000", receive recommendations, and then ask "Which one has the longest battery life?". Verify the response directly compares the battery life of the laptops recommended in the preceding turn.

**Acceptance Scenarios**:
1. **Given** a previous turn recommending laptops, **When** the user asks a follow-up referring to "the first one" or "which is cheaper", **Then** the assistant accurately resolves the reference to the specific laptop and answers using its verified specifications.
2. **Given** a user asks to compare previously recommended laptops, **When** the prompt is submitted, **Then** the assistant provides a structured side-by-side comparison of their key specifications (processor, RAM, storage, battery, display, and price).
3. **Given** an ongoing conversation, **When** the user navigates between store pages (e.g., Home, About Us, Contact), **Then** the conversation history and context remain intact when reopening or viewing the assistant.

---

### User Story 3 - Interactive Store Support & Policy Q&A (Priority: P2)

Customers need direct, conversational answers about store operations, shipping times, return windows, and warranty terms. When a customer asks a support question like "Do you offer free shipping?" or "What is your return policy?", the assistant provides a concise, direct answer synthesized from verified store documentation, avoiding generic evasions or raw file dumps.

**Why this priority**: Clear and interactive customer service builds trust and prevents cart abandonment due to unanswered logistical concerns.

**Independent Test**: Ask "What is your return policy and do you provide free shipping?", and verify that the assistant provides explicit answers (e.g., 30-day return policy and free standard shipping on all laptops) verified from store documentation.

**Acceptance Scenarios**:
1. **Given** a customer asks about shipping, returns, or warranty, **When** the query is evaluated, **Then** the assistant responds with direct answers grounded in official store documentation.
2. **Given** a customer asks a question combining policy and product inquiries (e.g., "What warranty comes with the GameForce 15?"), **When** the query is processed, **Then** the assistant answers both the product-specific warranty and general store coverage.

---

### User Story 4 - Session Management & Interactive Controls (Priority: P2)

Shoppers need intuitive controls to manage their shopping consultation: minimizing/maximizing the assistant smoothly, clearing or restarting the conversation when starting a new shopping search, and receiving clear visual feedback (loading status) while verified answers are being prepared.

**Why this priority**: Clear controls ensure the assistant does not block the storefront, does not freeze the screen, and allows shoppers to reset their consultation when shifting goals.

**Independent Test**: Open the assistant, send queries, click the close/minimize button, verify the assistant collapses cleanly to its floating icon, reopen it, and verify history is retained; then click a "New Chat / Reset" control to start fresh.

**Acceptance Scenarios**:
1. **Given** the assistant is open, **When** the user clicks the close/minimize control, **Then** the window closes smoothly and the floating launcher icon remains visible at the fixed bottom-right.
2. **Given** the user triggers a query, **When** data retrieval and response synthesis are in progress, **Then** an active processing indicator is shown so the user knows the assistant is working.
3. **Given** an active chat, **When** the user initiates a session reset, **Then** previous messages are cleared from view and the friendly initial greeting with quick suggestions is restored.

---

### Edge Cases

- **Rapid Multiple Clicks**: If a customer clicks multiple suggestion chips or presses enter rapidly, the system must process requests sequentially without creating corrupted duplicate turns or crashing.
- **Empty / Whitespace Queries**: Submitting blank or whitespace-only inputs must be ignored without sending network requests or adding blank bubbles.
- **Unlisted / Unknown Product Names**: If a user asks about a laptop brand or model not carried by the store (e.g., "Do you have MacBook Pro?"), the assistant must politely state that the item is not in VoltKart's catalog and offer the closest available store match based on user needs.
- **Out-of-Scope Inquiries**: If a user asks about unrelated topics (e.g., weather, politics, cooking recipes), the assistant must politely redirect the customer back to laptop shopping and store policies.
- **Storefront Page Navigation**: Switching between pages must not reset active session memory unless the user explicitly restarts the conversation or refreshes their browser.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The assistant MUST provide clickable prompt chips that immediately trigger grounded search and recommendation queries upon selection.
- **FR-002**: The assistant MUST retain multi-turn dialogue history within the current customer visit, allowing pronouns and ordinal references ("the first one", "the cheaper laptop", "both of them") to resolve to previously mentioned catalog products.
- **FR-003**: All product information (names, prices, processors, RAM, storage, battery life, graphics, displays) presented in the assistant MUST match verified database catalog records exactly.
- **FR-004**: The assistant MUST support structured multi-laptop comparisons upon user request, comparing key technical specifications and pricing side by side.
- **FR-005**: The assistant MUST answer store support inquiries (shipping, delivery times, return window, warranty coverage) strictly from verified store knowledge records.
- **FR-006**: The assistant MUST display distinct, legible user and assistant message containers with clear visual separation.
- **FR-007**: The assistant MUST display an active progress indicator while searching the catalog and generating responses.
- **FR-008**: The assistant MUST provide a control to reset or start a new conversation session, restoring the initial welcome state.
- **FR-009**: The assistant MUST remain persistently accessible at a fixed viewport location across all storefront pages without obstructing navigation.
- **FR-010**: The assistant MUST gracefully reject non-retail or out-of-scope queries with a polite explanation and guidance toward laptop exploration.
- **FR-011**: The assistant MUST present recommended laptops in a compact, readable format that fits within the assistant panel without horizontal overflow or text clipping.
- **FR-012**: The assistant MUST allow users to seamlessly combine manual text entry with quick suggestion chips throughout the conversation.

### Key Entities *(include if feature involves data)*

- **Catalog Laptop**: The verified product record containing exact model name, brand, retail price, target usage category, and technical specifications (processor, RAM, storage, display, graphics, battery, warranty).
- **Chat Session**: A customer interaction session containing a unique session identifier, creation timestamp, and sequential message turns.
- **Message Turn**: A discrete communication event with a role (customer or assistant), textual content, timestamp, detected shopping intent, and optional associated catalog product references.
- **Store Policy Knowledge**: Verified store documentation covering shipping terms, delivery timeframes, return policies, warranty terms, and order handling rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of product names, prices, and specifications returned in chat responses match verified catalog records without synthetic invention or hallucination.
- **SC-002**: Clicking any suggestion chip triggers a complete, grounded response delivered to the customer in under 3 seconds.
- **SC-003**: In multi-turn dialogue tests, the assistant accurately resolves ordinal and comparative references (e.g., "compare the first two") to the correct products in 100% of standard test scenarios.
- **SC-004**: Customer queries regarding store policies (shipping, returns, warranty) receive accurate answers matching store documentation in 100% of test cases.
- **SC-005**: The assistant widget remains fixed, responsive, and legible on both full-screen desktop viewports and standard laptop screens without breaking storefront page layout.

## Assumptions

- The store catalog consists of genuine, verified laptop records currently maintained in the primary database.
- Store policy answers are grounded in the verified store FAQ and policy knowledge base.
- Users interact via standard modern web browsers on desktop and laptop devices.
- Network connectivity to the primary database and inference service remains stable during active shopping sessions.
