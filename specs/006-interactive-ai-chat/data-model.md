# Data Model: Interactive AI Shopping Assistant

## Entities

### Chat Session (`voltkart_db.conversations`)
- `conversation_id`: String (UUID or unique hash)
- `title`: String (e.g., "Storefront Chat" or dynamic topic from first turn)
- `created_at`: Datetime
- `updated_at`: Datetime
- `message_count`: Integer

### Message Turn (`st.session_state.messages` & `conversations.turns`)
- `role`: "user" | "assistant"
- `content`: String
- `intent`: "recommend" | "compare" | "support" | "general" | "out_of_scope" | null
- `products`: List of Catalog Product dictionaries
- `retrieved_ids`: List of product/FAQ IDs
- `timestamp`: Datetime

### Interactive Prompt Trigger
- `source`: "chip" | "card_action" | "text_input"
- `action_type`: "query" | "compare" | "detail" | "reset"
- `payload`: String or Dict
