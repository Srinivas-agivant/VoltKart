---
description: "Task list for VoltKart Storefront, Floating AI Chatbot & PDF Knowledge Base"
---

# Tasks: VoltKart Storefront, Floating AI Chatbot & PDF Knowledge Base

**Input**: Design documents from `/specs/002-storefront-pdf-chatbot/`
**Prerequisites**: plan.md, spec.md, data-model.md, constitution.md

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup & Data Model Extension

- [X] `T101` Add `COLLECTION_KNOWLEDGE_BASE = "knowledge_base"` to `config.py`
- [X] `T102` Update `database.py` to create indexes on the `knowledge_base` collection (`chunk_id`, `filename`, `category`, text index)
- [X] `T103` Define `KnowledgeBaseChunkModel` and `KnowledgeDocumentSummary` in `models/schemas.py`

---

## Phase 2: PDF Processing & Knowledge Base Backend

- [X] `T104` Implement `PdfProcessor` in `backend/pdf_processor.py` for multi-page PDF text extraction and overlapping text chunking
- [X] `T105` Implement `KnowledgeBaseService` in `backend/knowledge_base_service.py` for chunk insertion, content hashing, deduplication, search, and document deletion
- [X] `T106` Update `backend/retrieval_service.py` to perform hybrid search across `knowledge_base` chunks, `faqs`, and `store_policies`
- [X] `T107` Create automated tests in `tests/test_pdf_knowledge_base.py` verifying PDF text extraction, chunking, and knowledge base search

---

## Phase 3: E-Commerce Storefront

- [X] `T108` Implement `frontend/storefront.py` featuring VoltKart navbar, hero banner, live search, multi-faceted filters (brand, price slider, RAM, processor), product cards, and "View Details" specs

---

## Phase 4: Floating VoltKart AI Chatbot

- [X] `T109` Implement `frontend/floating_chat.py` with bottom-right floating trigger button, chat window overlay, standard welcome greeting, conversational timeline, and session state retention

---

## Phase 5: Admin PDF Knowledge Base Management UI

- [X] `T110` Update `frontend/admin_dashboard.py` with a dedicated PDF Document Upload & Knowledge Base Manager tab (category selector, chunk preview, document list, and delete actions)

---

## Phase 6: Application Assembly & Verification

- [X] `T111` Update `app.py` to assemble the storefront navigation (Home, Laptops, About Us, Contact, Admin) with persistent floating chatbot integration
- [X] `T112` Generate synthetic test PDF document `data/sample_store_policy.pdf`
- [X] `T113` Execute complete test suite (`pytest tests/`) and verify all tests pass
