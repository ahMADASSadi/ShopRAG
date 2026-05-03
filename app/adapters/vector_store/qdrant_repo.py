from typing import List
from decimal import Decimal

from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)

from app.config import get_settings
from app.core.domain.similar_product import SimilarProduct
from app.core.ports.vector_repository import VectorRepositoryPort

settings = get_settings()


class QdrantVectorRepository(VectorRepositoryPort):
    def __init__(self, client: QdrantClient) -> None:
        self._client = client
        self._collection = settings.QDRANT_COLLECTION
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        collections = [c.name for c in self._client.get_collections().collections]
        if self._collection not in collections:
            logger.info(f"Creating Qdrant collection: {self._collection}")
            self._client.create_collection(
                collection_name=self._collection,
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_DIM,
                    distance=Distance.COSINE,
                ),
            )
            logger.success(f"Qdrant collection '{self._collection}' created")

    def upsert(self, product_id: int, similar_products: List[SimilarProduct], embedding: List[float]) -> None:
        logger.info(f"Upserting {len(similar_products)} similar products for product_id={product_id}")
        points = []
        for idx, sp in enumerate(similar_products):
            point_id = product_id * 10000 + idx
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "product_id": product_id,
                        "source_name": sp.source_name,
                        "source_url": sp.source_url,
                        "price": float(sp.price),
                        "title": sp.title,
                        "currency": sp.currency,
                        "similarity_score": sp.similarity_score,
                    },
                )
            )
        if points:
            self._client.upsert(collection_name=self._collection, points=points)
            logger.success(f"Upserted {len(points)} points for product_id={product_id}")

    def search_similar(self, embedding: List[float], limit: int = 5) -> List[dict]:
        logger.debug(f"Searching for similar vectors limit={limit}")
        results = self._client.search(
            collection_name=self._collection,
            query_vector=embedding,
            limit=limit,
        )
        return [
            {**r.payload, "score": r.score}
            for r in results
        ]

    def get_by_product_id(self, product_id: int) -> List[SimilarProduct]:
        logger.debug(f"Getting similar products for product_id={product_id}")
        results = self._client.scroll(
            collection_name=self._collection,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="product_id",
                        match=MatchValue(value=product_id),
                    )
                ]
            ),
            limit=100,
        )
        similar = []
        for point in results[0]:
            p = point.payload
            similar.append(
                SimilarProduct(
                    product_id=p["product_id"],
                    source_name=p["source_name"],
                    source_url=p["source_url"],
                    price=Decimal(str(p["price"])),
                    similarity_score=p["similarity_score"],
                    title=p["title"],
                    currency=p.get("currency", "USD"),
                )
            )
        return similar
