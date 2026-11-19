"""File processing and dynamic column mapping module for VoltKart."""

import io
from pathlib import Path
from typing import Any, Union
import pandas as pd

# Canonical Aliases for Dynamic Column Mapping
COLUMN_ALIASES: dict[str, dict[str, list[str]]] = {
    "products": {
        "product_id": ["product_id", "id", "item_id", "sku", "code", "product_code"],
        "name": ["name", "title", "product_name", "model", "laptop_name", "laptop"],
        "brand": ["brand", "manufacturer", "company", "make", "store"],
        "price": ["price", "mrp", "cost", "amount", "rate", "pricing", "selling_price", "price_inr"],
        "processor": ["processor", "cpu", "chipset", "proc", "processor_brand"],
        "ram": ["ram", "memory", "ram_size", "system_memory", "ram_gb"],
        "storage": ["storage", "disk", "ssd", "hdd", "rom", "hard_drive", "storage_capacity", "storage_gb"],
        "display": ["display", "screen", "screen_size", "resolution", "display_size", "display_inches"],
        "graphics": ["graphics", "gpu", "graphic_card", "video_card"],
        "weight": ["weight", "laptop_weight", "mass", "weight_kg"],
        "battery_life": ["battery_life", "battery", "battery_hours", "backup", "estimated_battery_hours"],
        "warranty": ["warranty", "guarantee", "warranty_period"],
        "usage_type": ["usage_type", "usage", "category", "segment", "type", "use_case", "usage_category"],
    },
    "faqs": {
        "faq_id": ["faq_id", "id", "question_id"],
        "category": ["category", "topic", "type", "section"],
        "question": ["question", "query", "title", "faq"],
        "answer": ["answer", "response", "solution", "description"],
        "keywords": ["keywords", "tags", "labels"],
    },
    "policies": {
        "policy_id": ["policy_id", "id"],
        "category": ["category", "type"],
        "title": ["title", "name", "policy_title"],
        "description": ["description", "content", "terms", "policy_text", "body"],
        "keywords": ["keywords", "tags"],
    },
}


class FileProcessor:
    """Reads tabular files (.csv, .xlsx, .xls) and handles column normalization."""

    @staticmethod
    def read_file(file_input: Union[str, Path, io.BytesIO, Any], filename: str) -> pd.DataFrame:
        """Reads CSV or Excel files into a Pandas DataFrame."""
        ext = Path(filename).suffix.lower()

        if ext == ".csv":
            try:
                df = pd.read_csv(file_input, encoding="utf-8")
            except UnicodeDecodeError:
                if hasattr(file_input, "seek"):
                    file_input.seek(0)
                df = pd.read_csv(file_input, encoding="latin1")
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(file_input, engine="openpyxl")
        else:
            raise ValueError(f"Unsupported file format '{ext}'. Only .csv, .xlsx, and .xls are supported.")

        # Clean string whitespace in headers
        df.columns = [str(c).strip() for c in df.columns]
        return df

    @staticmethod
    def auto_map_columns(df_columns: list[str], dataset_type: str) -> dict[str, str]:
        """Automatically maps uploaded columns to canonical schema keys using alias tables.

        Returns:
            dict mapping: { canonical_key: uploaded_column_name }
        """
        alias_map = COLUMN_ALIASES.get(dataset_type, {})
        normalized_cols = {str(col).strip().lower(): col for col in df_columns}
        result_mapping: dict[str, str] = {}

        for canonical_key, aliases in alias_map.items():
            matched_col = None
            for alias in aliases:
                alias_clean = alias.strip().lower()
                if alias_clean in normalized_cols:
                    matched_col = normalized_cols[alias_clean]
                    break
            if matched_col:
                result_mapping[canonical_key] = matched_col

        return result_mapping

    @staticmethod
    def apply_mapping(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
        """Renames DataFrame columns based on { canonical_key: uploaded_col_name }."""
        # Invert mapping to { uploaded_col_name: canonical_key }
        invert_map = {v: k for k, v in mapping.items() if v in df.columns}
        renamed_df = df.rename(columns=invert_map)
        return renamed_df
