"""Tests for PDF text extraction, overlapping chunking, and knowledge base search."""

from pathlib import Path
import mongomock
import pytest

from backend.pdf_processor import PdfProcessor
from backend.knowledge_base_service import KnowledgeBaseService


@pytest.fixture
def sample_pdf_path():
    pdf_path = Path("data/sample_store_policy.pdf")
    assert pdf_path.exists(), "Sample PDF must exist for tests"
    return str(pdf_path)


def test_pdf_text_extraction(sample_pdf_path):
    """Verify that multi-page PDF is extracted with text per page."""
    with open(sample_pdf_path, "rb") as f:
        pages = PdfProcessor.extract_text_from_pdf(f)

    assert len(pages) == 3
    assert pages[0]["page_number"] == 1
    assert "7-Day Return" in pages[0]["text"]
    assert pages[1]["page_number"] == 2
    assert "Manufacturer Warranty" in pages[1]["text"]
    assert pages[2]["page_number"] == 3
    assert "Express Courier Shipping" in pages[2]["text"]


def test_pdf_overlapping_chunking(sample_pdf_path):
    """Verify that text is split into chunks with overlap and metadata."""
    with open(sample_pdf_path, "rb") as f:
        pages = PdfProcessor.extract_text_from_pdf(f)

    chunks = PdfProcessor.chunk_extracted_pages(
        pages_data=pages,
        filename="sample_store_policy.pdf",
        category="Return Policy",
        chunk_size=300,
        chunk_overlap=50,
    )

    assert len(chunks) >= 3
    first_chunk = chunks[0]
    assert "chunk_id" in first_chunk
    assert first_chunk["filename"] == "sample_store_policy.pdf"
    assert first_chunk["category"] == "Return Policy"
    assert first_chunk["page_number"] == 1
    assert len(first_chunk["content_hash"]) == 32


def test_knowledge_base_ingest_and_search(sample_pdf_path):
    """Verify ingestion into MongoDB, deduplication, and search retrieval."""
    mock_db = mongomock.MongoClient()["test_kb_db"]
    kb_service = KnowledgeBaseService(db=mock_db)

    with open(sample_pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # 1. Ingest
    res = kb_service.ingest_pdf(pdf_bytes, "sample_store_policy.pdf", "Return Policy")
    assert res["status"] == "completed"
    assert res["total_pages"] == 3
    assert res["inserted"] > 0

    # 2. Ingest duplicate without replace
    res_dup = kb_service.ingest_pdf(pdf_bytes, "sample_store_policy.pdf", "Return Policy", replace=False)
    assert res_dup["inserted"] == 0
    assert res_dup["skipped"] > 0

    # 3. Search for "unboxing video"
    search_results = kb_service.search_knowledge_base("unboxing video requirement for return")
    assert len(search_results) > 0
    assert any("unboxing" in c["chunk_text"].lower() for c in search_results)

    # 4. Search for "RAM upgrade"
    upgrade_results = kb_service.search_knowledge_base("Can I upgrade RAM without voiding warranty?")
    assert len(upgrade_results) > 0
    assert any("upgrade" in c["chunk_text"].lower() for c in upgrade_results)

    # 5. List and Delete
    doc_list = kb_service.list_stored_documents()
    assert len(doc_list) == 1
    assert doc_list[0]["filename"] == "sample_store_policy.pdf"

    deleted = kb_service.delete_document("sample_store_policy.pdf")
    assert deleted > 0
    assert len(kb_service.list_stored_documents()) == 0
