"""PDF extraction and text chunking processor for VoltKart knowledge base."""

import hashlib
import io
import logging
import re
from typing import BinaryIO, Union
import pypdf

logger = logging.getLogger("voltkart.pdf")


class PdfProcessor:
    """Extracts text from multi-page PDFs and generates overlapping text chunks."""

    @staticmethod
    def extract_text_from_pdf(file_input: Union[bytes, BinaryIO, io.BytesIO]) -> list[dict]:
        """Extracts text per page from a PDF file.

        Returns:
            list of dict: [{"page_number": int, "text": str}]
        """
        if isinstance(file_input, bytes):
            stream = io.BytesIO(file_input)
        else:
            stream = file_input

        reader = pypdf.PdfReader(stream)
        pages_data = []

        for idx, page in enumerate(reader.pages, start=1):
            try:
                page_text = page.extract_text() or ""
                # Normalize excessive whitespace and linebreaks
                cleaned_text = re.sub(r"\s+", " ", page_text).strip()
                if cleaned_text:
                    pages_data.append({"page_number": idx, "text": cleaned_text})
            except Exception as e:
                logger.warning("Error extracting page %d: %s", idx, e)

        return pages_data

    @classmethod
    def chunk_extracted_pages(
        cls,
        pages_data: list[dict],
        filename: str,
        category: str,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
    ) -> list[dict]:
        """Splits multi-page text into overlapping chunks with metadata.

        Args:
            pages_data: list of dicts with page_number and text.
            filename: original source filename.
            category: document category.
            chunk_size: target character length per chunk.
            chunk_overlap: overlap between adjacent chunks.

        Returns:
            list of chunk dicts ready for KnowledgeBaseChunkModel.
        """
        chunks: list[dict] = []
        chunk_counter = 1

        for page in pages_data:
            page_num = page["page_number"]
            text = page["text"]

            if len(text) <= chunk_size:
                # Page text fits in a single chunk
                chunk_hash = cls.compute_chunk_hash(text)
                chunks.append(
                    {
                        "chunk_id": f"CHK-{filename[:8]}-P{page_num}-{chunk_counter:03d}",
                        "filename": filename,
                        "category": category,
                        "page_number": page_num,
                        "chunk_text": text,
                        "character_count": len(text),
                        "content_hash": chunk_hash,
                    }
                )
                chunk_counter += 1
            else:
                # Sliding window chunking
                start = 0
                while start < len(text):
                    end = min(start + chunk_size, len(text))

                    # If not at the end of the text, try to break at a sentence or word boundary
                    if end < len(text):
                        last_period = text.rfind(". ", start + 200, end)
                        if last_period != -1:
                            end = last_period + 1
                        else:
                            last_space = text.rfind(" ", start + 200, end)
                            if last_space != -1:
                                end = last_space

                    chunk_slice = text[start:end].strip()
                    if len(chunk_slice) >= 20:
                        chunk_hash = cls.compute_chunk_hash(chunk_slice)
                        chunks.append(
                            {
                                "chunk_id": f"CHK-{filename[:8]}-P{page_num}-{chunk_counter:03d}",
                                "filename": filename,
                                "category": category,
                                "page_number": page_num,
                                "chunk_text": chunk_slice,
                                "character_count": len(chunk_slice),
                                "content_hash": chunk_hash,
                            }
                        )
                        chunk_counter += 1

                    if end >= len(text):
                        break
                    start = max(start + 1, end - chunk_overlap)

        return chunks

    @staticmethod
    def compute_chunk_hash(chunk_text: str) -> str:
        """Computes a deterministic MD5 hash for a text chunk."""
        cleaned = re.sub(r"\s+", " ", chunk_text).strip().lower()
        return hashlib.md5(cleaned.encode("utf-8")).hexdigest()
