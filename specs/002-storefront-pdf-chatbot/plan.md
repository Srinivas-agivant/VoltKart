# Implementation Plan: VoltKart Storefront, Floating AI Chatbot & PDF Knowledge Base

**Branch**: `002-storefront-pdf-chatbot` | **Date**: 2026-11-19 | **Spec**: [specs/002-storefront-pdf-chatbot/spec.md](spec.md)

---

## Summary

Expand the VoltKart application with a modern, responsive e-commerce storefront (Hero banner, live search, multi-faceted filters, dynamic laptop product cards with "View Details"), a floating bottom-right AI Assistant Chatbot widget accessible across the storefront, and an Admin PDF Knowledge Base ingestion pipeline with multi-page text extraction, overlapping chunking, and metadata tracking in MongoDB `knowledge_base`.

---

## Technical Context

- **Frontend**: Streamlit with custom CSS for e-commerce aesthetics (navy blue `#0f172a`, clean white `#ffffff`, slate grey `#f8fafc`) and floating bottom-right chat widget.
- **Backend**: Python 3.10+
- **PDF Extraction**: `pypdf` (multi-page extraction, sliding window chunking with 500-character size and 100-character overlap)
- **Database**: MongoDB (`voltkart_db`)
  - Existing Collections: `products`, `faqs`, `store_policies`, `conversations`, `messages`, `recommendations`, `import_history`
  - New Collection: `knowledge_base` (stores chunked PDF text with `chunk_id`, `filename`, `category`, `page_number`, `chunk_text`, `content_hash`, `created_at`)
- **AI / LLM**: Google Gemini API (`google-genai` SDK) with strict database/knowledge-base grounding and local deterministic fallback.

---

## Project Structure & Modifications

```text
VoltKart/
├── app.py                      # Updated: Homepage navigation bar, hero, storefront routing, floating chatbot
├── config.py                   # Updated: Added COLLECTION_KNOWLEDGE_BASE constant
├── database.py                 # Updated: Added knowledge_base collection and indexes
│
├── frontend/
│   ├── storefront.py           # NEW: E-commerce homepage, hero banner, search, filters, product card grid
│   ├── floating_chat.py        # NEW: Floating bottom-right chatbot widget, modal/expander, greeting, session state
│   ├── components.py           # Preserved & Enhanced: Recommendation cards, comparison tables, suggestion chips
│   ├── chat_interface.py       # Preserved: Standalone chat view for admin/direct testing
│   └── admin_dashboard.py      # Updated: Added PDF Document Upload & Knowledge Base Management tab
│
├── backend/
│   ├── pdf_processor.py        # NEW: Multi-page PDF text extraction and overlapping text chunker
│   ├── knowledge_base_service.py # NEW: MongoDB knowledge_base repository, deduplication, search & deletion
│   ├── retrieval_service.py    # Updated: Hybrid search querying both knowledge_base chunks and structured FAQs/policies
│   ├── file_processor.py       # Preserved: CSV/XLSX/XLS tabular parsing & dynamic mapping
│   ├── data_validator.py       # Preserved: Tabular cleaning and validation
│   ├── data_importer.py        # Preserved: Catalog importer and audit logger
│   ├── gemini_service.py       # Preserved: Structured intent & grounded generation
│   ├── intent_service.py       # Preserved: Intent router
│   ├── recommendation_service.py # Preserved: 2-3 product recommendations
│   ├── comparison_service.py   # Preserved: Product comparison
│   ├── faq_service.py          # Preserved & Updated: Injects retrieved PDF knowledge chunks
│   └── conversation_service.py # Preserved: Session and message turn persistence
│
├── models/
│   └── schemas.py              # Updated: KnowledgeBaseChunkModel & KnowledgeDocumentSummary
│
├── data/
│   ├── sample_products.csv     # Preserved
│   ├── sample_faqs.csv         # Preserved
│   ├── sample_policies.csv     # Preserved
│   └── sample_store_policy.pdf # NEW: Synthetic PDF store policy for test verification
│
└── tests/
    ├── test_pdf_knowledge_base.py # NEW: Tests for PDF text extraction, chunking, and knowledge base search
    ├── test_import.py          # Preserved
    ├── test_recommendation.py  # Preserved
    ├── test_faq.py             # Preserved
    └── test_chat.py            # Preserved
```
