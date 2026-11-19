"""Image and pricing utilities for VoltKart laptop catalog."""

import urllib.parse
from typing import Any, Optional


# Curated high-resolution laptop photography URLs (white/clean background)
BRAND_IMAGE_MAP = {
    "apple": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500&auto=format&fit=crop&q=80",
    "lenovo": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=500&auto=format&fit=crop&q=80",
    "dell": "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=500&auto=format&fit=crop&q=80",
    "hp": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=500&auto=format&fit=crop&q=80",
    "asus": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500&auto=format&fit=crop&q=80",
    "gaming": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=500&auto=format&fit=crop&q=80",
    "student": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500&auto=format&fit=crop&q=80",
    "creator": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500&auto=format&fit=crop&q=80",
    "office": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=500&auto=format&fit=crop&q=80",
    "default": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500&auto=format&fit=crop&q=80",
}


def get_laptop_svg_data_uri(model_name: str, category: str = "general") -> str:
    """Generates a self-contained, crisp vector SVG laptop illustration as a data URI.

    Ensures zero broken images even offline or in air-gapped environments.
    """
    clean_cat = str(category).lower().strip()
    theme_colors = {
        "gaming": ("#090d16", "#22c55e", "#ef4444", "#1e293b", "#22c55e"),
        "student": ("#f8fafc", "#0284c7", "#38bdf8", "#cbd5e1", "#0284c7"),
        "office": ("#1e293b", "#475569", "#94a3b8", "#334155", "#38bdf8"),
        "creator": ("#090d16", "#8b5cf6", "#ec4899", "#1e293b", "#d946ef"),
    }
    top_color, grad1, grad2, base_color, accent = theme_colors.get(clean_cat, theme_colors["student"])
    safe_id = "".join(c for c in model_name if c.isalnum()) or "laptop"

    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 260 175' width='100%' height='100%'>
      <defs>
        <linearGradient id='grad_{safe_id}' x1='0%' y1='0%' x2='100%' y2='100%'>
          <stop offset='0%' stop-color='{grad1}'/>
          <stop offset='100%' stop-color='{grad2}'/>
        </linearGradient>
      </defs>
      <!-- Laptop Screen Lid -->
      <rect x='28' y='12' width='204' height='124' rx='9' fill='#1e293b' stroke='#334155' stroke-width='2'/>
      <!-- Inner Bezel -->
      <rect x='34' y='18' width='192' height='112' rx='5' fill='#020617'/>
      <!-- Display Screen Wallpaper -->
      <rect x='37' y='21' width='186' height='106' rx='3' fill='url(#grad_{safe_id})' opacity='0.9'/>
      <!-- Webcam Dot -->
      <circle cx='130' cy='15' r='1.5' fill='#94a3b8'/>
      <!-- Model Text Watermark -->
      <text x='130' y='76' font-family='system-ui, -apple-system, sans-serif' font-size='13' font-weight='700' fill='#ffffff' text-anchor='middle' opacity='0.92'>{model_name}</text>
      <!-- Keyboard Base in Perspective -->
      <polygon points='8,139 252,139 236,158 24,158' fill='{base_color}' stroke='#64748b' stroke-width='1.2'/>
      <!-- Trackpad -->
      <rect x='112' y='142' width='36' height='11' rx='2' fill='#94a3b8' opacity='0.5'/>
      <!-- Power / Lip Indicator -->
      <line x1='118' y1='158' x2='142' y2='158' stroke='{accent}' stroke-width='2.2'/>
    </svg>"""
    return "data:image/svg+xml;utf8," + urllib.parse.quote(svg)


def get_laptop_image_url(laptop: dict[str, Any]) -> str:
    """Returns the most appropriate photography URL for the given laptop."""
    brand = str(laptop.get("brand", "") or laptop.get("store", "")).lower()
    usage = str(laptop.get("usage_type", "") or laptop.get("usage_category", "")).lower()
    name = str(laptop.get("name", "") or laptop.get("model", "")).lower()

    if "gaming" in usage or "gaming" in name:
        return BRAND_IMAGE_MAP["gaming"]
    if "macbook" in name or "apple" in brand:
        return BRAND_IMAGE_MAP["apple"]
    if "lenovo" in brand or "thinkpad" in name or "ideapad" in name:
        return BRAND_IMAGE_MAP["lenovo"]
    if "dell" in brand:
        return BRAND_IMAGE_MAP["dell"]
    if "hp" in brand:
        return BRAND_IMAGE_MAP["hp"]
    if "asus" in brand:
        return BRAND_IMAGE_MAP["asus"]
    if "creator" in usage or "creator" in name or "design" in name:
        return BRAND_IMAGE_MAP["creator"]
    if "student" in usage or "study" in name or "aerobook" in name:
        return BRAND_IMAGE_MAP["student"]
    if "office" in usage or "work" in name or "biz" in name:
        return BRAND_IMAGE_MAP["office"]

    return BRAND_IMAGE_MAP["default"]


def calculate_mrp(price: float) -> tuple[float, int]:
    """Calculates a realistic retail M.R.P. and discount percentage for e-commerce deal cards."""
    # Approximate 18% to 28% discount benchmark
    mrp = round(price * 1.25, -2) - 1.0
    discount = int(round((1 - (price / mrp)) * 100)) if mrp > price else 0
    return mrp, max(discount, 12)
