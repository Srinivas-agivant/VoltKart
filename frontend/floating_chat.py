"""Floating VoltKart AI Assistant Chatbot widget anchored at fixed bottom-right."""

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
    render_followup_chips,
)


def render_floating_chatbot():
    """Renders the persistent floating chatbot widget strictly fixed to bottom-right corner."""
    # Manage Open / Minimized State
    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False

    # Initialize Backend Services
    conv_svc = ConversationService()
    gemini_svc = GeminiService()
    intent_svc = IntentService(gemini_service=gemini_svc)
    rec_svc = RecommendationService(gemini_service=gemini_svc, conversation_service=conv_svc)
    comp_svc = ComparisonService(gemini_service=gemini_svc)
    faq_svc = FaqService(gemini_service=gemini_svc)

    # Initialize Session Conversation
    if "conversation_id" not in st.session_state or not st.session_state.conversation_id:
        st.session_state.conversation_id = conv_svc.create_conversation("Storefront Chat")

    # Initial Welcome Greeting
    welcome_text = "Hi! Welcome to VoltKart. I'm your AI shopping assistant. How can I help you today?"

    if "messages" not in st.session_state or not st.session_state.messages:
        db_history = conv_svc.get_conversation_history(st.session_state.conversation_id)
        if db_history:
            st.session_state.messages = db_history
        else:
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": welcome_text,
                    "intent": "general",
                    "products": [],
                }
            ]

    # Inject Viewport-Fixed CSS Rules — strictly scoped by Streamlit keys to avoid affecting page containers
    chat_css = (
        '<style>'
        # --- Floating Circular Chat Launcher (Bottom-Right Viewport-Fixed) ---
        '.st-key-floating_launcher_wrap {'
        '  position: fixed !important;'
        '  bottom: 28px !important;'
        '  right: 28px !important;'
        '  z-index: 9999999 !important;'
        '  width: 66px !important;'
        '  height: 66px !important;'
        '  min-width: 66px !important;'
        '  min-height: 66px !important;'
        '  padding: 0 !important;'
        '  margin: 0 !important;'
        '  background: transparent !important;'
        '  box-shadow: none !important;'
        '  border: none !important;'
        '}'
        '.st-key-floating_launcher_wrap div[data-testid="stElementContainer"],'
        '.st-key-floating_launcher_wrap .stButton,'
        '.st-key-floating_open_btn {'
        '  width: 66px !important;'
        '  height: 66px !important;'
        '  min-width: 66px !important;'
        '  min-height: 66px !important;'
        '  padding: 0 !important;'
        '  margin: 0 !important;'
        '  background: transparent !important;'
        '  box-shadow: none !important;'
        '  border: none !important;'
        '}'
        '.st-key-floating_open_btn button {'
        '  position: fixed !important;'
        '  bottom: 28px !important;'
        '  right: 28px !important;'
        '  z-index: 9999999 !important;'
        '  width: 66px !important;'
        '  height: 66px !important;'
        '  min-width: 66px !important;'
        '  min-height: 66px !important;'
        '  border-radius: 50% !important;'
        '  background: linear-gradient(135deg, #e11d48 0%, #be123c 100%) !important;'
        '  color: #ffffff !important;'
        '  font-size: 32px !important;'
        '  line-height: 1 !important;'
        '  padding: 0 !important;'
        '  border: 2.5px solid #ffffff !important;'
        '  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.16), 0 2px 6px rgba(0, 0, 0, 0.08) !important;'
        '  cursor: pointer !important;'
        '  display: flex !important;'
        '  align-items: center !important;'
        '  justify-content: center !important;'
        '  transition: transform 0.22s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.22s ease !important;'
        '  margin: 0 !important;'
        '  pointer-events: auto !important;'
        '}'
        '.st-key-floating_open_btn button p {'
        '  font-size: 30px !important;'
        '  line-height: 1 !important;'
        '  margin: 0 !important;'
        '  padding: 0 !important;'
        '  color: #ffffff !important;'
        '}'
        '.st-key-floating_open_btn button:hover {'
        '  transform: scale(1.10) !important;'
        '  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.22), 0 2px 8px rgba(0, 0, 0, 0.10) !important;'
        '  background: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%) !important;'
        '}'
        # --- Floating Chat Window Overlay (Bottom-Right Viewport-Fixed) ---
        '.st-key-floating_chat_panel {'
        '  position: fixed !important;'
        '  bottom: 24px !important;'
        '  right: 24px !important;'
        '  width: 420px !important;'
        '  max-width: calc(100vw - 32px) !important;'
        '  height: 600px !important;'
        '  max-height: calc(100vh - 48px) !important;'
        '  background: #ffffff !important;'
        '  border: 1.5px solid #fecdd3 !important;'
        '  border-radius: 18px !important;'
        '  box-shadow: 0 20px 45px -10px rgba(0, 0, 0, 0.18), 0 8px 20px rgba(0, 0, 0, 0.06) !important;'
        '  z-index: 9999999 !important;'
        '  overflow: hidden !important;'
        '  padding: 14px 16px !important;'
        '  display: flex !important;'
        '  flex-direction: column !important;'
        '}'
        # --- Force all chat content to respect the 420px panel width ---
        '.st-key-floating_chat_panel * {'
        '  max-width: 100% !important;'
        '  overflow-wrap: break-word !important;'
        '  word-wrap: break-word !important;'
        '}'
        '.st-key-floating_chat_panel [data-testid="column"] {'
        '  min-width: 0 !important;'
        '}'
        # --- Make chat messages compact & styled ---
        '.st-key-floating_chat_panel [data-testid="stChatMessage"] {'
        '  padding: 8px 10px !important;'
        '  gap: 8px !important;'
        '  background-color: #fff1f2 !important;'
        '  border: 1px solid #fecdd3 !important;'
        '  border-radius: 12px !important;'
        '}'
        '.st-key-floating_chat_panel [data-testid="stChatMessage"] p,'
        '.st-key-floating_chat_panel [data-testid="stChatMessage"] span {'
        '  font-size: 0.86rem !important;'
        '  line-height: 1.45 !important;'
        '  color: #0f172a !important;'
        '}'
        # --- In-chat product card containers ---
        '.st-key-floating_chat_panel div[data-testid="stVerticalBlockBorderWrapper"] {'
        '  background-color: #ffffff !important;'
        '  border: 1px solid #fecdd3 !important;'
        '  border-radius: 10px !important;'
        '}'
        # --- Compact buttons inside chat panel ---
        '.st-key-floating_chat_panel .stButton button {'
        '  background-color: #fff1f2 !important;'
        '  color: #be123c !important;'
        '  border: 1px solid #fecdd3 !important;'
        '  font-size: 0.72rem !important;'
        '  padding: 4px 6px !important;'
        '  min-height: 28px !important;'
        '  border-radius: 6px !important;'
        '}'
        '.st-key-floating_chat_panel .stButton button:hover {'
        '  background-color: #ffe4e6 !important;'
        '  border-color: #e11d48 !important;'
        '  color: #9f1239 !important;'
        '}'
        '</style>'
    )
    st.markdown(chat_css, unsafe_allow_html=True)

    if not st.session_state.chat_open:
        # Render Fixed Bottom-Right Floating Circular Icon with explicit container key
        with st.container(key="floating_launcher_wrap"):
            if st.button("💬", key="floating_open_btn", help="Open VoltKart AI Assistant"):
                st.session_state.chat_open = True
                st.rerun()
    else:
        # Render Fixed Floating Chat Window Overlay with explicit container key
        with st.container(key="floating_chat_panel"):
            # Chat Header with Title, Reset, and Close buttons
            hcol1, hcol2, hcol3 = st.columns([4, 1, 1])
            with hcol1:
                header_html = (
                    '<div style="display:flex; align-items:center; gap:8px;">'
                    '<span style="font-size:1.3rem; color:#e11d48;">⚡</span>'
                    '<div>'
                    '<div style="font-weight:800; font-size:0.92rem; color:#0f172a;">VoltKart AI Assistant</div>'
                    '<div style="font-size:0.68rem; color:#64748b;">Grounded Store Expert • Always Live</div>'
                    '</div>'
                    '</div>'
                )
                st.markdown(header_html, unsafe_allow_html=True)
            with hcol2:
                if st.button("🔄", key="floating_reset_btn", help="Start New Chat Session"):
                    new_cid = conv_svc.create_conversation("Storefront Chat")
                    st.session_state.conversation_id = new_cid
                    st.session_state.messages = [
                        {
                            "role": "assistant",
                            "content": welcome_text,
                            "intent": "general",
                            "products": [],
                        }
                    ]
                    st.rerun()
            with hcol3:
                if st.button("✖", key="floating_close_btn", help="Close Assistant"):
                    st.session_state.chat_open = False
                    st.rerun()

            # Initial Suggestion Chips (shown when conversation is at starting state)
            chip_query = None
            has_history = len(st.session_state.messages) > 1
            if not has_history:
                chip_query = render_suggestion_chips(compact=True, key_prefix="initial")

            pending_action_prompt = None

            # Message Timeline (scrollable area with dynamic height)
            timeline_height = 400 if has_history else 300
            timeline_container = st.container(height=timeline_height)
            with timeline_container:
                for idx, msg in enumerate(st.session_state.messages):
                    role = msg.get("role", "assistant")
                    with st.chat_message(role):
                        st.markdown(msg.get("content", ""))

                        products = msg.get("products", [])
                        intent = msg.get("intent")
                        if products and intent == "recommend":
                            card_prompt = render_product_cards(products, compact=True, key_prefix=f"m_{idx}")
                            if card_prompt:
                                pending_action_prompt = card_prompt

                            # Render interactive follow-up chips under the latest recommendation turn
                            if idx == len(st.session_state.messages) - 1:
                                fup_prompt = render_followup_chips(products, key_prefix=f"m_{idx}")
                                if fup_prompt:
                                    pending_action_prompt = fup_prompt

                        elif products and intent == "compare":
                            render_comparison_table(products, compact=True)

            # Chat Input Field
            user_input = st.chat_input("Ask about laptops, specs, policies...", key="floating_chat_input")
            active_prompt = pending_action_prompt or chip_query or user_input

            if active_prompt:
                cid = st.session_state.conversation_id

                # Save & Display User Turn
                st.session_state.messages.append({"role": "user", "content": active_prompt, "intent": None})
                conv_svc.save_message(cid, "user", active_prompt)

                if len(st.session_state.messages) <= 3:
                    conv_svc.update_conversation_title(cid, active_prompt)

                with timeline_container:
                    with st.chat_message("user"):
                        st.markdown(active_prompt)

                    with st.chat_message("assistant"):
                        with st.spinner("⚡ Finding verified information..."):
                            history = st.session_state.messages[:-1]
                            intent_data = intent_svc.parse_intent(active_prompt, history=history)
                            intent = intent_data.get("intent", "general")

                            response_text = ""
                            turn_products = []

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

                            else:
                                response_text = gemini_svc.generate_grounded_response(
                                    user_query=active_prompt,
                                    intent="general",
                                    retrieved_docs=[],
                                    history=history,
                                )

                            st.markdown(response_text)
                            if turn_products and intent == "recommend":
                                render_product_cards(turn_products, compact=True, key_prefix="live")
                            elif turn_products and intent == "compare":
                                render_comparison_table(turn_products, compact=True)

                            # Save Turn in Database
                            retrieved_ids = [p.get("product_id") for p in turn_products] if turn_products else []
                            conv_svc.save_message(cid, "assistant", response_text, intent=intent, retrieved_ids=retrieved_ids)
                            st.session_state.messages.append(
                                {
                                    "role": "assistant",
                                    "content": response_text,
                                    "intent": intent,
                                    "products": turn_products,
                                }
                            )

                st.rerun()
