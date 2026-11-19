"""Tests for file ingestion, column mapping, schema validation, and deduplication."""

import mongomock
import pandas as pd
import pytest

from backend.file_processor import FileProcessor
from backend.data_validator import DataValidator
from backend.data_importer import DataImporter


def test_read_sample_products_csv():
    """Verify that sample_products.csv is parsed with correct row count and headers."""
    df = FileProcessor.read_file("data/sample_products.csv", "sample_products.csv")
    assert len(df) == 25
    assert "name" in df.columns
    assert "price" in df.columns
    assert "ram" in df.columns


def test_auto_mapping_aliases():
    """Verify auto-mapping matches non-standard headers like 'Cost', 'Memory', 'Title'."""
    raw_columns = ["Product_ID", "Title", "Brand", "Cost", "Memory", "Storage_Capacity", "Screen"]
    mapping = FileProcessor.auto_map_columns(raw_columns, "products")

    assert mapping["name"] == "Title"
    assert mapping["price"] == "Cost"
    assert mapping["ram"] == "Memory"
    assert mapping["storage"] == "Storage_Capacity"
    assert mapping["display"] == "Screen"


def test_data_validation_cleaning():
    """Verify numeric cleaning and validation on messy data."""
    messy_data = pd.DataFrame([
        {
            "product_id": "VK-TEST-01",
            "name": "VoltBook Test Edition",
            "brand": "VoltKart",
            "price": "Rs. 55,000/-",
            "processor": "Intel i5",
            "ram": "16 GB DDR4",
            "storage": "1 TB NVMe SSD",
            "display": "15.6 inch FHD",
            "graphics": "Intel Iris",
            "weight": "1.65 kg",
            "battery_life": "8.5 Hours",
            "warranty": "1 Year",
            "usage_type": "Student / College",
        },
        {
            "product_id": "VK-TEST-BAD",
            "name": "",  # Missing name (invalid)
            "brand": "VoltKart",
            "price": "-500",  # Negative price (invalid)
            "processor": "Intel",
            "ram": "8GB",
            "storage": "256GB",
            "display": "14 inch",
            "graphics": "Intel",
            "weight": "1.5 kg",
            "battery_life": "5h",
            "warranty": "1 Year",
            "usage_type": "general",
        },
    ])

    valid, invalid = DataValidator.clean_and_validate(messy_data, "products", "test.csv")
    assert len(valid) == 1
    assert len(invalid) == 1

    item = valid[0]
    assert item["price"] == 55000.0
    assert item["ram_gb"] == 16
    assert item["storage_gb"] == 1024
    assert item["weight_kg"] == 1.65
    assert item["battery_hours"] == 8.5
    assert item["usage_type"] == "student"


def test_importer_deduplication():
    """Verify deduplication handles 'skip' vs 'update' modes properly."""
    mock_db = mongomock.MongoClient()["test_voltkart"]
    importer = DataImporter(db=mock_db)

    record_v1 = [{
        "product_id": "VK-DEDUP-01",
        "name": "VoltBook Original",
        "brand": "VoltKart",
        "price": 50000.0,
        "processor": "Intel i5",
        "ram": "8GB",
        "ram_gb": 8,
        "storage": "512GB",
        "storage_gb": 512,
        "display": "15 inch",
        "graphics": "Intel",
        "weight": "1.5 kg",
        "weight_kg": 1.5,
        "battery_life": "6 Hours",
        "battery_hours": 6.0,
        "warranty": "1 Year",
        "usage_type": "general",
        "content_hash": "hash_v1",
        "source_file": "test.csv",
    }]

    # First insert
    res1 = importer.import_records(record_v1, "products", "test.csv", mode="skip")
    assert res1["inserted"] == 1
    assert res1["skipped"] == 0

    # Second insert with same ID, mode='skip'
    res2 = importer.import_records(record_v1, "products", "test.csv", mode="skip")
    assert res2["inserted"] == 0
    assert res2["skipped"] == 1

    # Third insert with same ID, mode='update' and updated price
    record_v2 = [dict(record_v1[0])]
    record_v2[0]["price"] = 48000.0
    res3 = importer.import_records(record_v2, "products", "test.csv", mode="update")
    assert res3["updated"] == 1
    assert res3["skipped"] == 0

    saved = mock_db["products"].find_one({"product_id": "VK-DEDUP-01"})
    assert saved["price"] == 48000.0
