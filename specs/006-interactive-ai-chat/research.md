# Technical Research: Interactive AI Shopping Assistant

## Decision 1: Interactive Prompt Chip Flow in Streamlit

**Context**: In Streamlit, buttons inside containers trigger a script rerun. When a user clicks a suggestion chip button, the button returns `True` for that turn only.
**Decision**: Capture the clicked prompt in `chip_query` at the top of the chat panel. Check `active_prompt = chip_query or user_input`. If `active_prompt` is present, append the user turn, execute the intent -> retrieval -> generation pipeline, append the assistant turn with products, save to MongoDB, and trigger `st.rerun()`. This ensures instant responsiveness with zero delay.

## Decision 2: In-Chat Product Actions & Follow-Up Suggestions

**Context**: After recommending laptops, customers often want to know more details or compare them without typing long model names.
**Decision**: In compact chat mode:
1. Render interactive quick-action buttons below the timeline (e.g., "📊 Compare Top 2", "🔋 Longest Battery?", "💰 Cheaper Alternatives?").
2. Inside each compact product card, provide quick interactive spec summary and an action button to ask details about that specific model.
3. Clicking any action sets `st.session_state.pending_prompt`, which is processed on the next turn.

## Decision 3: Clean Support Policy Answer Extraction

**Context**: Knowledge base PDF chunks often contain several questions and answers in a single chunk (e.g., shipping, returns, tracking). When users ask "do u offer free shipping?", dumping the full chunk presents irrelevant Q&As.
**Decision**: In `gemini_service.py` and `faq_service.py`:
- Filter retrieved chunk text to isolate the specific question/answer matching the user's inquiry.
- If multiple Q&As are in a chunk, extract the specific `Q: ...` and `A: ...` matching the query.
- Gemini's system instruction already enforces: "Single Best Direct Answer Rule: Generate ONLY ONE best possible output answering the customer query directly". The deterministic fallback will also extract the specific matching Q&A rather than dumping the whole chunk.

## Decision 4: New Chat / Session Reset Control

**Context**: Users need an easy way to clear previous dialogue and start a new shopping inquiry without refreshing the entire web page.
**Decision**: Add a "🔄" New Chat button in the chat header next to the close button. When clicked, it generates a new conversation ID in MongoDB, clears `st.session_state.messages`, and reruns to show the fresh welcome state.
