"""Data importer module handling MongoDB insertions, deduplication, and audit logging."""

from datetime import datetime, timezone
import logging
from typing import Any
import config
from database import get_db

logger = logging.getLogger("voltkart.importer")


class DataImporter:
    """Manages batch database insertions with deduplication mode support and audit logging."""

    def __init__(self, db=None):
        self.db = db if db is not None else get_db()

    def _get_target_collection_name(self, dataset_type: str) -> str:
        if dataset_type == "products":
            return config.COLLECTION_PRODUCTS
        elif dataset_type == "faqs":
            return config.COLLECTION_FAQS
        elif dataset_type == "policies":
            return config.COLLECTION_POLICIES
        raise ValueError(f"Unknown dataset type: {dataset_type}")

    def _get_id_field(self, dataset_type: str) -> str:
        if dataset_type == "products":
            return "product_id"
        elif dataset_type == "faqs":
            return "faq_id"
        elif dataset_type == "policies":
            return "policy_id"
        return "_id"

    def import_records(
        self,
        valid_records: list[dict],
        dataset_type: str,
        filename: str,
        mode: str = "skip",  # "skip" | "update"
        invalid_records: list[dict] = None,
    ) -> dict[str, Any]:
        """Imports validated records into MongoDB, honoring deduplication mode."""
        if invalid_records is None:
            invalid_records = []

        coll_name = self._get_target_collection_name(dataset_type)
        collection = self.db[coll_name]
        id_field = self._get_id_field(dataset_type)

        total_records = len(valid_records) + len(invalid_records)
        inserted_count = 0
        updated_count = 0
        skipped_count = 0
        failed_count = len(invalid_records)
        error_logs = [f"Row {r['row_index']}: {', '.join(r['errors'])}" for r in invalid_records]

        now_utc = datetime.now(timezone.utc)

        for record in valid_records:
            record_id = record.get(id_field)
            if not record_id:
                failed_count += 1
                error_logs.append(f"Missing {id_field} in record {record.get('name', 'Unknown')}")
                continue

            # Check if record already exists by ID
            existing = collection.find_one({id_field: record_id})

            if existing:
                if mode == "skip":
                    skipped_count += 1
                    logger.debug("Skipped duplicate record: %s", record_id)
                elif mode == "update":
                    record["updated_at"] = now_utc
                    collection.update_one({id_field: record_id}, {"$set": record})
                    updated_count += 1
                    logger.debug("Updated existing record: %s", record_id)
            else:
                record["created_at"] = now_utc
                record["updated_at"] = now_utc
                collection.insert_one(record)
                inserted_count += 1

        import_status = "completed" if failed_count == 0 else ("partial" if inserted_count > 0 or updated_count > 0 else "failed")

        # Record in import_history collection
        audit_record = {
            "filename": filename,
            "dataset_type": dataset_type,
            "total_records": total_records,
            "inserted_records": inserted_count,
            "updated_records": updated_count,
            "skipped_duplicates": skipped_count,
            "failed_records": failed_count,
            "import_status": import_status,
            "error_log": error_logs[:50],
            "imported_at": now_utc,
        }

        try:
            self.db[config.COLLECTION_IMPORT_HISTORY].insert_one(audit_record)
        except Exception as e:
            logger.warning("Failed to write import history log: %s", e)

        return {
            "filename": filename,
            "dataset_type": dataset_type,
            "total": total_records,
            "inserted": inserted_count,
            "updated": updated_count,
            "skipped": skipped_count,
            "failed": failed_count,
            "status": import_status,
            "errors": error_logs,
        }

    def get_import_history(self, limit: int = 15) -> list[dict]:
        """Retrieves recent import audit logs."""
        try:
            return list(
                self.db[config.COLLECTION_IMPORT_HISTORY]
                .find({}, {"_id": 0})
                .sort("imported_at", -1)
                .limit(limit)
            )
        except Exception:
            return []
