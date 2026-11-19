"""Knowledge base service managing PDF document chunk ingestion, search, and lifecycle."""

from datetime import datetime, timezone
import logging
import re
from typing import Any, BinaryIO, Optional, Union
import config
from database import get_db
from backend.pdf_processor import PdfProcessor
from models.schemas import KnowledgeBaseChunkModel

logger = logging.getLogger("voltkart.knowledge_base")


class KnowledgeBaseService:
    """Manages document chunks in MongoDB knowledge_base collection."""

    def __init__(self, db=None):
        self.db = db if db is not None else get_db()

    def ingest_pdf(
        self,
        file_input: Union[bytes, BinaryIO],
        filename: str,
        category: str,
        replace: bool = False,
    ) -> dict[str, Any]:
        """Extracts, chunks, validates, and stores a PDF document in MongoDB.

        Returns:
            dict containing ingestion summary.
        """
        coll = self.db[config.COLLECTION_KNOWLEDGE_BASE]

        # 1. Extract text
        pages_data = PdfProcessor.extract_text_from_pdf(file_input)
        if not pages_data:
            return {
                "filename": filename,
                "category": category,
                "total_pages": 0,
                "total_chunks": 0,
                "inserted": 0,
                "status": "failed",
                "error": "No extractable text found in PDF. Scanned or image-only PDFs are not supported.",
            }

        total_pages = len(pages_data)

        # 2. Chunk text
        chunks_data = PdfProcessor.chunk_extracted_pages(
            pages_data=pages_data,
            filename=filename,
            category=category,
            chunk_size=500,
            chunk_overlap=100,
        )

        if not chunks_data:
            return {
                "filename": filename,
                "category": category,
                "total_pages": total_pages,
                "total_chunks": 0,
                "inserted": 0,
                "status": "failed",
                "error": "Extracted text was too short to generate valid knowledge chunks.",
            }

        # 3. Handle replace mode
        if replace:
            deleted_res = coll.delete_many({"filename": filename})
            logger.info("Replaced existing PDF %s (deleted %d chunks)", filename, deleted_res.deleted_count)

        inserted_count = 0
        skipped_count = 0
        now_utc = datetime.now(timezone.utc)

        # 4. Insert chunks with deduplication
        for cdata in chunks_data:
            try:
                # Deduplication check by content_hash or chunk_id
                existing = coll.find_one(
                    {"$or": [{"chunk_id": cdata["chunk_id"]}, {"content_hash": cdata["content_hash"]}]}
                )
                if existing and not replace:
                    skipped_count += 1
                    continue

                model = KnowledgeBaseChunkModel(**cdata)
                doc = model.model_dump()
                doc["created_at"] = now_utc
                coll.insert_one(doc)
                inserted_count += 1
            except Exception as e:
                logger.warning("Error saving chunk %s: %s", cdata.get("chunk_id"), e)

        # 5. Log to import_history
        import_status = "completed" if inserted_count > 0 else ("skipped" if skipped_count > 0 else "failed")
        audit_entry = {
            "filename": filename,
            "dataset_type": f"pdf_{category.lower().replace(' ', '_')}",
            "total_records": len(chunks_data),
            "inserted_records": inserted_count,
            "updated_records": 0,
            "skipped_duplicates": skipped_count,
            "failed_records": 0,
            "import_status": import_status,
            "error_log": [],
            "imported_at": now_utc,
        }
        try:
            self.db[config.COLLECTION_IMPORT_HISTORY].insert_one(audit_entry)
        except Exception:
            pass

        return {
            "filename": filename,
            "category": category,
            "total_pages": total_pages,
            "total_chunks": len(chunks_data),
            "inserted": inserted_count,
            "skipped": skipped_count,
            "status": import_status,
        }

    def search_knowledge_base(
        self, query: str, category: Optional[str] = None, limit: int = 3
    ) -> list[dict]:
        """Searches knowledge_base collection for relevant text chunks."""
        coll = self.db[config.COLLECTION_KNOWLEDGE_BASE]
        lower_q = query.lower()

        # Build query
        filter_query: dict[str, Any] = {}
        if category:
            filter_query["category"] = category

        all_chunks = list(coll.find(filter_query, {"_id": 0}).limit(200))
        if not all_chunks:
            return []

        # Tokenize query for term frequency ranking
        query_words = [w for w in re.findall(r"\w+", lower_q) if len(w) > 3]

        scored_chunks = []
        for chk in all_chunks:
            text = chk.get("chunk_text", "").lower()
            score = 0
            for word in query_words:
                if word in text:
                    score += text.count(word)

            if score > 0:
                scored_chunks.append((score, chk))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_chunks[:limit]]

    def list_stored_documents(self) -> list[dict]:
        """Summarizes distinct PDF documents stored in the knowledge base."""
        coll = self.db[config.COLLECTION_KNOWLEDGE_BASE]
        docs = list(coll.find({}, {"_id": 0, "filename": 1, "category": 1, "page_number": 1, "created_at": 1}))

        doc_map: dict[str, dict] = {}
        for d in docs:
            fn = d.get("filename", "unknown")
            if fn not in doc_map:
                doc_map[fn] = {
                    "filename": fn,
                    "category": d.get("category", "General"),
                    "max_page": d.get("page_number", 1),
                    "total_chunks": 1,
                    "uploaded_at": d.get("created_at"),
                }
            else:
                doc_map[fn]["total_chunks"] += 1
                doc_map[fn]["max_page"] = max(doc_map[fn]["max_page"], d.get("page_number", 1))

        return list(doc_map.values())

    def delete_document(self, filename: str) -> int:
        """Deletes all chunks belonging to a filename from the knowledge base."""
        coll = self.db[config.COLLECTION_KNOWLEDGE_BASE]
        res = coll.delete_many({"filename": filename})
        return res.deleted_count
