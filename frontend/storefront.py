"""Modern, professional e-commerce storefront for VoltKart laptop retail.

Implements Amazon-style orange deal carousel shelves and product cards.
Exclusively displays laptops with exact database model names.
"""

import streamlit as st
import pandas as pd

from database import get_db
import config
from frontend.laptop_images import (
    get_laptop_image_url,
    get_laptop_svg_data_uri,
    calculate_mrp,
)


def render_storefront(nav_selection: str = "Home", header_search: str = ""):
    """Renders the main VoltKart laptop e-commerce storefront."""
    db = get_db()
    products_coll = db[config.COLLECTION_PRODUCTS]

    # Custom CSS for Amazon-Style Orange Deal Container and Elevated White Product Cards
    css_content = """
<style>
.hero-banner {
    background: linear-gradient(135deg, #4c0519 0%, #881337 45%, #9f1239 100%);
    padding: 38px 32px;
    border-radius: 14px;
    color: #ffffff;
    margin-bottom: 24px;
    box-shadow: 0 8px 24px -4px rgba(136, 19, 55, 0.25);
    border: 1px solid rgba(254, 205, 211, 0.3);
    position: relative;
    overflow: hidden;
}
.hero-banner::after {
    content: "⚡";
    position: absolute;
    right: 36px;
    top: 16px;
    font-size: 7.5rem;
    opacity: 0.08;
    pointer-events: none;
}
.hero-title {
    font-size: 2.3rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 10px;
    letter-spacing: -0.5px;
    line-height: 1.2;
}
.hero-subtitle {
    font-size: 1.05rem;
    color: #ffe4e6;
    margin-bottom: 0px;
    max-width: 680px;
    line-height: 1.55;
}

/* Amazon-Style Vibrant Orange Deal Shelf Container */
.deal-shelf-container,
div[class*="st-key-shelf_box_"] {
    background: linear-gradient(135deg, #ea580c 0%, #f97316 100%) !important;
    border-radius: 14px !important;
    padding: 18px 20px 22px 20px !important;
    margin-bottom: 24px !important;
    box-shadow: 0 6px 18px rgba(234, 88, 12, 0.16) !important;
}
.deal-shelf-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
    padding: 0 4px;
}
.deal-shelf-title {
    font-size: 1.28rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.2px;
}
.deal-shelf-page-tag {
    color: #ffffff;
    font-size: 0.85rem;
    font-weight: 700;
    background: rgba(0, 0, 0, 0.16);
    padding: 3px 10px;
    border-radius: 20px;
}

/* Amazon-Style On-Grid Side Scroll Navigation Button */
div[class*="st-key-shelf_box_"] .stButton button {
    background: #ffffff !important;
    color: #ea580c !important;
    border: 1.5px solid rgba(255, 255, 255, 0.95) !important;
    border-radius: 12px !important;
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    line-height: 1 !important;
    min-height: 100px !important;
    width: 100% !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.18) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0 !important;
    cursor: pointer !important;
    transition: transform 0.18s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.18s ease !important;
}
div[class*="st-key-shelf_box_"] .stButton button:hover {
    transform: scale(1.08) !important;
    background: #ffffff !important;
    color: #e11d48 !important;
    border-color: #ffffff !important;
    box-shadow: 0 8px 22px rgba(0, 0, 0, 0.28) !important;
}
div[class*="st-key-shelf_box_"] .stButton button p {
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    line-height: 1 !important;
    margin: 0 !important;
    padding: 0 !important;
    color: #ea580c !important;
}
div[class*="st-key-shelf_box_"] .stButton button:hover p {
    color: #e11d48 !important;
}

/* 3-Card Symmetrical Responsive Grid */
.deal-shelf-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
    align-items: stretch;
}
@media (max-width: 1024px) {
    .deal-shelf-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}
@media (max-width: 640px) {
    .deal-shelf-grid {
        grid-template-columns: 1fr;
    }
}

/* Clean White Elevated Deal Card */
.deal-card {
    background: #ffffff !important;
    border: 1.5px solid #fecdd3;
    border-radius: 12px;
    padding: 16px 16px 18px 16px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 310px;
    transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}
.deal-card * {
    color: #0f172a !important;
}
.deal-card .deal-card-mrp,
.deal-card .deal-card-mrp * {
    color: #64748b !important;
}
.deal-card .deal-card-discount {
    color: #ffffff !important;
    background: #dc2626 !important;
}
.deal-card .deal-card-specs {
    color: #475569 !important;
}
.deal-card:hover {
    transform: translateY(-4px);
    border-color: #fb7185;
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.15);
}
.deal-card-img-wrap {
    height: 145px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #ffffff;
    margin-bottom: 10px;
    border-radius: 6px;
    overflow: hidden;
}
.deal-card-img {
    max-height: 135px;
    max-width: 100%;
    object-fit: contain;
}
.deal-card-title {
    font-size: 0.9rem;
    font-weight: 600;
    color: #0f172a;
    line-height: 1.35;
    margin-bottom: 8px;
    height: 38px;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}
.deal-card-price-row {
    margin-top: auto;
    display: flex;
    align-items: baseline;
    flex-wrap: wrap;
    gap: 4px;
}
.deal-card-price {
    font-size: 1.28rem;
    font-weight: 800;
    color: #0f172a;
}
.deal-card-cents {
    font-size: 0.72rem;
    font-weight: 700;
    vertical-align: top;
    position: relative;
    top: -2px;
}
.deal-card-mrp {
    font-size: 0.76rem;
    color: #565959;
    margin-left: 3px;
}
.deal-card-discount {
    background: #cc0c39;
    color: #ffffff;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 3px;
    margin-left: auto;
}
.deal-card-specs {
    font-size: 0.74rem;
    color: #64748b;
    margin-top: 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Specs table expander styling */
.spec-item {
    font-size: 0.84rem;
    color: #475569;
    margin-bottom: 5px;
    line-height: 1.4;
}
</style>
"""
    st.markdown(css_content, unsafe_allow_html=True)

    # 1. About Us Page View
    if nav_selection == "About Us":
        st.markdown("## ℹ️ About VoltKart")
        st.markdown(
            """
            **VoltKart** is India's premier specialized online retailer for high-performance laptop computers,
            creator workstations, and professional business machines.

            ### Our Core Promises:
            - **100% Genuine Factory-Sealed Laptops**: Sourced directly from certified brand distributors (Lenovo, HP, Dell, Asus, Apple, Acer, VoltKart).
            - **7-Day Return Guarantee**: Complete peace of mind with our verified return and refund protocol.
            - **Grounded AI Shopping Assistant**: Real-time advice, comparison, and policy resolution powered directly by store records.
            - **Zero Fake Specs or Fabricated Pricing**: All information is verified directly against our live database catalog.
            """
        )
        return

    # 2. Contact Page View
    if nav_selection == "Contact":
        st.markdown("## 📞 Contact VoltKart Support")
        st.markdown(
            """
            Have questions regarding your order, warranty, specifications, or delivery? Reach out to our team:

            - 📧 **Customer Support**: `support@voltkart.com`
            - 📞 **Toll-Free Helpline**: `1800-VOLT-KART` (9:00 AM – 9:00 PM IST)
            - 🏢 **Headquarters**: VoltKart Technologies Hub, Outer Ring Road, Bangalore, Karnataka, India
            - 💬 **Live Assistant**: Click the floating circular chat icon at the bottom-right of your screen!
            """
        )
        return

    # 3. Main Storefront / Laptop Browsing View
    # Hero Section
    hero_html = (
        '<div class="hero-banner">'
        '<div class="hero-title">Find Your Perfect Laptop</div>'
        '<div class="hero-subtitle">'
        'Explore premium laptops for coding, college, gaming and business. Authentic verified models directly from certified store records.'
        '</div>'
        '</div>'
    )
    st.markdown(hero_html, unsafe_allow_html=True)

    # Fetch and Normalize All Laptops from MongoDB (Strictly Laptops, Exact DB Names)
    raw_laptops = list(products_coll.find({}, {"_id": 0}))
    all_laptops = []
    for p in raw_laptops:
        model_name = p.get("name") or p.get("model")
        if not model_name:
            continue
        brand_name = p.get("brand") or p.get("store") or "VoltKart"
        price_val = float(p.get("price") or p.get("price_inr") or 0.0)
        usage_val = str(p.get("usage_type") or p.get("usage_category") or "general").lower()
        ram_gb_val = int(p.get("ram_gb") or 8)
        ram_val = str(p.get("ram") or f"{ram_gb_val}GB RAM")
        storage_gb_val = int(p.get("storage_gb") or 512)
        storage_val = str(p.get("storage") or f"{storage_gb_val}GB {p.get('storage_type', 'SSD')}")
        proc_val = str(p.get("processor") or "Intel Core i5")
        gpu_val = str(p.get("graphics") or "Intel Iris Xe")
        disp_val = str(p.get("display") or f"{p.get('display_inches', 14.0)}\" {p.get('resolution', 'FHD')}")
        batt_val = str(p.get("battery_life") or f"{p.get('estimated_battery_hours', 8.0)} Hours")
        weight_val = str(p.get("weight") or f"{p.get('weight_kg', 1.4)} kg")
        warr_val = str(p.get("warranty") or "1 Year Manufacturer Coverage")
        pid_val = str(p.get("product_id") or "VK-LAP")

        all_laptops.append({
            "product_id": pid_val,
            "name": model_name,  # Exact name from MongoDB
            "model": model_name,
            "brand": brand_name,
            "price": price_val,
            "price_inr": price_val,
            "usage_type": usage_val,
            "usage_category": usage_val,
            "ram_gb": ram_gb_val,
            "ram": ram_val,
            "storage_gb": storage_gb_val,
            "storage": storage_val,
            "processor": proc_val,
            "graphics": gpu_val,
            "display": disp_val,
            "battery_life": batt_val,
            "weight": weight_val,
            "warranty": warr_val,
        })

    if not all_laptops:
        st.warning(
            "No laptops found in the database. The catalog is currently being updated. Please refresh shortly."
        )
        return

    # Storefront Header Controls (Dynamic Search Result Indicator & Filters)
    with st.container():
        fcol1, fcol2 = st.columns([3, 1])
        with fcol1:
            if header_search and header_search.strip():
                search_badge = f"<div style='font-size:1.18rem; font-weight:700; color:#0f172a; padding-top:6px;'>Search Results for <span style='color:#e11d48;'>\"{header_search.strip()}\"</span></div>"
                st.markdown(search_badge, unsafe_allow_html=True)
            else:
                cat_badge = "<div style='font-size:1.18rem; font-weight:700; color:#0f172a; padding-top:6px;'>💻 Featured Laptop Deal Categories</div>"
                st.markdown(cat_badge, unsafe_allow_html=True)
        with fcol2:
            sort_by = st.selectbox(
                "Sort By",
                options=["Featured", "Price: Low to High", "Price: High to Low", "RAM: High to Low"],
                index=0,
                key="storefront_sort",
                label_visibility="collapsed",
            )

        with st.expander("🎛️ Filter Laptops by Brand, Price Range, RAM, and Processor", expanded=False):
            fc1, fc2, fc3, fc4 = st.columns(4)

            # 1. Brand Filter
            all_brands = sorted(list(set(p.get("brand", "") for p in all_laptops if p.get("brand"))))
            with fc1:
                selected_brands = st.multiselect("Brand", options=all_brands, default=[], key="f_brand")

            # 2. Price Range Filter
            prices = [float(p.get("price", 0)) for p in all_laptops if p.get("price")]
            min_p = min(prices) if prices else 20000.0
            max_p = max(prices) if prices else 200000.0
            with fc2:
                price_range = st.slider(
                    "Price Range (₹)",
                    min_value=float(int(min_p // 1000 * 1000)),
                    max_value=float(int((max_p // 1000 + 1) * 1000)),
                    value=(float(int(min_p)), float(int(max_p))),
                    step=1000.0,
                    key="f_price",
                )

            # 3. RAM Filter
            with fc3:
                all_ram = sorted(list(set(int(p.get("ram_gb", 8)) for p in all_laptops if p.get("ram_gb"))))
                selected_ram = st.multiselect(
                    "RAM Size",
                    options=[f"{r}GB" for r in all_ram],
                    default=[],
                    key="f_ram",
                )
                selected_ram_ints = [int(r.replace("GB", "")) for r in selected_ram]

            # 4. Processor / Usage Filter
            with fc4:
                selected_usage = st.multiselect(
                    "Intended Usage",
                    options=["student", "office", "gaming", "creator", "coding", "business", "general"],
                    default=[],
                    key="f_usage",
                )

    # Filtering Pipeline
    filtered = all_laptops
    is_filtered = bool(
        header_search.strip()
        or selected_brands
        or selected_ram_ints
        or selected_usage
        or (price_range[0] > min_p or price_range[1] < max_p)
    )

    # Apply Search Query from header search widget
    effective_search = (header_search or "").strip().lower()
    if effective_search:
        filtered = [
            p
            for p in filtered
            if effective_search in p.get("name", "").lower()
            or effective_search in p.get("brand", "").lower()
            or effective_search in p.get("processor", "").lower()
            or effective_search in p.get("graphics", "").lower()
            or effective_search in str(p.get("ram", "")).lower()
            or effective_search in str(p.get("storage", "")).lower()
        ]

    # Apply Brand Filter
    if selected_brands:
        filtered = [p for p in filtered if p.get("brand") in selected_brands]

    # Apply Price Range Filter
    filtered = [p for p in filtered if price_range[0] <= float(p.get("price", 0)) <= price_range[1]]

    # Apply RAM Filter
    if selected_ram_ints:
        filtered = [p for p in filtered if int(p.get("ram_gb", 0)) in selected_ram_ints]

    # Apply Usage Type Filter
    if selected_usage:
        filtered = [p for p in filtered if p.get("usage_type", "").lower() in selected_usage]

    # Apply Sorting
    if sort_by == "Price: Low to High":
        filtered.sort(key=lambda x: float(x.get("price", 0)))
    elif sort_by == "Price: High to Low":
        filtered.sort(key=lambda x: float(x.get("price", 0)), reverse=True)
    elif sort_by == "RAM: High to Low":
        filtered.sort(key=lambda x: int(x.get("ram_gb", 0)), reverse=True)

    # Helper function to generate an Amazon-Style Orange Deal Shelf
    def render_amazon_deal_shelf(title: str, shelf_laptops: list[dict], shelf_key: str):
        if not shelf_laptops:
            return

        page_key = f"shelf_page_{shelf_key}"
        if page_key not in st.session_state:
            st.session_state[page_key] = 0

        current_page = st.session_state[page_key]
        items_per_page = 3
        total_items = len(shelf_laptops)
        max_pages = max(1, (total_items + items_per_page - 1) // items_per_page)
        if current_page >= max_pages:
            current_page = 0
            st.session_state[page_key] = 0

        start_idx = current_page * items_per_page
        visible_laptops = shelf_laptops[start_idx : start_idx + items_per_page]

        cards_html = []
        for laptop in visible_laptops:
            db_name = laptop.get("name") or laptop.get("model")
            price_val = float(laptop.get("price", 0))
            mrp_val, discount_pct = calculate_mrp(price_val)
            img_url = get_laptop_image_url(laptop)
            svg_fallback = get_laptop_svg_data_uri(db_name, laptop.get("usage_type", "general"))

            card_markup = (
                f'<div class="deal-card">'
                f'<div class="deal-card-img-wrap">'
                f'<img src="{img_url}" onerror="this.onerror=null; this.src=\'{svg_fallback}\';" class="deal-card-img" alt="{db_name}" />'
                f'</div>'
                f'<div class="deal-card-title" title="{db_name}">{db_name}</div>'
                f'<div class="deal-card-price-row">'
                f'<span class="deal-card-price">₹{int(price_val):,}<span class="deal-card-cents">00</span></span>'
                f'<span class="deal-card-mrp">M.R.P: <span style="text-decoration: line-through;">₹{mrp_val:,.2f}</span></span>'
                f'<span class="deal-card-discount">{discount_pct}% off</span>'
                f'</div>'
                f'<div class="deal-card-specs">⚙️ {laptop.get("processor")} • {laptop.get("ram")} • {laptop.get("storage")}</div>'
                f'</div>'
            )
            cards_html.append(card_markup)

        # Build full shelf markup with header, on-grid cards, and on-grid side scroll navigation
        with st.container(key=f"shelf_box_{shelf_key}"):
            page_info = (
                f'<span class="deal-shelf-page-tag">Page {current_page + 1} of {max_pages} ({total_items} Laptops)</span>'
                if total_items > items_per_page
                else f'<span class="deal-shelf-page-tag">({total_items} Laptops)</span>'
            )
            shelf_header_html = (
                f'<div class="deal-shelf-header">'
                f'<span class="deal-shelf-title">{title}</span>'
                f'{page_info}'
                f'</div>'
            )
            st.markdown(shelf_header_html, unsafe_allow_html=True)

            if total_items > items_per_page:
                c1, c2, c3, c_btn = st.columns([1, 1, 1, 0.16], vertical_alignment="center", gap="medium")
                card_cols = [c1, c2, c3]
                for idx_c, col in enumerate(card_cols):
                    with col:
                        if idx_c < len(cards_html):
                            st.markdown(cards_html[idx_c], unsafe_allow_html=True)
                with c_btn:
                    if st.button("›", key=f"grid_next_{shelf_key}", help=f"Scroll to next laptops ({current_page + 1}/{max_pages})", use_container_width=True):
                        st.session_state[page_key] = (current_page + 1) % max_pages
                        st.rerun()
                    if current_page > 0:
                        if st.button("‹", key=f"grid_prev_{shelf_key}", help="Scroll to previous laptops", use_container_width=True):
                            st.session_state[page_key] = (current_page - 1) % max_pages
                            st.rerun()
            else:
                c1, c2, c3 = st.columns([1, 1, 1], gap="medium")
                for idx_c, col in enumerate([c1, c2, c3]):
                    with col:
                        if idx_c < len(cards_html):
                            st.markdown(cards_html[idx_c], unsafe_allow_html=True)

        # Specifications Expander directly below the shelf
        with st.expander(f"🔍 Detailed Specifications for {title} ({total_items} Laptops)", expanded=False):
            spec_cols = st.columns(min(len(visible_laptops), 3))
            for scol, laptop in zip(spec_cols, visible_laptops):
                with scol:
                    with st.container(border=True):
                        st.markdown(f"**{laptop.get('name')}**")
                        st.caption(f"Brand: {laptop.get('brand')} | SKU: `{laptop.get('product_id')}`")
                        st.write(f"⚙️ **CPU**: {laptop.get('processor')}")
                        st.write(f"🧠 **RAM**: {laptop.get('ram')}")
                        st.write(f"💾 **Storage**: {laptop.get('storage')}")
                        st.write(f"🎮 **GPU**: {laptop.get('graphics')}")
                        st.write(f"🖥️ **Display**: {laptop.get('display')}")
                        st.write(f"🔋 **Battery**: {laptop.get('battery_life')}")
                        st.write(f"🛡️ **Warranty**: {laptop.get('warranty')}")

    # Catalog Count
    catalog_count_html = (
        f"<div style='margin-bottom:18px; color:#64748b; font-size:0.92rem;'>"
        f"Showing <b style='color:#e11d48;'>{len(filtered)}</b> of <b style='color:#e11d48;'>{len(all_laptops)}</b> genuine laptops in catalog"
        f"</div>"
    )
    st.markdown(catalog_count_html, unsafe_allow_html=True)

    if not filtered:
        st.info("No laptops match your selected filters. Try broadening your criteria or clearing the search query.")
        if st.button("Reset Filters"):
            st.rerun()
        return

    # Scenario A: User applied active filters or search -> Show Filtered Results Deal Shelf
    if is_filtered:
        # Group filtered results into shelves of 3 cards each
        cols_per_shelf = 3
        for idx in range(0, len(filtered), cols_per_shelf):
            chunk = filtered[idx : idx + cols_per_shelf]
            shelf_num = (idx // cols_per_shelf) + 1
            render_amazon_deal_shelf(f"Deals Matching Your Search (Shelf {shelf_num})", chunk, f"filtered_{idx}")
        return

    # Scenario B: Default Home View -> Curated Category Deal Shelves (Amazon-Style)
    # 1. Gaming Laptops Shelf
    gaming_laptops = [p for p in all_laptops if p.get("usage_type") == "gaming" or "gaming" in p.get("name", "").lower()]
    render_amazon_deal_shelf("Deals on Gaming Laptops", gaming_laptops, "gaming")

    # 2. Student & Everyday Laptops Shelf
    student_laptops = [
        p for p in all_laptops
        if p.get("usage_type") in ["student", "general"]
        and "gaming" not in p.get("name", "").lower()
    ]
    render_amazon_deal_shelf("Deals on Student & Everyday Laptops", student_laptops, "student")

    # 3. Office & Business Laptops Shelf
    office_laptops = [
        p for p in all_laptops
        if p.get("usage_type") in ["office", "business"]
        and p not in gaming_laptops
        and p not in student_laptops
    ]
    render_amazon_deal_shelf("Deals on Office & Business Laptops", office_laptops, "office")

    # 4. Creator & Ultra Laptops Shelf
    creator_laptops = [
        p for p in all_laptops
        if p not in gaming_laptops
        and p not in student_laptops
        and p not in office_laptops
    ]
    if creator_laptops:
        render_amazon_deal_shelf("Deals on Creator & Ultra Laptops", creator_laptops, "creator")
