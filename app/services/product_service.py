from decimal import Decimal
from typing import List, Optional

from loguru import logger

from app.core.domain.product import Product
from app.core.ports.product_repository import ProductRepositoryPort


class ProductService:
    def __init__(self, product_repo: ProductRepositoryPort) -> None:
        self._repo = product_repo

    def get_product(self, product_id: int) -> Optional[Product]:
        logger.info(f"ProductService: get_product id={product_id}")
        return self._repo.get_by_id(product_id)

    def list_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        logger.info(f"ProductService: list_products skip={skip} limit={limit}")
        return self._repo.get_all(skip=skip, limit=limit)

    def create_product(self, product: Product) -> Product:
        logger.info(f"ProductService: create_product sku={product.sku}")
        return self._repo.create(product)

    def update_price(self, product_id: int, new_price: Decimal) -> Optional[Product]:
        logger.info(f"ProductService: update_price id={product_id} price={new_price}")
        return self._repo.update_price(product_id, new_price)

    def delete_product(self, product_id: int) -> bool:
        logger.info(f"ProductService: delete_product id={product_id}")
        return self._repo.delete(product_id)
