"""Data validation, normalization, and deduplication hashing module for VoltKart."""

import hashlib
import json
import re
from datetime import datetime
from typing import Any
import pandas as pd
from pydantic import ValidationError

from models.schemas import ProductModel, FAQModel, StorePolicyModel


class DataValidator:
    """Cleans raw row data, coerces numeric fields, validates Pydantic models, and generates hashes."""

    @staticmethod
    def clean_price(val: Any) -> float:
        """Coerces price representations (e.g. 'Rs. 55,000/-', '₹54999.00') to float."""
        if pd.isna(val):
            return 0.0
        val_str = str(val).strip()
        match = re.search(r"(\d[\d,]*(?:\.\d+)?)", val_str)
        if match:
            num_str = match.group(1).replace(",", "")
            try:
                return float(num_str)
            except ValueError:
                pass
        return 0.0

    @staticmethod
    def clean_ram_gb(val: Any) -> int:
        """Extracts integer GB from strings like '16GB DDR4', '16 GB', '8'."""
        if pd.isna(val):
            return 8
        match = re.search(r"(\d+)\s*(?:gb|gigabyte)?", str(val), re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 8

    @staticmethod
    def clean_storage_gb(val: Any) -> int:
        """Extracts normalized storage in GB from strings like '1TB SSD', '512GB'."""
        if pd.isna(val):
            return 256
        val_str = str(val).lower()
        # Check TB
        tb_match = re.search(r"(\d+)\s*(?:tb|terabyte)", val_str)
        if tb_match:
            return int(tb_match.group(1)) * 1024
        # Check GB
        gb_match = re.search(r"(\d+)\s*(?:gb|gigabyte)", val_str)
        if gb_match:
            return int(gb_match.group(1))
        # Plain number
        num_match = re.search(r"(\d+)", val_str)
        if num_match:
            num = int(num_match.group(1))
            return num * 1024 if num <= 4 else num
        return 256

    @staticmethod
    def clean_weight_kg(val: Any) -> float:
        """Extracts normalized weight in kg from strings like '1.65 kg', '1650g'."""
        if pd.isna(val):
            return 1.8
        val_str = str(val).lower()
        if "g" in val_str and "kg" not in val_str:
            match = re.search(r"(\d+)\s*g", val_str)
            if match:
                return round(float(match.group(1)) / 1000.0, 2)
        match = re.search(r"([\d.]+)\s*(?:kg)?", val_str)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return 1.8

    @staticmethod
    def clean_battery_hours(val: Any) -> float:
        """Extracts normalized battery life in hours from strings like '8.5 Hours', '10 hrs'."""
        if pd.isna(val):
            return 6.0
        match = re.search(r"([\d.]+)\s*(?:hours|hour|hrs|hr)?", str(val), re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return 6.0

    @staticmethod
    def clean_keywords(val: Any) -> list[str]:
        """Splits comma- or semicolon-separated keyword strings into a clean list."""
        if pd.isna(val) or not val:
            return []
        if isinstance(val, list):
            return [str(k).strip() for k in val if str(k).strip()]
        parts = re.split(r"[;,]", str(val))
        return [p.strip() for p in parts if p.strip()]

    @classmethod
    def compute_content_hash(cls, record_dict: dict) -> str:
        """Generates a deterministic MD5 hash of core record attributes for deduplication."""
        # Filter out system and timestamp keys
        filtered = {k: v for k, v in record_dict.items() if k not in ["_id", "created_at", "updated_at", "source_file", "content_hash"]}
        serialized = json.dumps(filtered, sort_keys=True, default=str)
        return hashlib.md5(serialized.encode("utf-8")).hexdigest()

    @classmethod
    def clean_and_validate(
        cls, df: pd.DataFrame, dataset_type: str, filename: str = "upload"
    ) -> tuple[list[dict], list[dict]]:
        """Processes a DataFrame, applying type coercions and Pydantic validation.

        Returns:
            (valid_records, invalid_records)
        """
        valid_records: list[dict] = []
        invalid_records: list[dict] = []

        records = df.to_dict(orient="records")

        for idx, raw_record in enumerate(records, start=1):
            row_errors: list[str] = []
            try:
                if dataset_type == "products":
                    raw_price = raw_record.get("price")
                    numeric_price = cls.clean_price(raw_price)
                    if numeric_price <= 0:
                        row_errors.append(f"Invalid price value: '{raw_price}'")

                    norm_record = {
                        "product_id": str(raw_record.get("product_id") or f"VK-AUTO-{idx}").strip(),
                        "name": str(raw_record.get("name") or "").strip(),
                        "brand": str(raw_record.get("brand") or "Generic").strip(),
                        "price": numeric_price,
                        "processor": str(raw_record.get("processor") or "Standard Processor").strip(),
                        "ram": str(raw_record.get("ram") or "8GB").strip(),
                        "ram_gb": cls.clean_ram_gb(raw_record.get("ram")),
                        "storage": str(raw_record.get("storage") or "512GB SSD").strip(),
                        "storage_gb": cls.clean_storage_gb(raw_record.get("storage")),
                        "display": str(raw_record.get("display") or "15.6 inch Display").strip(),
                        "graphics": str(raw_record.get("graphics") or "Integrated Graphics").strip(),
                        "weight": str(raw_record.get("weight") or "1.8 kg").strip(),
                        "weight_kg": cls.clean_weight_kg(raw_record.get("weight")),
                        "battery_life": str(raw_record.get("battery_life") or "6 Hours").strip(),
                        "battery_hours": cls.clean_battery_hours(raw_record.get("battery_life")),
                        "warranty": str(raw_record.get("warranty") or "1 Year Manufacturer").strip(),
                        "usage_type": str(raw_record.get("usage_type") or "general").strip(),
                        "source_file": filename,
                    }

                    if not norm_record["name"]:
                        row_errors.append("Product name is required")

                    if row_errors:
                        invalid_records.append({"row_index": idx, "errors": row_errors, "raw": raw_record})
                        continue

                    # Validate with Pydantic
                    model = ProductModel(**norm_record)
                    record_dict = model.model_dump()
                    # Populate dual-field compatibility keys
                    record_dict["model"] = record_dict.get("name")
                    record_dict["price_inr"] = record_dict.get("price")
                    record_dict["store"] = record_dict.get("brand")
                    record_dict["usage_category"] = record_dict.get("usage_type")
                    record_dict["content_hash"] = cls.compute_content_hash(record_dict)
                    valid_records.append(record_dict)

                elif dataset_type == "faqs":
                    norm_record = {
                        "faq_id": str(raw_record.get("faq_id") or f"FAQ-{idx:03d}").strip(),
                        "category": str(raw_record.get("category") or "General").strip(),
                        "question": str(raw_record.get("question") or "").strip(),
                        "answer": str(raw_record.get("answer") or "").strip(),
                        "keywords": cls.clean_keywords(raw_record.get("keywords")),
                        "source_file": filename,
                    }
                    if not norm_record["question"] or len(norm_record["question"]) < 5:
                        row_errors.append("Question must be at least 5 characters")
                    if not norm_record["answer"] or len(norm_record["answer"]) < 5:
                        row_errors.append("Answer must be at least 5 characters")

                    if row_errors:
                        invalid_records.append({"row_index": idx, "errors": row_errors, "raw": raw_record})
                        continue

                    model = FAQModel(**norm_record)
                    record_dict = model.model_dump()
                    record_dict["content_hash"] = cls.compute_content_hash(record_dict)
                    valid_records.append(record_dict)

                elif dataset_type == "policies":
                    norm_record = {
                        "policy_id": str(raw_record.get("policy_id") or f"POL-{idx:03d}").strip(),
                        "category": str(raw_record.get("category") or "general").strip(),
                        "title": str(raw_record.get("title") or "").strip(),
                        "description": str(raw_record.get("description") or "").strip(),
                        "keywords": cls.clean_keywords(raw_record.get("keywords")),
                        "source_file": filename,
                    }
                    if not norm_record["title"]:
                        row_errors.append("Policy title is required")
                    if not norm_record["description"] or len(norm_record["description"]) < 10:
                        row_errors.append("Policy description must be at least 10 characters")

                    if row_errors:
                        invalid_records.append({"row_index": idx, "errors": row_errors, "raw": raw_record})
                        continue

                    model = StorePolicyModel(**norm_record)
                    record_dict = model.model_dump()
                    record_dict["content_hash"] = cls.compute_content_hash(record_dict)
                    valid_records.append(record_dict)

                else:
                    invalid_records.append({"row_index": idx, "errors": [f"Unknown dataset category '{dataset_type}'"], "raw": raw_record})

            except ValidationError as ve:
                err_msgs = [f"{e['loc'][0]}: {e['msg']}" for e in ve.errors()]
                invalid_records.append({"row_index": idx, "errors": err_msgs, "raw": raw_record})
            except Exception as e:
                invalid_records.append({"row_index": idx, "errors": [str(e)], "raw": raw_record})

        return valid_records, invalid_records
