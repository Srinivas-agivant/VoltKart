# ⚡ VoltKart - AI-Powered Laptop Storefront & Shopping Assistant

> **Next-Generation E-Commerce Storefront, Floating AI Chatbot, and PDF Knowledge Base powered by Google Gemini, Streamlit, and MongoDB.**

VoltKart is a modern, high-performance laptop retail web application and conversational shopping assistant. It enables shoppers to explore verified laptop models, search and filter by brand/price/RAM/processor, compare models side-by-side, and ask customer support questions (returns, refunds, warranty, shipping) with **100% factual grounding** and a **strict zero-hallucination policy** backed by structured MongoDB collections and unstructured PDF knowledge documents.

---
## 🌟 Key Features

### 🛒 1. Modern E-Commerce Storefront
- **Full-Width Distraction-Free Layout**: Clean storefront layout with complete elimination of administrative and telemetry sidebars.
- **Branded Navigation Bar**: Streamlined top header featuring **`⚡ VoltKart`** branding, **Home**, **Laptops**, **About Us**, **Contact**, and an integrated dynamic search input.
- **Hero Banner**: High-impact *"Find Your Perfect Laptop"* hero section on a dark navy gradient background with sky-blue typography.
- **Dynamic Search & Multi-Faceted Filters**: Real-time search across laptop names, brands, processors, and graphics chips; interactive brand multiselect, dynamic price range slider (₹), RAM size multiselect, usage filters, and sorting (*Featured*, *Price: Low to High*, *Price: High to Low*, *RAM: High to Low*).
- **Responsive Product Grid**: Attractive 3-column product cards with brand badges, pricing, key specs (CPU, RAM, Storage, GPU, Battery Life), and an expandable *"🔍 View Details"* drawer (Display, Weight, Warranty, SKU).
- **Strict Domain Focus**: Exclusively features laptops—no phones, televisions, or unrelated electronics.

### 💬 2. Viewport-Fixed Floating VoltKart AI Chatbot
- **Strict Constant Fixed Position**: Anchored permanently at the bottom-right corner of the screen using CSS `position: fixed !important; bottom: 24px; right: 24px; z-index: 999999;`—remains accessible during scrolling and page navigation.
- **Circular Icon Toggle**: Circular launcher button with chat icon `💬` that opens and closes a fixed popup chat panel without shifting page content.
- **Standardized Greeting**: Welcomes every shopper: *"Hi! Welcome to VoltKart. I'm your AI shopping assistant. How can I help you today?"*
- **Persistent Multi-Turn Memory**: Full conversational memory with relative reference resolution (*"Compare the first two laptops"* or *"Show me something lighter"*).
- **Interactive UI Cards**: Directly renders rich product recommendation cards, comparison tables, and quick suggestion chips inside the chat interface.

### 📄 3. PDF Upload & Knowledge Base Management
- **Multi-Page PDF Processing**: Utilizes `pypdf` to extract high-fidelity text across multi-page store documents.
- **Intelligent Sliding Window Chunking**: Splits extracted text into 500-character chunks with 100-character overlaps and sentence boundary awareness.
- **Document Categorization**: Categorizes knowledge into FAQs, Product Catalogue, Return Policy, Warranty Policy, Shipping Policy, and Other Store Information.
- **Deduplication & Audit**: Computes deterministic SHA-256 chunk hashes (`content_hash`) and unique `chunk_id`s to prevent duplicate chunks.
- **Lifecycle Management**: Admin interface allows listing stored documents with chunk statistics and deleting or replacing documents with a single click.

### 🛡️ 4. Grounded Hybrid RAG Pipeline & Zero-Hallucination Policy
- **Stage 1 (Intent & Requirements Extraction)**: Gemini extracts structured shopping criteria (budget, RAM, processor, usage type) into a validated JSON schema.
- **Stage 2 (Python MongoDB Retrieval Gate)**: Pure Python executes the query against `products`, `faqs`, `store_policies`, and `knowledge_base` chunks. Gemini **never** queries or invents database records directly.
- **Stage 3 (Grounded Response Synthesis)**: Only retrieved database records are passed to Gemini for natural language response generation. If data is not in the database, the agent strictly replies that the information is unavailable.
- **Resilient Fallback**: Operates deterministically even without an active Gemini API key using local regex/keyword matching.

---

## 🛠️ Technology Stack

- **Frontend**: [Streamlit](https://streamlit.io/) (v1.38+)
- **Backend**: Python 3.10+
- **Primary Database**: MongoDB (PyMongo direct driver with resilient mock fallback)
- **PDF Processing**: `pypdf` (v5.0+)
- **Tabular Processing**: Pandas & OpenPyXL
- **AI / LLM Engine**: Google Gemini API (`google-genai` SDK)
- **Validation**: Pydantic v2
- **Testing**: pytest

---

## 📂 Project Structure

```text
VoltKart/
├── app.py                      # Main Streamlit application & navigation router
├── config.py                   # Environment configuration & collection names
├── database.py                 # PyMongo connection management & collection indexing
├── requirements.txt            # Python dependencies (including pypdf)
├── .env                        # Environment variable configuration
├── .gitignore                  # Git ignore rules (.env, cache, etc.)
│
├── frontend/
│   ├── storefront.py           # Modern e-commerce homepage & laptop catalog grid
│   ├── floating_chat.py        # Floating VoltKart AI Assistant widget
│   ├── chat_interface.py       # Full-screen conversational customer assistant
│   ├── admin_dashboard.py      # Admin ingestion (CSV/Excel & PDF Knowledge Base)
│   └── components.py           # Recommendation cards & comparison tables
│
├── backend/
│   ├── pdf_processor.py        # PDF text extraction & sliding-window chunking
│   ├── knowledge_base_service.py # PDF chunk ingestion, deduplication, search & deletion
│   ├── file_processor.py       # Pandas/OpenPyXL tabular parsing & column mapping
│   ├── data_validator.py       # Row cleaning, normalization, & Pydantic validation
│   ├── data_importer.py        # MongoDB insertion, deduplication mode, & audit logging
│   ├── gemini_service.py       # Google Gemini API wrapper (grounding & fallback)
│   ├── intent_service.py       # Intent extraction & regex fallback parser
│   ├── retrieval_service.py    # Hybrid MongoDB product, FAQ & PDF chunk querying
│   ├── recommendation_service.py # 2-3 product recommendation orchestration
│   ├── comparison_service.py   # Side-by-side spec comparison table builder
│   ├── faq_service.py          # Customer support policy/FAQ resolver
│   └── conversation_service.py # Session lifecycle & recommendation position tracking
│
├── models/
│   └── schemas.py              # Pydantic schemas (Product, FAQ, Policy, Chunk, Intent)
│
├── data/
│   ├── sample_products.csv     # 25 synthetic laptop listings
│   ├── sample_faqs.csv         # 15 synthetic support FAQs
│   ├── sample_policies.csv     # Synthetic store return, warranty, and shipping policies
│   └── sample_store_policy.pdf # Synthetic 3-page store policy PDF document
│
├── tests/
│   ├── test_pdf_knowledge_base.py # PDF extraction, chunking & knowledge search tests
│   ├── test_import.py          # CSV/Excel ingestion, mapping, and validation tests
│   ├── test_recommendation.py  # Budget filtering, ranking, and grounding tests
│   ├── test_faq.py             # Policy retrieval and anti-hallucination tests
│   └── test_chat.py            # Session persistence & relative reference tests
│
└── README.md                   # Complete documentation
```

---

## 🚀 Quickstart & Setup Instructions

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12
- MongoDB installed locally OR MongoDB Atlas connection string (or run in resilient in-memory mode automatically)
- Google Gemini API key from [Google AI Studio](https://aistudio.google.com/)

### 2. Installation
```powershell
# Navigate to the workspace directory
cd c:\Users\SrinivasCharyThimmap\Desktop\hackathon

# Install required dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Configure your `.env` file in the project root:
```ini
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=voltkart_db
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```
*(Note: If `GEMINI_API_KEY` is not provided, the application automatically runs in deterministic local fallback mode).*

### 4. Running the Application
Launch the application using Streamlit:
```powershell
streamlit run app.py
```
The application will open automatically in your browser at `http://localhost:8501`.

*(The application automatically seeds the 25 synthetic laptops, 15 FAQs, policies, and the sample PDF store document on first launch if the database is empty).*

---

## 🧪 Running Automated Tests

Run the complete test suite:
```powershell
pytest -v tests/
```
All **14 unit and integration tests** across PDF extraction, sliding chunking, knowledge base search, data ingestion, budget filtering, deterministic ranking, anti-hallucination, and conversation persistence will execute and pass:
```text
tests/test_chat.py::test_conversation_persistence PASSED
tests/test_chat.py::test_relative_reference_resolution PASSED
tests/test_faq.py::test_documented_policy_retrieval PASSED
tests/test_faq.py::test_zero_hallucination_on_unlisted_policy PASSED
tests/test_import.py::test_read_sample_products_csv PASSED
tests/test_import.py::test_auto_mapping_aliases PASSED
tests/test_import.py::test_data_validation_cleaning PASSED
tests/test_import.py::test_importer_deduplication PASSED
tests/test_pdf_knowledge_base.py::test_pdf_text_extraction PASSED
tests/test_pdf_knowledge_base.py::test_pdf_overlapping_chunking PASSED
tests/test_pdf_knowledge_base.py::test_knowledge_base_ingest_and_search PASSED
tests/test_recommendation.py::test_budget_filtering_and_ranking PASSED
tests/test_recommendation.py::test_no_matching_products PASSED
tests/test_recommendation.py::test_zero_hallucination_on_empty_products PASSED
```

---

## 🎬 Verification & Demo Walkthrough

### 1. Storefront Laptop Discovery
1. On the homepage (`Home` or `Laptops`), view the curated laptop catalog.
2. Use the search bar to query `"ThinkPad"` or `"RTX"`.
3. Open the **"🎛️ Filter Laptops"** panel to filter by brand (e.g. `Lenovo`, `Dell`), adjust the price range slider, or select `16GB` RAM.
4. Expand **"🔍 View Details"** on any card to inspect full CPU, GPU, display, weight, and warranty specifications.

### 2. Floating AI Assistant & Recommendations
1. Click the floating **"💬 VoltKart AI Assistant"** button at the bottom-right.
2. Ask:
   `"I need a laptop for college under ₹60,000 with good battery life."`
3. **Result**: The assistant extracts budget ($\le 60,000$), usage (`student`), queries MongoDB, ranks candidates, and displays top recommendation cards with verified specs and reasons.

### 3. Multi-Turn Product Comparison
1. In the chat, follow up with:
   `"Compare the first two laptops."`
2. **Result**: The assistant resolves positions 1 and 2 from conversation history, queries their database specs, and renders a structured side-by-side comparison table.

### 4. PDF Document Knowledge Base Retrieval
1. In the chat, ask:
   `"What is your return policy according to store documents?"`
2. **Result**: The assistant queries the `knowledge_base` chunks extracted from `sample_store_policy.pdf` and provides the exact 7-day return policy and eligibility rules.

### 5. Anti-Hallucination Negative Test
1. In the chat, ask:
   `"Do you offer 24-month zero-interest EMI on credit cards?"`
2. **Result**: Because EMI policies are absent from the store records, the assistant explicitly states that the store documents do not contain that information, strictly refusing to invent terms.

### 6. Admin Control Center & PDF Ingestion
1. Select **"Admin Center"** in the top navigation.
2. Go to the **"📄 PDF Knowledge Base"** tab.
3. Select category `"Return Policy"`, upload any PDF document, and click **"🚀 Extract & Ingest PDF into Knowledge Base"**.
4. View real-time metrics (Pages Extracted, Chunks Generated, Chunks Inserted) and manage/delete stored documents.
