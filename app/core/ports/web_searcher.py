from abc import ABC, abstractmethod
from typing import List
from app.core.domain.similar_product import SimilarProduct


class WebSearcherPort(ABC):
    @abstractmethod
    def search_similar_products(self, product_name: str, product_id: int, max_results: int = 5) -> List[SimilarProduct]:
        ...
