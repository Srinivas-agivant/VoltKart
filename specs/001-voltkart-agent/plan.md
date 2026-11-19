# Implementation Plan: VoltKart AI Agent

**Branch**: `001-voltkart-agent` | **Date**: 2026-11-19 | **Spec**: [specs/001-voltkart-agent/spec.md](spec.md)

**Input**: Feature specification from `specs/001-voltkart-agent/spec.md`

---

## Summary

Build VoltKart, an intelligent laptop e-commerce customer support and product recommendation application. The system features a responsive Streamlit UI with customer chat and administrative dataset ingestion (CSV, XLSX, XLS), backed by Python services and MongoDB (`voltkart_db`). Generative reasoning is powered by Google Gemini API using a strict Two-Stage Decoupled Architecture (Stage 1: Intent & Filter Extraction $\rightarrow$ Python PyMongo Retrieval $\rightarrow$ Stage 2: Grounded Natural Language Response Synthesis), enforcing a non-negotiable zero-hallucination policy.

---

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**:
- `streamlit` (v1.38+): Reactive chat timeline, file upload widgets, state management
- `pymongo` (v4.8+): Direct, low-overhead MongoDB database connectivity
- `pandas` (v2.2+): Vectorized tabular file parsing, data cleaning, normalization
- `openpyxl` (v3.1+): Excel (`.xlsx`, `.xls`) parsing engine for Pandas
- `google-genai` / `google-generativeai`: Google Gemini API SDK for structured intent parsing and grounded response generation
- `pydantic` (v2.8+): Strong type and schema validation for ingestion and intent models
- `python-dotenv`: Secure configuration loading from `.env`

**Storage**: MongoDB (`voltkart_db`)  
- Collections: `products`, `faqs`, `store_policies`, `conversations`, `messages`, `recommendations`, `import_history`

**Testing**: `pytest` (unit and integration tests for file ingestion, validation, retrieval, and fallback mechanisms)

**Target Platform**: Local execution on Windows / Linux / macOS via `streamlit run app.py`

**Project Type**: Monolithic Streamlit application with modular Python service layer (clean separation between frontend components, ingestion pipelines, database repositories, and AI orchestration)

**Performance Goals**:
- End-to-end recommendation turn response time: $< 3.5$ seconds
- Batch file ingestion and validation (100 rows): $< 15$ seconds
- UI memory and message reload from MongoDB: $< 300$ ms

**Constraints**:
- Strict 9-hour hackathon execution window: No microservices, no distributed message queues, no separate React/FastAPI layers.
- Strict Zero-Hallucination Policy: Python MUST retrieve factual records from MongoDB before Gemini generates an answer. Unretrieved facts MUST NOT be presented.
- Fallback Resilience: Direct MongoDB keyword search fallback if Gemini API encounters rate limits or errors.

**Scale/Scope**:
- 25 synthetic fictional laptop products
- 15 synthetic customer support FAQs
- Synthetic return, warranty, and shipping policies
- Multi-turn conversational memory with relative ordinal referencing ("compare the first two")

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate # | Constitution Principle | Status | Validation Evidence |
|---|---|---|---|
| **Gate 1** | **I. Streamlit-First Frontend** | **PASS** | UI is built exclusively in Streamlit (`app.py`, `frontend/`). No external web frameworks introduced. |
| **Gate 2** | **II. Pure Python Backend** | **PASS** | All business logic, ingestion, validation, scoring, and orchestration in pure Python. |
| **Gate 3** | **III. MongoDB Primary Storage** | **PASS** | Single source of truth using database `voltkart_db` with 7 dedicated collections. |
| **Gate 4** | **IV. Google Gemini API** | **PASS** | Gemini powers intent extraction and grounded generation. |
| **Gate 5** | **V & XI. Pandas & Multi-Format Ingestion** | **PASS** | `FileProcessor` uses Pandas and OpenPyXL for `.csv`, `.xlsx`, and `.xls`. |
| **Gate 6** | **VI. Direct PyMongo Connectivity** | **PASS** | Direct `pymongo.MongoClient` used. No ORM/ODM overhead. |
| **Gate 7** | **VII & VIII. Strict DB Grounding & Zero Hallucination** | **PASS** | Two-stage pipeline: Python retrieves factual documents from MongoDB before calling Gemini for response synthesis. |
| **Gate 8** | **IX. Tri-Stage Decoupled Pipeline** | **PASS** | Separates Intent Understanding, Database Retrieval, and Response Generation. |
| **Gate 9** | **X. Conversation Memory** | **PASS** | Session state cached in Streamlit + persistent storage in `conversations` and `messages`. |
| **Gate 10** | **XII. Pre-Insert Validation** | **PASS** | `DataValidator` enforces schema and type validation before any MongoDB write. |
| **Gate 11** | **XIII. Synthetic Data Exclusivity** | **PASS** | 100% synthetic dataset generated in `data/`. No real-world PII or commercial data used. |
| **Gate 12** | **XIV. Secrets in Environment Variables** | **PASS** | `config.py` loads `GEMINI_API_KEY` and `MONGODB_URI` via `python-dotenv`. Credentials excluded from UI and Git. |
| **Gate 13** | **XVI. 9-Hour Hackathon Delivery** | **PASS** | Streamlined monolithic layout running via `streamlit run app.py`. |

---

## Project Structure

### Documentation (this feature)

```text
specs/001-voltkart-agent/
├── spec.md              # Feature specification
├── plan.md              # This technical implementation plan
├── research.md          # Technical decisions and architectural rationale
├── data-model.md        # MongoDB collections, schemas, and indexes
├── quickstart.md        # Setup instructions and end-to-end verification flows
├── contracts/           # API and service interface contracts
│   ├── gemini-intent-contract.json
│   └── service-interfaces.md
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (repository root)

```text
VoltKart/
├── app.py                      # Main Streamlit application entry point
├── config.py                   # Environment configuration & constants
├── database.py                 # PyMongo connection management & index setup
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment variable template
├── .gitignore                  # Git ignore rules (.env, __pycache__, etc.)
│
├── frontend/
│   ├── __init__.py
│   ├── chat_interface.py       # Customer chat timeline, inputs, & suggestion chips
│   ├── admin_dashboard.py      # Admin ingestion UI, column mapping, & audit views
│   └── components.py           # Product recommendation cards & comparison tables
│
├── backend/
│   ├── __init__.py
│   ├── file_processor.py       # Pandas/OpenPyXL tabular parsing & column mapping
│   ├── data_validator.py       # Cleaning, normalization, hashing, & Pydantic validation
│   ├── data_importer.py        # MongoDB insertion, deduplication mode, & audit logging
│   ├── gemini_service.py       # Google Gemini API wrapper (structured intent & grounded generation)
│   ├── intent_service.py       # Intent classification & fallback parser
│   ├── retrieval_service.py    # MongoDB product/FAQ/policy querying & Python fit scoring
│   ├── recommendation_service.py # 2-3 product recommendation orchestration
│   ├── comparison_service.py   # Side-by-side spec comparison table builder
│   ├── faq_service.py          # Customer support policy/FAQ resolver
│   └── conversation_service.py # Session lifecycle, message history, & position tracking
│
├── models/
│   ├── __init__.py
│   └── schemas.py              # Pydantic models for Product, FAQ, Policy, Intent, & Ingestion
│
├── data/
│   ├── sample_products.csv     # 25 synthetic laptops
│   ├── sample_faqs.csv         # 15 synthetic FAQs
│   └── sample_policies.csv     # Synthetic store return, warranty, and shipping policies
│
├── tests/
│   ├── __init__.py
│   ├── test_import.py          # Tests for file processing and data validation
│   ├── test_recommendation.py  # Tests for Python ranking and candidate selection
│   ├── test_faq.py             # Tests for FAQ/policy retrieval and anti-hallucination
│   └── test_chat.py            # Tests for conversation history and relative referencing
│
└── README.md                   # Project documentation, setup, and hackathon overview
```

**Structure Decision**: Monolithic Streamlit application with decoupled service layer. Keeps the codebase easily navigable, independently testable via `pytest`, and directly executable with `streamlit run app.py` without requiring secondary process runners.

---

## Complexity Tracking

> Zero constitutional violations detected. No complex distributed systems, microservices, or external queue workers are introduced.
