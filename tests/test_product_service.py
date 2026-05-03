from decimal import Decimal
from unittest.mock import MagicMock
from datetime import datetime

import pytest

from app.core.domain.product import Product
from app.services.product_service import ProductService


def make_product(product_id: int = 1) -> Product:
    return Product(
        id=product_id,
        name="Test Product",
        description="A test product",
        price=Decimal("29.99"),
        category="Electronics",
        sku=f"SKU-{product_id:03d}",
        stock=10,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


def test_get_product_found():
    repo = MagicMock()
    product = make_product(1)
    repo.get_by_id.return_value = product
    service = ProductService(repo)
    result = service.get_product(1)
    assert result == product
    repo.get_by_id.assert_called_once_with(1)


def test_get_product_not_found():
    repo = MagicMock()
    repo.get_by_id.return_value = None
    service = ProductService(repo)
    result = service.get_product(999)
    assert result is None


def test_list_products():
    repo = MagicMock()
    products = [make_product(i) for i in range(1, 4)]
    repo.get_all.return_value = products
    service = ProductService(repo)
    result = service.list_products(skip=0, limit=10)
    assert len(result) == 3
    repo.get_all.assert_called_once_with(skip=0, limit=10)


def test_create_product():
    repo = MagicMock()
    product = make_product(1)
    repo.create.return_value = product
    service = ProductService(repo)
    result = service.create_product(product)
    assert result == product
    repo.create.assert_called_once_with(product)


def test_update_price():
    repo = MagicMock()
    product = make_product(1)
    updated = Product(**{**product.__dict__, "price": Decimal("24.99")})
    repo.update_price.return_value = updated
    service = ProductService(repo)
    result = service.update_price(1, Decimal("24.99"))
    assert result.price == Decimal("24.99")
    repo.update_price.assert_called_once_with(1, Decimal("24.99"))


def test_delete_product():
    repo = MagicMock()
    repo.delete.return_value = True
    service = ProductService(repo)
    result = service.delete_product(1)
    assert result is True


def test_delete_product_not_found():
    repo = MagicMock()
    repo.delete.return_value = False
    service = ProductService(repo)
    result = service.delete_product(999)
    assert result is False
