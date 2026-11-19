# Internal Service Interfaces: VoltKart Backend

This document defines the Python method signatures and contracts between backend modules, ensuring clean decoupling between UI, data processing, retrieval, and LLM services.

---

## 1. `FileProcessor` (`backend/file_processor.py`)

Responsible for loading and normalizing files.

```python
class FileProcessor:
    @staticmethod
    def read_file(file_obj, filename: str) -> pd.DataFrame:
        """Reads CSV, XLSX, or XLS into a pandas DataFrame."""
        ...

    @staticmethod
    def auto_map_columns(df_columns: list[str], dataset_type: str) -> dict[str, str]:
        """Matches source columns to standard schema keys using alias tables.
        Returns mapping: { 'target_schema_key': 'uploaded_column_name' }"""
        ...

    @staticmethod
    def apply_mapping(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
        """Renames DataFrame columns according to confirmed mapping."""
        ...
```

---

## 2. `DataValidator` (`backend/data_validator.py`)

Responsible for data cleaning, type coercion, and Pydantic validation.

```python
class DataValidator:
    @staticmethod
    def clean_and_validate(df: pd.DataFrame, dataset_type: str) -> tuple[list[dict], list[dict]]:
        """Cleans and validates records.
        Returns:
            valid_records: list of dictionaries ready for MongoDB
            invalid_records: list of { 'row_index': int, 'errors': list[str], 'raw': dict }
        """
        ...

    @staticmethod
    def compute_content_hash(record: dict) -> str:
        """Generates deterministic MD5 hash for duplicate detection."""
        ...
```

---

## 3. `DataImporter` (`backend/data_importer.py`)

Responsible for database insertion, deduplication, and audit logging.

```python
class DataImporter:
    def __init__(self, db: Database): ...

    def import_records(
        self,
        records: list[dict],
        dataset_type: str,
        filename: str,
        mode: str = "skip"  # 'skip' | 'update'
    ) -> dict:
        """Inserts records into MongoDB respecting mode.
        Returns summary:
            {
                'total': int,
                'inserted': int,
                'updated': int,
                'skipped': int,
                'failed': int,
                'status': str
            }
        """
        ...
```

---

## 4. `GeminiService` (`backend/gemini_service.py`)

Responsible for LLM API calls with structured schema and error handling.

```python
class GeminiService:
    def __init__(self, api_key: str): ...

    def classify_intent(self, user_query: str, history: list[dict]) -> dict:
        """Calls Gemini with JSON schema to extract intent and structured parameters.
        Returns dictionary conforming to GeminiIntentExtractionContract."""
        ...

    def generate_grounded_response(
        self,
        user_query: str,
        intent: str,
        retrieved_docs: list[dict],
        history: list[dict]
    ) -> str:
        """Generates natural language response strictly grounded on retrieved_docs.
        If retrieved_docs is empty, states information is unavailable."""
        ...
```

---

## 5. `RetrievalService` (`backend/retrieval_service.py`)

Responsible for MongoDB querying, filtering, and deterministic scoring.

```python
class RetrievalService:
    def __init__(self, db: Database): ...

    def get_recommendations(self, requirements: dict, limit: int = 3) -> list[dict]:
        """Queries products in MongoDB based on budget and spec filters.
        Ranks candidates using deterministic Python fit scoring.
        Returns top `limit` product dictionaries with `recommendation_reason`."""
        ...

    def get_support_answers(self, query: str, category: str = None) -> list[dict]:
        """Queries faqs and store_policies using text index and category filters.
        Returns list of matching FAQ/policy dictionaries."""
        ...

    def resolve_comparison_products(
        self,
        conversation_id: str,
        positions: list[int] = None,
        product_names: list[str] = None
    ) -> list[dict]:
        """Resolves ordinal positions (e.g. [1, 2]) or names against
        MongoDB recommendations for the active conversation.
        Returns list of full product dictionaries."""
        ...
```

---

## 6. `ConversationService` (`backend/conversation_service.py`)

Responsible for managing sessions, logging messages, and recording recommendation positions.

```python
class ConversationService:
    def __init__(self, db: Database): ...

    def get_or_create_conversation(self, conversation_id: str = None, initial_title: str = None) -> str:
        """Returns existing or creates new conversation_id in MongoDB."""
        ...

    def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        intent: str = None,
        retrieved_ids: list[str] = None
    ):
        """Appends message turn to messages collection."""
        ...

    def save_recommendations(
        self,
        conversation_id: str,
        recommended_products: list[dict]
    ):
        """Saves positions (1, 2, 3) and product_ids in recommendations collection."""
        ...

    def get_conversation_history(self, conversation_id: str, limit: int = 10) -> list[dict]:
        """Retrieves past message turns formatted for Gemini context."""
        ...

    def list_recent_conversations(self, limit: int = 20) -> list[dict]:
        """Returns recent conversation summaries for the Streamlit sidebar."""
        ...
```
