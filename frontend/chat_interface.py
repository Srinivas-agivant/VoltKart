"""Chat interface module managing conversational sessions, product displays, and AI responses."""

import streamlit as st

from backend.intent_service import IntentService
from backend.recommendation_service import RecommendationService
from backend.comparison_service import ComparisonService
from backend.faq_service import FaqService
from backend.conversation_service import ConversationService
from backend.gemini_service import GeminiService
from frontend.components import (
    render_product_cards,
    render_comparison_table,
    render_suggestion_chips,
)


def render_chat_interface():
    """Renders the conversational customer shopping and support assistant."""
    st.title("⚡ VoltKart AI Shopping & Support Assistant")
    st.caption("Ask questions about laptop specs, request personalized recommendations, compare models, or check store policies.")

    # Initialize Backend Services
    conv_svc = ConversationService()
    gemini_svc = GeminiService()
    intent_svc = IntentService(gemini_service=gemini_svc)
    rec_svc = RecommendationService(gemini_service=gemini_svc, conversation_service=conv_svc)
    comp_svc = ComparisonService(gemini_service=gemini_svc)
    faq_svc = FaqService(gemini_service=gemini_svc)

    # Initialize Session State
    if "conversation_id" not in st.session_state or not st.session_state.conversation_id:
        st.session_state.conversation_id = conv_svc.create_conversation("New Shopping Chat")

    if "messages" not in st.session_state:
        # Load any existing turns from MongoDB or start fresh
        db_history = conv_svc.get_conversation_history(st.session_state.conversation_id)
        if db_history:
            st.session_state.messages = db_history
        else:
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": (
                        "Hello! Welcome to **VoltKart**! ⚡ I am your dedicated laptop specialist. "
                        "Tell me what you are looking for (e.g. *'Suggest a coding laptop under ₹60,000'*), "
                        "ask to compare models, or ask about our return and warranty policies."
                    ),
                    "intent": "general",
                    "products": [],
                }
            ]

    # Suggestion Chips
    chip_query = render_suggestion_chips()

    # Display Chat Timeline
    for msg in st.session_state.messages:
        role = msg.get("role", "assistant")
        with st.chat_message(role):
            st.markdown(msg.get("content", ""))

            # Render recommendation cards if products attached
            products = msg.get("products", [])
            intent = msg.get("intent")
            if products and intent == "recommend":
                render_product_cards(products)
            elif products and intent == "compare":
                render_comparison_table(products)

    # Chat Input
    user_input = st.chat_input("Type your question or requirement (e.g. 'Laptop for college under 50k')...")

    active_prompt = chip_query or user_input

    if active_prompt:
        cid = st.session_state.conversation_id

        # 1. Append User Message to UI State & MongoDB
        user_msg_entry = {"role": "user", "content": active_prompt, "intent": None}
        st.session_state.messages.append(user_msg_entry)
        conv_svc.save_message(cid, "user", active_prompt)

        # Update title if first user message
        if len(st.session_state.messages) <= 3:
            conv_svc.update_conversation_title(cid, active_prompt)

        # Display immediately in UI
        with st.chat_message("user"):
            st.markdown(active_prompt)

        # 2. Process Assistant Turn
        with st.chat_message("assistant"):
            with st.spinner("⚡ Consulting store database & verifying catalog..."):
                history = st.session_state.messages[:-1]

                # Stage 1: Intent Extraction
                intent_data = intent_svc.parse_intent(active_prompt, history=history)
                intent = intent_data.get("intent", "general")

                response_text = ""
                turn_products = []

                # Stage 2: Route & Execute Decoupled Pipeline
                if intent == "recommend":
                    rec_result = rec_svc.process_recommendation(
                        user_query=active_prompt,
                        conversation_id=cid,
                        intent_data=intent_data,
                        history=history,
                    )
                    response_text = rec_result["response_text"]
                    turn_products = rec_result["products"]

                elif intent == "compare":
                    comp_result = comp_svc.process_comparison(
                        user_query=active_prompt,
                        conversation_id=cid,
                        intent_data=intent_data,
                        history=history,
                    )
                    response_text = comp_result["response_text"]
                    turn_products = comp_result["products"]

                elif intent == "support":
                    faq_result = faq_svc.process_support(
                        user_query=active_prompt,
                        intent_data=intent_data,
                        history=history,
                    )
                    response_text = faq_result["response_text"]

                elif intent == "out_of_scope":
                    response_text = gemini_svc.generate_grounded_response(
                        user_query=active_prompt,
                        intent="out_of_scope",
                        retrieved_docs=[],
                        history=history,
                    )

                else:  # general or fallback
                    response_text = gemini_svc.generate_grounded_response(
                        user_query=active_prompt,
                        intent="general",
                        retrieved_docs=[],
                        history=history,
                    )

                # Render Response
                st.markdown(response_text)
                if turn_products and intent == "recommend":
                    render_product_cards(turn_products)
                elif turn_products and intent == "compare":
                    render_comparison_table(turn_products)

                # Save Assistant Message
                retrieved_ids = [p.get("product_id") for p in turn_products] if turn_products else []
                conv_svc.save_message(cid, "assistant", response_text, intent=intent, retrieved_ids=retrieved_ids)

                assistant_entry = {
                    "role": "assistant",
                    "content": response_text,
                    "intent": intent,
                    "products": turn_products,
                }
                st.session_state.messages.append(assistant_entry)

        st.rerun()
