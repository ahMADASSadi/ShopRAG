from abc import ABC, abstractmethod
from typing import List
from app.core.domain.similar_product import SimilarProduct


class VectorRepositoryPort(ABC):
    @abstractmethod
    def upsert(self, product_id: int, similar_products: List[SimilarProduct], embedding: List[float]) -> None:
        ...

    @abstractmethod
    def search_similar(self, embedding: List[float], limit: int = 5) -> List[dict]:
        ...

    @abstractmethod
    def get_by_product_id(self, product_id: int) -> List[SimilarProduct]:
        ...
