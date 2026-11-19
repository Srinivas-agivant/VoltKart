"""Tests for storefront product filtering and dynamic search pipeline."""

import pytest


@pytest.fixture
def sample_catalog():
    return [
        {
            "product_id": "VK001",
            "name": "ThinkPad E14",
            "brand": "Lenovo",
            "price": 58999.0,
            "processor": "Intel Core i5-1335U",
            "ram_gb": 16,
            "ram": "16GB",
            "storage": "512GB SSD",
            "usage_type": "coding",
        },
        {
            "product_id": "VK002",
            "name": "Pavilion Gaming 15",
            "brand": "HP",
            "price": 64999.0,
            "processor": "AMD Ryzen 5 7535HS",
            "ram_gb": 8,
            "ram": "8GB",
            "storage": "512GB SSD",
            "usage_type": "gaming",
        },
        {
            "product_id": "VK003",
            "name": "MacBook Air M2",
            "brand": "Apple",
            "price": 99999.0,
            "processor": "Apple M2",
            "ram_gb": 16,
            "ram": "16GB",
            "storage": "512GB SSD",
            "usage_type": "business",
        },
    ]


def test_search_by_model_name(sample_catalog):
    query = "thinkpad"
    filtered = [
        p
        for p in sample_catalog
        if query in p["name"].lower()
        or query in p["brand"].lower()
        or query in p["processor"].lower()
    ]
    assert len(filtered) == 1
    assert filtered[0]["name"] == "ThinkPad E14"


def test_filter_by_brand_and_ram(sample_catalog):
    filtered = [p for p in sample_catalog if p["brand"] == "Apple" and p["ram_gb"] == 16]
    assert len(filtered) == 1
    assert filtered[0]["brand"] == "Apple"


def test_filter_by_price_range(sample_catalog):
    filtered = [p for p in sample_catalog if 50000.0 <= p["price"] <= 70000.0]
    assert len(filtered) == 2
    names = [p["name"] for p in filtered]
    assert "ThinkPad E14" in names
    assert "Pavilion Gaming 15" in names


def test_deal_card_mrp_and_exact_db_name(sample_catalog):
    from frontend.laptop_images import calculate_mrp, get_laptop_image_url, get_laptop_svg_data_uri

    for laptop in sample_catalog:
        db_name = laptop.get("name")
        price = laptop.get("price")
        mrp, discount = calculate_mrp(price)

        # M.R.P. must strictly exceed selling price
        assert mrp > price
        assert discount >= 12

        # Exact database name is preserved
        assert db_name in ["ThinkPad E14", "Pavilion Gaming 15", "MacBook Air M2"]

        # Valid photo URL and offline SVG data URI generated
        img_url = get_laptop_image_url(laptop)
        assert img_url.startswith("https://")

        svg_data = get_laptop_svg_data_uri(db_name, laptop.get("usage_type"))
        assert svg_data.startswith("data:image/svg+xml;utf8,")
        assert db_name in svg_data or "".join(c for c in db_name if c.isalnum()) in svg_data

