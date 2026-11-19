# Research & Technical Decisions: VoltKart AI Agent

**Feature**: VoltKart AI Customer Support & Product Recommendation Agent  
**Date**: 2026-11-19  
**Status**: Completed  

---

## 1. Two-Stage LLM Interaction Pattern (Intent $\rightarrow$ Retrieval $\rightarrow$ Generation)

### Context & Problem
We must ensure that the conversational agent never invents product specifications, prices, or store policies. Relying on a single-turn end-to-end LLM generation poses severe hallucination risks and makes verification impossible.

### Decision
Implement a strict **Two-Stage Decoupled LLM Architecture**:
1. **Stage 1 (Intent & Parameter Extraction)**: Customer message is sent to Google Gemini API configured with a structured JSON schema response (`response_schema` / `response_mime_type="application/json"`). Gemini classifies the intent (`recommend`, `support`, `compare`, `other`) and extracts structured parameters (budget limit, brand, RAM, storage, processor, usage type, target products).
2. **Python Retrieval Gate**: Pure Python backend validates extracted parameters and executes deterministic MongoDB queries via PyMongo. Gemini is NOT involved in database retrieval.
3. **Stage 2 (Grounded Response Generation)**: The retrieved database records (products or FAQ/policy documents) are injected into a strict system prompt instructing Gemini to answer using *only* the provided records. If records are empty, Gemini is constrained to state that the information or matching product is unavailable.

### Rationale
- Strictly enforces Constitution Principle VII (Strict Database Grounding) and Principle VIII (Zero-Hallucination Policy).
- Eliminates non-deterministic DB querying and prevents SQL/NoSQL injection risks.
- Allows deterministic logging and auditing of exactly which database records were referenced for every response.

### Alternatives Considered
- *Tool/Function Calling Agent (e.g., LangChain agent with DB tool)*: Rejected. Re-entrant agentic tool calling adds unpredictability, loop latency, and token overhead that threatens the 9-hour delivery window.
- *Single-Prompt Zero-Shot with Entire Catalog in Context*: Rejected. Context window costs, latency spikes, and severe catalog hallucination risks.

---

## 2. MongoDB Schema & PyMongo Query Patterns

### Context & Problem
The application requires storage for laptops, support documents, multi-turn chat history, and file import history. Queries must support range filtering (price $\le$ budget), exact matching (brand), text searches (FAQ keywords), and session tracking.

### Decision
Use MongoDB database `voltkart_db` with 7 dedicated collections:
1. `products`: Laptops with hardware attributes, normalized numeric fields (`price`, `ram_gb`, `storage_gb`, `battery_hours`, `weight_kg`), and compound indexes on `{ usage_type: 1, price: 1 }`, `{ brand: 1, price: 1 }`, and unique index on `product_id`.
2. `faqs`: Question/answer pairs with `category`, `keywords`, and text index on `question` and `keywords`.
3. `store_policies`: Policy articles (`category`, `title`, `description`) with text index.
4. `conversations`: Session tracking (`conversation_id`, `title`, `created_at`, `updated_at`).
5. `messages`: Turn-level chat messages (`conversation_id`, `role`, `content`, `intent`, `retrieved_record_ids`, `created_at`).
6. `recommendations`: Product positions per turn (`conversation_id`, `product_id`, `position`, `recommendation_reason`, `created_at`) for relative multi-turn referencing.
7. `import_history`: Batch audit log (`filename`, `dataset_type`, `total_records`, `inserted_records`, `updated_records`, `skipped_duplicates`, `failed_records`, `status`, `imported_at`).

### Rationale
- PyMongo offers direct, low-overhead connectivity with native dictionary serialization.
- Normalized numeric fields enable fast, clean range operators (`$lte`, `$gte`) without regex parsing on price strings.
- Storing `recommendations` with ordinal positions (`1`, `2`, `3`) makes resolving "compare the first two" trivial via direct database lookup.

### Alternatives Considered
- *SQL (SQLite / PostgreSQL)*: Rejected by Constitution (MongoDB is mandatory).
- *MongoEngine / ODM*: Rejected by Constitution Principle VI (Direct PyMongo Connectivity to avoid ORM complexity).

---

## 3. Tabular Data Ingestion & Dynamic Column Mapping

### Context & Problem
Admin users will upload `.csv`, `.xlsx`, and `.xls` files from various laptop distributors where column headers vary (e.g. `MRP` vs `Price`, `RAM_Size` vs `RAM`). Data must be validated before insertion.

### Decision
Build a reusable `FileProcessor` and `DataValidator` module using Pandas and OpenPyXL:
1. **Format Detection & Reading**: Read `.csv` via `pd.read_csv`, `.xlsx`/`.xls` via `pd.read_excel(..., engine="openpyxl")`.
2. **Dynamic Alias Dictionary**: Maintain a canonical alias map (e.g. `price` aliases: `mrp`, `cost`, `amount`, `rate`, `pricing`). Auto-detect matches case-insensitively.
3. **Interactive Streamlit Fallback**: For any unmatched required field, render Streamlit `st.selectbox` dropdowns populated with uploaded column headers so the admin can confirm mapping.
4. **Data Hygiene & Coercion**: Strip currency symbols (`₹`, `$`, `,`), extract numeric RAM/storage digits (e.g. "16 GB" $\rightarrow$ `16`), and validate mandatory non-null fields using Pydantic models.
5. **Deduplication Mode**: Compute content hash (MD5 of normalized product attributes) and check against `product_id`. Respect admin toggle ("Skip Duplicates" default vs "Update Existing").

### Rationale
- High reliability: Prevents malformed strings from breaking MongoDB queries.
- Meets Constitution Principle V (Pandas/OpenPyXL) and Principle XII (Pre-Insert Validation).

### Alternatives Considered
- *CSV standard library*: Lacks Excel support and vectorized data cleaning.
- *Strict column rejection*: Poor user experience for non-technical admins.

---

## 4. Deterministic Product Recommendation Ranking

### Context & Problem
When MongoDB query filters return multiple matching laptops (e.g., 5 to 10 candidates), we need a deterministic, explainable algorithm to select the best 2–3 laptops before prompting Gemini.

### Decision
Implement a pure Python weighted scoring algorithm:
$$\text{Score} = w_{\text{budget}} \cdot S_{\text{budget}} + w_{\text{ram}} \cdot S_{\text{ram}} + w_{\text{storage}} \cdot S_{\text{storage}} + w_{\text{battery}} \cdot S_{\text{battery}}$$
- **Budget Proximity**: For budget $B$ and laptop price $P \le B$, score ratio $\frac{P}{B}$ (rewards laptops utilizing the available budget to deliver maximum hardware capacity).
- **Spec Match**: Extra points awarded if RAM, storage, or dedicated GPU matches or exceeds requested thresholds.
- Top 3 highest-scoring laptops are selected and passed to Gemini with their specific winning factors highlighted.

### Rationale
- Fully deterministic and reproducible.
- Guarantees that only valid, in-stock, retrieved laptops are presented.
- Complies with Clarification Q4 resolution.

---

## 5. Multi-Turn Conversation Memory in Streamlit

### Context & Problem
Streamlit re-executes scripts top-to-bottom on each interaction. We need multi-turn context retention, sidebar history browsing, and relative product reference resolution ("compare the first two").

### Decision
1. **Session State + DB Synchronization**:
   - `st.session_state.messages`: In-memory list of active chat turns for instant UI rendering.
   - `st.session_state.conversation_id`: Active session UUID.
   - `st.session_state.last_recommendations`: Dictionary mapping position (`1`, `2`, `3`) to `product_id`.
2. **Persistent Storage**:
   - On every message, write user turn and assistant response into MongoDB `messages`.
   - On every recommendation, write positions into MongoDB `recommendations`.
3. **Sidebar History**:
   - Query MongoDB `conversations` sorted by `updated_at` descending.
   - Render conversation list with timestamps. Clicking an entry loads previous messages and recommended IDs from MongoDB into `st.session_state`.
   - "+ New Chat" button generates a new UUID and resets active UI state.
4. **Relative Reference Resolution**:
   - When Gemini detects intent `compare` with relative terms (`first two`, `laptop 1 and 3`), Python resolves positions against `st.session_state.last_recommendations` (or queries MongoDB `recommendations` for the active conversation), retrieves exact documents, and renders the comparison.

### Rationale
- Delivers a polished, ChatGPT-like interface natively in Streamlit.
- Ensures no loss of context across turns or page re-renders.

---

## 6. Fault Tolerance & Gemini API Fallback Strategy

### Context & Problem
During live demos, Gemini API rate limits, temporary timeouts, or network glitches can disrupt the presentation.

### Decision
Implement a resilient service wrapper with automatic fallback:
1. Wrap Gemini calls in `try/except` with a 5-second timeout.
2. If Gemini fails (timeout, rate limit 429, or invalid JSON output):
   - **Intent Fallback**: Python runs basic regex keyword matching on user query (looking for budget numbers, brand names like "HP", "Lenovo", or keywords like "return", "policy", "warranty").
   - **Database Fallback**: Executes direct MongoDB query using extracted keywords.
   - **UI Rendering**: Renders the matched laptop cards or FAQ text directly with a top info toast/banner: *"AI service is momentarily busy; displaying direct verified catalog matches."*
3. Never crash or present raw exception tracebacks to the user.

### Rationale
- Complies directly with Clarification Q2 resolution.
- Guarantees a working demo regardless of external API quota fluctuations.
