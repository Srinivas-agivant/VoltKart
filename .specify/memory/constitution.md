<!--
Sync Impact Report:
- Version change: [CONSTITUTION_VERSION] -> 1.0.0 (Initial Ratification)
- List of modified principles:
  - [PRINCIPLE_1_NAME] -> I. Frontend Architecture (Streamlit-First)
  - [PRINCIPLE_2_NAME] -> II. Backend Processing & Business Logic (Pure Python)
  - [PRINCIPLE_3_NAME] -> III. Primary Storage (MongoDB via PyMongo)
  - [PRINCIPLE_4_NAME] -> IV. LLM Integration (Google Gemini API)
  - [PRINCIPLE_5_NAME] -> V. Data Processing & Ingestion (Pandas & OpenPyXL)
  - Added VI. Direct PyMongo Connectivity (No ORM Overhead)
  - Added VII. Strict Database Grounding (Zero Unretrieved Facts)
  - Added VIII. Zero-Hallucination Policy (Non-Negotiable)
  - Added IX. Tri-Stage Decoupled Pipeline (Intent -> Retrieval -> Generation)
  - Added X. Conversation Memory & Context Management
  - Added XI. Multi-Format File Ingestion (CSV, XLSX, XLS)
  - Added XII. Pre-Insert Ingestion Validation
  - Added XIII. Synthetic Data Exclusivity (Privacy & Hackathon Safety)
  - Added XIV. Secrets & Credentials Isolation (Environment Variables Only)
  - Added XV. UI Responsiveness & Operational Reliability
  - Added XVI. Hackathon Scope Discipline (9-Hour Delivery Target)
- Added sections:
  - Technology Stack & Architectural Constraints
  - Development Workflow & Quality Gates
- Removed sections:
  - None
- Templates requiring updates:
  - .specify/templates/plan-template.md: ✅ verified aligned (constitution gates apply)
  - .specify/templates/spec-template.md: ✅ verified aligned
  - .specify/templates/tasks-template.md: ✅ verified aligned
- Follow-up TODOs:
  - None
-->

# VoltKart Constitution

## Core Principles

### I. Frontend Architecture (Streamlit-First)
The user interface MUST be built exclusively using Streamlit. No secondary web frameworks, separate micro-frontends, or heavy JavaScript clients shall be introduced.
*Rationale*: Streamlit provides rapid, reactive, stateful prototyping for AI chat and tabular file uploads, maximizing velocity within the strict 9-hour hackathon window.

### II. Backend Processing & Business Logic (Pure Python)
All backend processing, business logic, query generation, and agent orchestration MUST be implemented in pure Python.
*Rationale*: A unified Python codebase prevents context switching and integrates natively with Streamlit, PyMongo, Pandas, and the Google Gemini SDK.

### III. Primary Storage (MongoDB)
MongoDB MUST serve as the primary database and single source of truth for all operational datasets: products, specifications, pricing, inventory metadata, FAQs, and store policies.
*Rationale*: MongoDB's document model provides the flexibility required for dynamic e-commerce catalogs, nested product attributes, and fast text/field filtering.

### IV. LLM Integration (Google Gemini API)
The Google Gemini API MUST power all generative AI capabilities, including intent classification, entity extraction, semantic query formulation, and grounded customer response synthesis.
*Rationale*: Gemini provides high-throughput inference, strong structured-output capabilities, and a large context window ideal for grounded customer assistance.

### V. Data Processing & Ingestion (Pandas & OpenPyXL)
All tabular dataset loading, schema inspection, normalization, and transformation MUST be handled via Pandas (with OpenPyXL for Excel parsing).
*Rationale*: Pandas offers robust, vectorized data manipulation to reliably parse and sanitize external catalog uploads before storage.

### VI. Direct PyMongo Connectivity (No ORM Overhead)
All interactions with MongoDB MUST utilize the official `pymongo` driver directly. Object-Document Mappers (ODMs) or heavy ORMs MUST NOT be used.
*Rationale*: Direct PyMongo access minimizes boilerplate, avoids abstraction leaks, and delivers predictable, lightweight database interactions.

### VII. Strict Database Grounding (Zero Unretrieved Facts)
All product specifications, current pricing, stock availability, and store FAQ answers MUST be explicitly retrieved from MongoDB before being provided to the customer.
*Rationale*: E-commerce assistance demands factual accuracy; ungrounded answers lead to customer dissatisfaction and invalid orders.

### VIII. Zero-Hallucination Policy (Non-Negotiable)
The LLM MUST NEVER invent, assume, or extrapolate product specifications, prices, discounts, or store policies. If requested information is absent from the retrieved MongoDB context, the agent MUST explicitly inform the user of its unavailability and offer relevant alternatives or ask clarifying questions.
*Rationale*: Brand safety and trust are non-negotiable in customer support and product recommendations.

### IX. Tri-Stage Decoupled Pipeline (Intent -> Retrieval -> Generation)
The core AI architecture MUST strictly separate:
1. **Intent Understanding & Parameter Extraction**: Interpret customer queries and extract filter parameters.
2. **Database Retrieval**: Execute precise PyMongo queries/filters against MongoDB.
3. **Response Generation**: Synthesize a natural, helpful response strictly grounded in the retrieved records.
*Rationale*: Decoupling guarantees transparent debugging, inspectable retrieval steps, and verifiable grounding.

### X. Conversation Memory & Context Management
The application MUST maintain multi-turn conversation history within Streamlit session state and contextual memory. The agent MUST retain context across turns for follow-up inquiries, product comparisons, and refined searches.
*Rationale*: Realistic e-commerce conversations require conversational continuity without forcing the customer to repeat search criteria.

### XI. Multi-Format File Ingestion (CSV, XLSX, XLS)
The catalog ingestion module MUST accept and process file uploads in `.csv`, `.xlsx`, and `.xls` formats.
*Rationale*: Supports standard merchant catalog exports without requiring manual file conversions.

### XII. Pre-Insert Ingestion Validation
Uploaded files MUST be validated for required fields, valid data types (e.g. numeric prices, valid categories), and non-empty rows prior to inserting records into MongoDB. Malformed or invalid rows MUST be rejected with clear user feedback.
*Rationale*: Prevents database corruption, missing catalog attributes, and downstream retrieval failures.

### XIII. Synthetic Data Exclusivity (Privacy & Hackathon Safety)
All demonstration and testing data (product catalogs, mock orders, customer FAQs) MUST be 100% synthetic. No real customer personally identifiable information (PII) or proprietary commercial data shall be used.
*Rationale*: Adheres to strict privacy ethics and ensures safe, unencumbered presentation during hackathon evaluation.

### XIV. Secrets & Credentials Isolation (Environment Variables Only)
All API keys (including `GEMINI_API_KEY`) and database connection strings (`MONGODB_URI`) MUST be retrieved strictly from environment variables (e.g. via `python-dotenv`). Hardcoding credentials anywhere in source code or committing `.env` files is strictly prohibited.
*Rationale*: Mandatory security hygiene to prevent credential exposure in version control.

### XV. UI Responsiveness & Operational Reliability
The Streamlit application MUST remain responsive, clean, and crash-resilient. Long-running operations MUST provide user feedback (e.g., spinners or progress indicators), and database/API errors MUST be caught gracefully with human-friendly notices.
*Rationale*: A dependable, responsive user interface is essential for a compelling live hackathon demonstration.

### XVI. Hackathon Scope Discipline (9-Hour Delivery Target)
Every architectural and coding decision MUST prioritize delivering a fully functional, end-to-end working application within the 9-hour hackathon timeframe. Speculative features, premature optimizations, and unnecessary abstractions are forbidden.
*Rationale*: A working, demonstrated MVP delivers maximum hackathon value over unfinished perfection.

## Technology Stack & Architectural Constraints

### Approved Stack
- **Frontend**: Streamlit
- **Backend & Logic**: Python 3.10+
- **Primary Database**: MongoDB (Atlas or local instance)
- **Database Driver**: PyMongo
- **Tabular Data & File Parsing**: Pandas, OpenPyXL
- **Language Model**: Google Gemini API (`google-genai` / `google-generativeai`)
- **Data Validation**: Pydantic (for structured schema definitions and ingestion validation)
- **Environment Configuration**: `python-dotenv`

### Architectural Constraints
- **Monolithic Repository**: Keep frontend and backend services organized cleanly in a single repository without microservices or distributed message brokers.
- **No Heavy Frameworks**: Do not introduce FastAPI/Flask backends, Docker compose clusters, Celery queues, or vector database servers unless strictly required and approved.
- **Direct Execution**: The application MUST run straightforwardly with `streamlit run app.py` alongside a standard Python virtual environment.

## Development Workflow & Quality Gates

1. **Gate 1 - Constitution Check**: Every feature specification and plan must verify adherence to the 16 Core Principles (specifically zero-hallucination, MongoDB grounding, and environment variable security).
2. **Gate 2 - Ingestion Integrity**: Data import modules must be verified against test CSV/Excel files with validation assertions before connecting to live UI flows.
3. **Gate 3 - Grounding Verification**: Prompt templates and RAG chains must be verified against negative test cases (querying nonexistent products) to ensure the agent declines gracefully rather than hallucinating.
4. **Gate 4 - 9-Hour Milestone Check**: Features exceeding 45 minutes of implementation time must be simplified or rescoped immediately to protect the delivery deadline.

## Governance

- **Supremacy**: This Constitution supersedes all informal patterns, ad-hoc coding conventions, or conflicting team preferences.
- **Amendment Procedure**: Any modification to core principles requires an explicit version increment, documented rationale in the Sync Impact Report, and immediate propagation to `.specify/templates/`.
- **Versioning Policy**:
  - **MAJOR (X.0.0)**: Removal, fundamental change, or redefinition of core architectural principles.
  - **MINOR (1.X.0)**: Addition of new principles, tech stack additions, or substantial workflow guidelines.
  - **PATCH (1.0.X)**: Typo corrections, non-semantic clarifications, or minor wording refinements.
- **Compliance Review**: All task completions must confirm that no prohibited frameworks were added and that grounding in MongoDB is strictly maintained.

**Version**: 1.0.0 | **Ratified**: 2026-11-19 | **Last Amended**: 2026-11-19
