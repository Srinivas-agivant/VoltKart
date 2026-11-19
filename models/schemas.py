"""Pydantic schemas and data validation models for VoltKart."""

from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator


class ProductModel(BaseModel):
    """Pydantic model representing a Laptop Product in the VoltKart catalog."""

    product_id: str = Field(..., description="Unique product code (e.g. VK-LAP-001)")
    name: str = Field(..., min_length=2, description="Product commercial name")
    brand: str = Field(..., description="Brand name (e.g. HP, Lenovo, Dell, VoltKart)")
    price: float = Field(..., gt=0, description="Price in INR")
    processor: str = Field(..., description="Processor description")
    ram: str = Field(..., description="Raw RAM string")
    ram_gb: int = Field(default=8, ge=2, description="Normalized RAM in GB")
    storage: str = Field(..., description="Raw storage string")
    storage_gb: int = Field(default=256, ge=64, description="Normalized storage in GB")
    display: str = Field(..., description="Display specifications")
    graphics: str = Field(..., description="Graphics processor")
    weight: str = Field(..., description="Raw weight string")
    weight_kg: float = Field(default=1.8, ge=0.5, description="Normalized weight in kg")
    battery_life: str = Field(..., description="Raw battery life description")
    battery_hours: float = Field(default=6.0, ge=1.0, description="Normalized battery life in hours")
    warranty: str = Field(..., description="Warranty coverage terms")
    usage_type: str = Field(default="general", description="student | coding | gaming | business | general")
    specifications: dict[str, Any] = Field(default_factory=dict, description="Arbitrary attributes")
    content_hash: str = Field(default="", description="MD5 hash for deduplication")
    source_file: str = Field(default="manual_entry", description="Source filename")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("usage_type", mode="before")
    @classmethod
    def clean_usage(cls, v: Any) -> str:
        if not v or not isinstance(v, str):
            return "general"
        val = v.strip().lower()
        if "game" in val:
            return "gaming"
        if "code" in val or "dev" in val or "program" in val:
            return "coding"
        if "stud" in val or "colleg" in val or "school" in val:
            return "student"
        if "biz" in val or "busin" in val or "work" in val or "offic" in val:
            return "business"
        return "general"


class FAQModel(BaseModel):
    """Pydantic model representing a Customer Support FAQ."""

    faq_id: str = Field(..., description="Unique FAQ identifier (e.g. FAQ-001)")
    category: str = Field(..., description="Category (Returns, Warranty, Shipping, etc.)")
    question: str = Field(..., min_length=5, description="Customer question")
    answer: str = Field(..., min_length=5, description="Official factual answer")
    keywords: list[str] = Field(default_factory=list, description="Keywords for search")
    content_hash: str = Field(default="", description="MD5 hash for deduplication")
    source_file: str = Field(default="manual_entry")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StorePolicyModel(BaseModel):
    """Pydantic model representing an official Store Policy article."""

    policy_id: str = Field(..., description="Unique policy identifier (e.g. POL-001)")
    category: str = Field(..., description="return | refund | warranty | shipping | general")
    title: str = Field(..., min_length=3, description="Policy title")
    description: str = Field(..., min_length=10, description="Full policy statement")
    keywords: list[str] = Field(default_factory=list, description="Keywords for search")
    content_hash: str = Field(default="", description="MD5 hash for deduplication")
    source_file: str = Field(default="manual_entry")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RequirementsFilter(BaseModel):
    """Extracted shopping requirements for recommendations."""

    budget_max: Optional[float] = None
    budget_min: Optional[float] = None
    brand: Optional[str] = None
    usage_type: Optional[str] = None
    min_ram_gb: Optional[int] = None
    min_storage_gb: Optional[int] = None
    processor_preference: Optional[str] = None
    battery_preference: Optional[str] = None
    weight_preference: Optional[str] = None


class SupportQueryFilter(BaseModel):
    """Extracted support parameters."""

    category: Optional[str] = None
    search_keywords: list[str] = Field(default_factory=list)


class ComparisonTargets(BaseModel):
    """Extracted targets for product comparison."""

    positions: list[int] = Field(default_factory=list)
    product_names: list[str] = Field(default_factory=list)


class IntentResult(BaseModel):
    """Structured output returned by Stage 1 Intent Extraction."""

    intent: str = Field(..., description="recommend | support | compare | out_of_scope | general")
    requirements: Optional[RequirementsFilter] = None
    support_query: Optional[SupportQueryFilter] = None
    comparison_targets: Optional[ComparisonTargets] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class ImportSummary(BaseModel):
    """Audit summary for an administrator dataset ingestion."""

    filename: str
    dataset_type: str
    total_records: int = 0
    inserted_records: int = 0
    updated_records: int = 0
    skipped_duplicates: int = 0
    failed_records: int = 0
    import_status: str = "completed"
    error_log: list[str] = Field(default_factory=list)
    imported_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeBaseChunkModel(BaseModel):
    """Pydantic model representing an extracted text chunk from an uploaded PDF document."""

    chunk_id: str = Field(..., description="Unique chunk identifier (e.g. CHK-DOC-001)")
    filename: str = Field(..., description="Source PDF filename")
    category: str = Field(..., description="FAQs | Product Catalogue | Return Policy | Warranty Policy | Shipping Policy | Other Store Information")
    page_number: int = Field(default=1, ge=1, description="Source page number in PDF")
    chunk_text: str = Field(..., min_length=10, description="Extracted text chunk content")
    character_count: int = Field(default=0, ge=0)
    content_hash: str = Field(default="", description="MD5 hash of chunk text for deduplication")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeDocumentSummary(BaseModel):
    """Metadata summary of an uploaded PDF document in the knowledge base."""

    filename: str
    category: str
    total_pages: int
    total_chunks: int
    upload_date: datetime

