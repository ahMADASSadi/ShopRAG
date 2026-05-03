from functools import lru_cache

from sqlalchemy.orm import Session
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from fastapi import Depends

from app.adapters.db.session import get_db
from app.adapters.db.product_repo import SQLAlchemyProductRepository
from app.adapters.vector_store.qdrant_repo import QdrantVectorRepository
from app.adapters.web_search.duckduckgo_searcher import DuckDuckGoSearcher
from app.services.product_service import ProductService
from app.services.search_service import SearchService
from app.services.price_update_service import PriceUpdateService
from app.config import get_settings

settings = get_settings()


@lru_cache()
def get_qdrant_client() -> QdrantClient:
    return QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)


@lru_cache()
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(settings.EMBEDDING_MODEL)


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    repo = SQLAlchemyProductRepository(db)
    return ProductService(repo)


def get_search_service(db: Session = Depends(get_db)) -> SearchService:
    product_repo = SQLAlchemyProductRepository(db)
    vector_repo = QdrantVectorRepository(get_qdrant_client())
    web_searcher = DuckDuckGoSearcher()
    embedding_model = get_embedding_model()
    return SearchService(product_repo, vector_repo, web_searcher, embedding_model)


def get_price_update_service(db: Session = Depends(get_db)) -> PriceUpdateService:
    product_repo = SQLAlchemyProductRepository(db)
    search_svc = get_search_service(db)
    return PriceUpdateService(product_repo, search_svc)
