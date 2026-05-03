from decimal import Decimal
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.core.domain.product import Product
from app.core.domain.similar_product import SimilarProduct
from app.services.price_update_service import PriceUpdateService


def make_product(price: str = "30.00") -> Product:
    return Product(
        id=1,
        name="Test Product",
        description="A test product",
        price=Decimal(price),
        category="Electronics",
        sku="SKU-001",
        stock=10,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def make_similar(price: str) -> SimilarProduct:
    return SimilarProduct(
        product_id=1,
        source_name="TestShop",
        source_url="https://testshop.com/product",
        price=Decimal(price),
        similarity_score=0.9,
        title="Similar Product",
        currency="USD",
    )


def test_update_price_within_margin():
    repo = MagicMock()
    search_svc = MagicMock()
    product = make_product("30.00")
    repo.get_by_id.return_value = product
    search_svc.search_and_store_similar.return_value = [
        make_similar("29.00"),
        make_similar("31.00"),
    ]
    service = PriceUpdateService(repo, search_svc)
    result = service.update_product_price(1, force_search=True)
    # Avg is 30.00 - within 5% margin of current 30.00
    repo.update_price.assert_not_called()


def test_update_price_outside_margin():
    repo = MagicMock()
    search_svc = MagicMock()
    product = make_product("50.00")
    updated = make_product("28.00")
    repo.get_by_id.return_value = product
    repo.update_price.return_value = updated
    search_svc.search_and_store_similar.return_value = [
        make_similar("25.00"),
        make_similar("30.00"),
        make_similar("29.00"),
    ]
    service = PriceUpdateService(repo, search_svc)
    result = service.update_product_price(1, force_search=True)
    repo.update_price.assert_called_once()


def test_update_price_no_similar_products():
    repo = MagicMock()
    search_svc = MagicMock()
    search_svc.search_and_store_similar.return_value = []
    service = PriceUpdateService(repo, search_svc)
    result = service.update_product_price(1, force_search=True)
    assert result is None
    repo.update_price.assert_not_called()


def test_bulk_update():
    repo = MagicMock()
    search_svc = MagicMock()
    product1 = make_product("50.00")
    product2 = make_product("50.00")
    product2.id = 2
    product2.sku = "SKU-002"
    products = [product1, product2]
    repo.get_all.return_value = products
    repo.get_by_id.side_effect = lambda pid: product1 if pid == 1 else product2
    search_svc.search_and_store_similar.return_value = []  # no updates needed
    service = PriceUpdateService(repo, search_svc)
    results = service.bulk_update_prices()
    assert "updated" in results
    assert "skipped" in results
    assert "failed" in results
