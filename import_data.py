"""Data ingestion utility script for VoltKart.

Imports laptop products and FAQs into MongoDB with automatic schema mapping and validation.
Run with:
    python import_data.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

import config
from database import get_db, get_db_manager
from backend.file_processor import FileProcessor
from backend.data_validator import DataValidator
from backend.data_importer import DataImporter

def main():
    db = get_db()
    mgr = get_db_manager()
    importer = DataImporter(db=db)

    print(f"Connecting to MongoDB database '{config.DATABASE_NAME}' (Mock mode: {mgr.is_mock})...")

    # 1. Ingest Products
    products_csv = Path("data/voltkart_products_25.csv")
    if not products_csv.exists():
        products_csv = Path("data/sample_products.csv")

    if products_csv.exists():
        df_p = FileProcessor.read_file(products_csv, products_csv.name)
        mapping_p = FileProcessor.auto_map_columns(list(df_p.columns), "products")
        df_mapped_p = FileProcessor.apply_mapping(df_p, mapping_p)
        valid_p, invalid_p = DataValidator.clean_and_validate(df_mapped_p, "products", products_csv.name)
        res_p = importer.import_records(valid_p, "products", products_csv.name, mode="update", invalid_records=invalid_p)
        print(f"Products imported from {products_csv.name}: {res_p['inserted']} inserted, {res_p['updated']} updated.")

    # 2. Ingest FAQs
    faq_csv = Path("data/faq.csv")
    if not faq_csv.exists():
        faq_csv = Path("data/sample_faqs.csv")

    if faq_csv.exists():
        df_f = FileProcessor.read_file(faq_csv, faq_csv.name)
        mapping_f = FileProcessor.auto_map_columns(list(df_f.columns), "faqs")
        df_mapped_f = FileProcessor.apply_mapping(df_f, mapping_f)
        valid_f, invalid_f = DataValidator.clean_and_validate(df_mapped_f, "faqs", faq_csv.name)
        res_f = importer.import_records(valid_f, "faqs", faq_csv.name, mode="update", invalid_records=invalid_f)
        print(f"FAQs imported from {faq_csv.name}: {res_f['inserted']} inserted, {res_f['updated']} updated.")

    # 3. Ingest Policies
    policies_csv = Path("data/sample_policies.csv")
    if policies_csv.exists():
        df_pol = FileProcessor.read_file(policies_csv, policies_csv.name)
        mapping_pol = FileProcessor.auto_map_columns(list(df_pol.columns), "policies")
        df_mapped_pol = FileProcessor.apply_mapping(df_pol, mapping_pol)
        valid_pol, invalid_pol = DataValidator.clean_and_validate(df_mapped_pol, "policies", policies_csv.name)
        res_pol = importer.import_records(valid_pol, "policies", policies_csv.name, mode="update", invalid_records=invalid_pol)
        print(f"Policies imported from {policies_csv.name}: {res_pol['inserted']} inserted, {res_pol['updated']} updated.")

    print("\nMongoDB import completed successfully!")

if __name__ == "__main__":
    main()
