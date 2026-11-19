# Implementation Plan: Remove Admin Control Center

**Branch**: `009-remove-admin-control-center` | **Date**: 2026-11-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/009-remove-admin-control-center/spec.md`

## Summary

Completely remove the customer-facing Admin Control Center / Store Management Center from the VoltKart storefront. Remove the "⚙️ Store Management" toggle button in the footer and eliminate the `admin_mode` state-switching flow in `app.py`. Keep automatic background catalog seeding (`auto_seed_default_catalog()`) and backend ingestion services (`DataImporter`, `FileProcessor`, `DataValidator`, `import_data.py`) active so unit test suites and developer CLI scripts continue to run without regression.

## Technical Context

**Language/Version**: Python 3.10+ (Current runtime: Python 3.15)  
**Primary Dependencies**: Streamlit 1.67+, PyMongo 4.20+, Pandas 3.1+, Google GenAI SDK  
**Storage**: MongoDB (local or Atlas) with in-memory resilient mock fallback  
**Testing**: pytest  
**Target Platform**: Web browser via Streamlit server on Windows / Linux  
**Project Type**: Full-stack E-Commerce Web Storefront with Grounded AI Assistant  
**Performance Goals**: Instant page render without conditional admin routing delays  
**Constraints**: Zero customer-facing administrative tools, zero regressions across 22 test cases  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Streamlit-First)**: PASS. All UI modifications remain in Streamlit.
- **Principle II (Pure Python)**: PASS. No secondary languages introduced.
- **Principle III (MongoDB Single Source of Truth)**: PASS. Catalog data storage unchanged.
- **Principle VII & VIII (Grounded Retrieval & Zero Hallucination)**: PASS. AI shopping assistant remains grounded.
- **Principle XI & XII (File Ingestion & Validation)**: PASS. Backend services preserved for testing and CLI imports.
- **Principle XV (UI Responsiveness & Reliability)**: PASS. Simplifies render tree and avoids unnecessary state branches.

## Project Structure

### Documentation (this feature)

```text
specs/009-remove-admin-control-center/
├── spec.md
├── plan.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Affected Source Code

```text
app.py                         # Remove admin_mode toggle, footer button, and admin view branch
frontend/admin_dashboard.py    # Unmounted from main app (retained as internal tool)
tests/                         # Verification test suite (all 22 tests pass)
```
