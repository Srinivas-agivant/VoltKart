"""VoltKart - Premium Laptop E-Commerce Storefront & AI Shopping Assistant.

Main Streamlit application entry point. Run with:
    streamlit run app.py
"""

from pathlib import Path
import streamlit as st

import config
from database import get_db
from backend.file_processor import FileProcessor
from backend.data_validator import DataValidator
from backend.data_importer import DataImporter
from backend.knowledge_base_service import KnowledgeBaseService
from frontend.storefront import render_storefront
from frontend.floating_chat import render_floating_chatbot

# Configure Streamlit Page
st.set_page_config(
    page_title="VoltKart - Find Your Perfect Laptop",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Global UI Polish & Light-Red Theme
global_css = """
<style>
/* Modern Elegant Light-Red / Rose-Toned Canvas */
html, body, .stApp, [data-testid="stApp"], [data-testid="stAppViewContainer"], .stAppViewContainer, [data-testid="stMain"], section.main, .main, [data-testid="stMainBlockContainer"], .block-container {
    background-color: #fff1f2 !important;
    background: linear-gradient(180deg, #fff1f2 0%, #fef2f2 40%, #fff5f5 100%) !important;
    color: #0f172a !important;
}
header[data-testid="stHeader"] {
    background: transparent !important;
}

/* Completely hide Streamlit sidebar and toggle handle */
section[data-testid="stSidebar"] {
    display: none !important;
    width: 0px !important;
}
div[data-testid="collapsedControl"] {
    display: none !important;
}
.main .block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1300px !important;
}

/* Headings and General Typography */
h1, h2, h3, h4, h5, h6 {
    color: #0f172a !important;
    font-weight: 700 !important;
}
p, span, label {
    color: #334155;
}

/* Brand Header Styles */
.brand-logo-text {
    font-size: 1.85rem;
    font-weight: 800;
    color: #0f172a !important;
    letter-spacing: -0.5px;
    display: flex;
    align-items: center;
    gap: 8px;
    text-decoration: none;
}

/* Top Navigation Radio Tabs */
div[data-testid="stRadio"] > div {
    background: #ffffff !important;
    border: 1px solid #fecdd3 !important;
    border-radius: 10px !important;
    padding: 3px 8px !important;
    gap: 6px !important;
    box-shadow: 0 1px 3px rgba(225, 29, 72, 0.06) !important;
}
div[data-testid="stRadio"] label p {
    color: #475569 !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
}
div[data-testid="stRadio"] label:hover p {
    color: #e11d48 !important;
}

/* Search Widget Styling */
div[data-testid="stTextInput"] input {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border: 1.5px solid #fecdd3 !important;
    border-radius: 8px !important;
    font-size: 0.92rem !important;
    box-shadow: 0 1px 4px rgba(225, 29, 72, 0.06) !important;
}
div[data-testid="stTextInput"] input::placeholder {
    color: #94a3b8 !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #e11d48 !important;
    box-shadow: 0 0 0 3px rgba(225, 29, 72, 0.18) !important;
}

/* Expanders */
details[data-testid="stExpander"] {
    background-color: #ffffff !important;
    border: 1px solid #fecdd3 !important;
    border-radius: 10px !important;
    box-shadow: 0 1px 4px rgba(225, 29, 72, 0.05) !important;
}
details[data-testid="stExpander"] summary {
    color: #0f172a !important;
    font-weight: 600 !important;
}
details[data-testid="stExpander"] summary:hover {
    color: #e11d48 !important;
}
details[data-testid="stExpander"] summary svg {
    fill: #e11d48 !important;
}

/* Selectbox */
div[data-testid="stSelectbox"] > div > div {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border: 1.5px solid #fecdd3 !important;
    border-radius: 8px !important;
}
div[data-testid="stSelectbox"] svg {
    fill: #64748b !important;
}

/* Buttons */
div.stButton button {
    background-color: #ffffff !important;
    color: #e11d48 !important;
    border: 1.5px solid #fecdd3 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.15s ease !important;
}
div.stButton button:hover {
    background-color: #fff1f2 !important;
    border-color: #e11d48 !important;
    color: #be123c !important;
}

/* Footer Container */
.footer-container {
    margin-top: 60px;
    padding: 30px 20px;
    border-top: 1px solid #fecdd3;
    color: #64748b;
    font-size: 0.88rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
}
</style>
"""
st.markdown(global_css, unsafe_allow_html=True)


def auto_seed_default_catalog():
    """Automatically seeds default synthetic catalog & PDF knowledge base on first launch if empty."""
    db = get_db()
    products_count = db[config.COLLECTION_PRODUCTS].count_documents({})
    if products_count == 0:
        importer = DataImporter(db=db)
        seed_files = [
            ("data/sample_products.csv", "products", "sample_products.csv"),
            ("data/sample_faqs.csv", "faqs", "sample_faqs.csv"),
            ("data/sample_policies.csv", "policies", "sample_policies.csv"),
        ]
        for fpath, dt, fname in seed_files:
            if Path(fpath).exists():
                try:
                    df = FileProcessor.read_file(fpath, fname)
                    mapping = FileProcessor.auto_map_columns(list(df.columns), dt)
                    df_mapped = FileProcessor.apply_mapping(df, mapping)
                    valid, invalid = DataValidator.clean_and_validate(df_mapped, dt, fname)
                    importer.import_records(valid, dt, fname, mode="update", invalid_records=invalid)
                except Exception:
                    pass

    # Auto-seed sample store policy PDF into knowledge base if empty
    kb_count = db[config.COLLECTION_KNOWLEDGE_BASE].count_documents({})
    if kb_count == 0:
        pdf_path = Path("data/sample_store_policy.pdf")
        if pdf_path.exists():
            try:
                kb_svc = KnowledgeBaseService(db=db)
                with open(pdf_path, "rb") as f:
                    kb_svc.ingest_pdf(
                        file_input=f.read(),
                        filename="sample_store_policy.pdf",
                        category="Return Policy",
                        replace=True,
                    )
            except Exception:
                pass


# Run auto-seed
auto_seed_default_catalog()


def main():
    # Clean, Streamlined Customer Navigation Bar (Brand, Menu, Search Widget)
    nav_col1, nav_col2, nav_col3 = st.columns([1.2, 1.5, 1.8])

    # 1. Brand Identity: Simple, bold VoltKart with lightning symbol (no extra badges)
    with nav_col1:
        brand_html = (
            '<div class="brand-logo-text" style="padding-top: 6px;">'
            '<span style="font-size: 2.1rem; color: #e11d48;">⚡</span>'
            '<span style="font-size: 1.85rem; font-weight: 800; color: #0f172a; letter-spacing: -0.5px;">VoltKart</span>'
            '</div>'
        )
        st.markdown(brand_html, unsafe_allow_html=True)

    # 2. Main Navigation Links: Home, About Us, Contact (Catalogue is on Home)
    with nav_col2:
        nav_selection = st.radio(
            "Storefront Navigation",
            options=["Home", "About Us", "Contact"],
            horizontal=True,
            label_visibility="collapsed",
            key="top_navbar",
        )

    # 3. Dynamic Search Input Widget with Search Icon Prefix & Clear Action
    with nav_col3:
        scol1, scol2 = st.columns([5, 1])
        with scol1:
            header_search = st.text_input(
                "Search laptops by name, brand or specifications...",
                placeholder="🔍 Search name, brand, specs...",
                key="header_search_input",
                label_visibility="collapsed",
            )
        with scol2:
            if header_search:
                if st.button("✖", key="clear_header_search", help="Clear search"):
                    st.session_state.header_search_input = ""
                    st.rerun()

    st.markdown("<hr style='margin: 8px 0 24px 0; border: none; border-top: 1px solid #fecdd3;'>", unsafe_allow_html=True)

    # Render Active Storefront View (Home, About Us, Contact) - Catalogue is rendered on Home
    render_storefront(nav_selection=nav_selection, header_search=header_search)

    # Persistent Floating AI Assistant (Always fixed at bottom-right)
    render_floating_chatbot()

    # Clean E-Commerce Footer
    footer_html = (
        '<div class="footer-container">'
        '<div>'
        '<b>VoltKart Technologies Pvt Ltd</b> &copy; 2026. All rights reserved.'
        '<div style="font-size:0.78rem; color:#94a3b8; margin-top:4px;">'
        'Authorized retailer for Lenovo, HP, Dell, Asus, Apple & Acer laptops.'
        '</div>'
        '</div>'
        '<div style="text-align:right;">'
        '<div>📞 <b>Helpline</b>: 1800-VOLT-KART | 📧 <b>Support</b>: support@voltkart.com</div>'
        '<div style="font-size:0.78rem; color:#94a3b8; margin-top:4px;">Free insured shipping across India • 7-day return guarantee</div>'
        '</div>'
        '</div>'
    )
    st.markdown(footer_html, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
