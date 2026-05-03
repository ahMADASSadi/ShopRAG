from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List, Optional
from app.core.domain.product import Product


class ProductRepositoryPort(ABC):
    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        ...

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        ...

    @abstractmethod
    def create(self, product: Product) -> Product:
        ...

    @abstractmethod
    def update_price(self, product_id: int, new_price: Decimal) -> Optional[Product]:
        ...

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        ...
