from typing import List

from loguru import logger

from app.config import get_settings
from app.core.domain.similar_product import SimilarProduct
from app.core.ports.embedder import EmbedderPort
from app.core.ports.product_repository import ProductRepositoryPort
from app.core.ports.vector_repository import VectorRepositoryPort
from app.core.ports.web_searcher import WebSearcherPort

settings = get_settings()


class SearchService:
    def __init__(
        self,
        product_repo: ProductRepositoryPort,
        vector_repo: VectorRepositoryPort,
        web_searcher: WebSearcherPort,
        embedder: EmbedderPort,
    ) -> None:
        self._product_repo = product_repo
        self._vector_repo = vector_repo
        self._web_searcher = web_searcher
        self._embedder = embedder

    def _embed(self, text: str) -> List[float]:
        return self._embedder.embed(text)

    def search_and_store_similar(self, product_id: int) -> List[SimilarProduct]:
        product = self._product_repo.get_by_id(product_id)
        if product is None:
            logger.warning(f"SearchService: product_id={product_id} not found")
            return []

        logger.info(f"SearchService: starting search for product '{product.name}' (id={product_id})")
        similar_products = self._web_searcher.search_similar_products(
            product_name=product.name,
            product_id=product_id,
            max_results=settings.MAX_SEARCH_RESULTS,
        )

        if not similar_products:
            logger.warning(f"SearchService: no similar products found for product_id={product_id}")
            return []

        embedding = self._embed(f"{product.name} {product.description}")
        self._vector_repo.upsert(
            product_id=product_id,
            similar_products=similar_products,
            embedding=embedding,
        )
        logger.success(f"SearchService: stored {len(similar_products)} similar products for product_id={product_id}")
        return similar_products

    def get_similar_products(self, product_id: int) -> List[SimilarProduct]:
        logger.info(f"SearchService: get_similar_products product_id={product_id}")
        return self._vector_repo.get_by_product_id(product_id)
