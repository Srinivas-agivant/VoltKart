"""Reusable UI components for VoltKart Streamlit interface.

Compact variants are used inside the floating chat panel (430px width).
Full-width variants are used in the main storefront body.
"""

import pandas as pd
import streamlit as st


def render_product_cards(products: list[dict], compact: bool = True, key_prefix: str = "") -> str | None:
    """Renders product recommendation cards.

    Args:
        products: List of product dictionaries from MongoDB.
        compact: If True, renders vertically stacked compact cards (for chat panel).
                 If False, renders side-by-side 3-column cards (for storefront).
        key_prefix: Unique key prefix for Streamlit widgets.

    Returns:
        clicked_prompt: Optional user prompt if an interactive card button was clicked.
    """
    if not products:
        return None

    clicked_prompt = None

    if compact:
        # Compact stacked layout for the 430px-wide floating chat panel
        st.markdown("**⚡ Recommended Laptops:**")
        for idx, prod in enumerate(products, start=1):
            with st.container(border=True):
                name = prod.get("name") or prod.get("model", "Laptop")
                price = prod.get("price") or prod.get("price_inr", 0)
                brand = prod.get("brand") or prod.get("store", "VoltKart")
                proc = prod.get("processor", "")
                ram = prod.get("ram", "")
                storage = prod.get("storage", "")
                reason = prod.get("recommendation_reason", "")

                card_text = (
                    f"**#{idx} {name}**\n\n"
                    f"💰 ₹{float(price):,.0f} · {brand}\n\n"
                    f"⚙️ {proc} · {ram} · {storage}"
                )
                if reason:
                    card_text += f"\n\n💡 _{reason}_"

                st.markdown(card_text)

                # Interactive in-card action buttons
                col1, col2 = st.columns(2)
                safe_name = "".join(c for c in name if c.isalnum())
                if col1.button(f"🔍 Specs", key=f"btn_spec_{key_prefix}_{idx}_{safe_name}", use_container_width=True):
                    clicked_prompt = f"Tell me full specifications and details for {name}"
                if col2.button(f"🔋 Battery", key=f"btn_batt_{key_prefix}_{idx}_{safe_name}", use_container_width=True):
                    clicked_prompt = f"What is the battery life and warranty for {name}?"

        return clicked_prompt
    else:
        # Full-width side-by-side layout for storefront
        st.markdown("### ⚡ Recommended Laptops")
        cols = st.columns(min(len(products), 3))

        for idx, (col, prod) in enumerate(zip(cols, products), start=1):
            with col:
                with st.container(border=True):
                    name = prod.get("name") or prod.get("model", "Laptop")
                    st.markdown(f"#### #{idx} {name}")
                    st.markdown(
                        f"**Brand**: {prod.get('brand', 'VoltKart')} | "
                        f"**Category**: `{(prod.get('usage_type') or 'general').capitalize()}`"
                    )
                    st.markdown(f"### ₹{float(prod.get('price', 0)):,.0f}")

                    st.markdown("---")
                    st.markdown(f"💻 **CPU**: {prod.get('processor', 'N/A')}")
                    st.markdown(f"🧠 **RAM**: {prod.get('ram', 'N/A')}")
                    st.markdown(f"💾 **Storage**: {prod.get('storage', 'N/A')}")
                    st.markdown(f"🖥️ **Display**: {prod.get('display', 'N/A')}")
                    st.markdown(f"🎮 **Graphics**: {prod.get('graphics', 'N/A')}")
                    st.markdown(f"🔋 **Battery**: {prod.get('battery_life', 'N/A')}")
                    st.markdown(f"⚖️ **Weight**: {prod.get('weight', 'N/A')}")
                    st.markdown(f"🛡️ **Warranty**: {prod.get('warranty', 'N/A')}")

                    reason = prod.get("recommendation_reason")
                    if reason:
                        st.info(f"💡 **Why Recommended**: {reason}")

        return None


def render_comparison_table(products: list[dict], compact: bool = True):
    """Renders a side-by-side comparison table of 2 or more laptops.

    Args:
        products: List of product dictionaries.
        compact: If True, renders a compact vertical comparison (for chat panel).
    """
    if not products or len(products) < 2:
        return

    if compact:
        # Compact vertical comparison for 430px chat panel
        st.markdown("**📊 Laptop Comparison:**")
        for idx, p in enumerate(products, start=1):
            with st.container(border=True):
                name = p.get("name") or p.get("model", f"Laptop {idx}")
                price = p.get("price") or p.get("price_inr", 0)
                st.markdown(
                    f"**#{idx} {name}** — ₹{float(price):,.0f}\n\n"
                    f"⚙️ {p.get('processor', 'N/A')} · {p.get('ram', 'N/A')} · {p.get('storage', 'N/A')}\n\n"
                    f"🎮 {p.get('graphics', 'N/A')} · 🔋 {p.get('battery_life', 'N/A')}"
                )
    else:
        # Full-width table for storefront
        st.markdown("### 📊 Side-by-Side Laptop Comparison")

        data = {
            "Attribute": [
                "Price", "Processor", "RAM", "Storage", "Display",
                "Graphics", "Battery Life", "Weight", "Warranty", "Target Usage",
            ]
        }

        for idx, p in enumerate(products, start=1):
            name = p.get("name") or p.get("model", f"Laptop {idx}")
            col_header = f"#{idx} {name}"
            data[col_header] = [
                f"₹{float(p.get('price', 0)):,.0f}",
                p.get("processor", "N/A"),
                p.get("ram", "N/A"),
                p.get("storage", "N/A"),
                p.get("display", "N/A"),
                p.get("graphics", "N/A"),
                p.get("battery_life", "N/A"),
                p.get("weight", "N/A"),
                p.get("warranty", "N/A"),
                (p.get("usage_type") or "general").capitalize(),
            ]

        df_comp = pd.DataFrame(data)
        st.dataframe(df_comp, use_container_width=True, hide_index=True)


def render_suggestion_chips(compact: bool = True, key_prefix: str = "") -> str | None:
    """Renders clickable prompt chips for instant guidance.

    Args:
        compact: If True, uses 2-column layout with short labels (for chat panel).
        key_prefix: Unique key prefix for widget keys.
    """
    clicked_prompt = None

    if compact:
        # 2x2 grid with short labels that fit in 430px chat panel
        st.markdown("**Quick Inquiries:**")
        r1c1, r1c2 = st.columns(2)
        r2c1, r2c2 = st.columns(2)

        if r1c1.button("🎒 Student < ₹50k", key=f"chip_student_{key_prefix}", use_container_width=True):
            clicked_prompt = "Suggest a laptop for college student under Rs. 50000 with good battery life"
        if r1c2.button("💻 Coding < ₹70k", key=f"chip_coding_{key_prefix}", use_container_width=True):
            clicked_prompt = "Best coding laptop under Rs. 70000 with 16GB RAM"
        if r2c1.button("🎮 Gaming < ₹75k", key=f"chip_gaming_{key_prefix}", use_container_width=True):
            clicked_prompt = "Suggest a gaming laptop under Rs. 75000"
        if r2c2.button("📦 Returns & Ship", key=f"chip_support_{key_prefix}", use_container_width=True):
            clicked_prompt = "What is your return policy and do you offer free shipping?"
    else:
        # Full-width 4-column layout
        st.markdown("**Suggested Inquiries:**")
        col1, col2, col3, col4 = st.columns(4)

        if col1.button("🎒 Student Laptop < ₹50k", key=f"chip_student_{key_prefix}", use_container_width=True):
            clicked_prompt = "Suggest a laptop for college student under Rs. 50000 with good battery life"
        if col2.button("💻 Coding Laptop < ₹70k", key=f"chip_coding_{key_prefix}", use_container_width=True):
            clicked_prompt = "Best coding laptop under Rs. 70000 with 16GB RAM"
        if col3.button("🎮 Gaming Laptop < ₹75k", key=f"chip_gaming_{key_prefix}", use_container_width=True):
            clicked_prompt = "Suggest a gaming laptop under Rs. 75000"
        if col4.button("📦 Return & Shipping FAQs", key=f"chip_support_{key_prefix}", use_container_width=True):
            clicked_prompt = "What is your return policy and do you offer free shipping?"

    return clicked_prompt


def render_followup_chips(products: list[dict], key_prefix: str = "") -> str | None:
    """Renders interactive follow-up suggestion chips after recommendations.

    Args:
        products: List of recommended product dictionaries.
        key_prefix: Unique key prefix for widget keys.
    """
    if not products:
        return None

    clicked_prompt = None
    st.markdown("**💡 Quick Follow-ups:**")
    fcol1, fcol2 = st.columns(2)

    if len(products) >= 2:
        if fcol1.button("📊 Compare Top 2", key=f"fup_comp_{key_prefix}", use_container_width=True):
            clicked_prompt = "Compare the top 2 recommended laptops side-by-side with full specifications"
        if fcol2.button("🔋 Best Battery?", key=f"fup_batt_{key_prefix}", use_container_width=True):
            clicked_prompt = "Which of these recommended laptops has the longest battery life?"
    else:
        if fcol1.button("💰 Cheaper Options?", key=f"fup_cheap_{key_prefix}", use_container_width=True):
            clicked_prompt = "Show me cheaper alternative laptops with good performance"
        if fcol2.button("🛡️ Warranty Info?", key=f"fup_warr_{key_prefix}", use_container_width=True):
            clicked_prompt = "What warranty coverage and support is provided with this laptop?"

    return clicked_prompt
