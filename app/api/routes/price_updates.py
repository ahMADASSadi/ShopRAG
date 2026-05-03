from typing import List, Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from loguru import logger

from app.api.deps import get_price_update_service, get_search_service, get_product_service
from app.services.price_update_service import PriceUpdateService
from app.services.product_service import ProductService
from app.services.search_service import SearchService

router = APIRouter(prefix="/price-updates", tags=["price-updates"])


class SimilarProductResponse(BaseModel):
    product_id: int
    source_name: str
    source_url: str
    price: Decimal
    similarity_score: float
    title: str
    currency: str


class PriceUpdateResponse(BaseModel):
    product_id: int
    old_price: Optional[Decimal]
    new_price: Optional[Decimal]
    updated: bool
    message: str


class BulkUpdateResponse(BaseModel):
    updated: int
    skipped: int
    failed: int
    message: str = ""


@router.post("/{product_id}/search", response_model=List[SimilarProductResponse])
def search_similar_products(
    product_id: int,
    search_svc: SearchService = Depends(get_search_service),
):
    logger.info(f"POST /price-updates/{product_id}/search")
    similar = search_svc.search_and_store_similar(product_id)
    if not similar:
        raise HTTPException(status_code=404, detail="No similar products found or product not found")
    return [
        SimilarProductResponse(
            product_id=sp.product_id,
            source_name=sp.source_name,
            source_url=sp.source_url,
            price=sp.price,
            similarity_score=sp.similarity_score,
            title=sp.title,
            currency=sp.currency,
        )
        for sp in similar
    ]


@router.get("/{product_id}/similar", response_model=List[SimilarProductResponse])
def get_similar_products(
    product_id: int,
    search_svc: SearchService = Depends(get_search_service),
):
    logger.info(f"GET /price-updates/{product_id}/similar")
    similar = search_svc.get_similar_products(product_id)
    return [
        SimilarProductResponse(
            product_id=sp.product_id,
            source_name=sp.source_name,
            source_url=sp.source_url,
            price=sp.price,
            similarity_score=sp.similarity_score,
            title=sp.title,
            currency=sp.currency,
        )
        for sp in similar
    ]


@router.post("/{product_id}/update", response_model=PriceUpdateResponse)
def update_product_price(
    product_id: int,
    force_search: bool = True,
    product_svc: ProductService = Depends(get_product_service),
    price_svc: PriceUpdateService = Depends(get_price_update_service),
):
    logger.info(f"POST /price-updates/{product_id}/update force_search={force_search}")
    existing = product_svc.get_product(product_id)
    old_price = existing.price if existing else None
    updated = price_svc.update_product_price(product_id, force_search=force_search)
    if updated is None:
        return PriceUpdateResponse(
            product_id=product_id,
            old_price=old_price,
            new_price=None,
            updated=False,
            message="No price update was necessary or product not found",
        )
    return PriceUpdateResponse(
        product_id=product_id,
        old_price=old_price,
        new_price=updated.price,
        updated=True,
        message=f"Price updated to {updated.price}",
    )


@router.post("/bulk-update", status_code=202)
def bulk_update_prices(
    background_tasks: BackgroundTasks,
    force_search: bool = False,
    price_svc: PriceUpdateService = Depends(get_price_update_service),
):
    logger.info(f"POST /price-updates/bulk-update force_search={force_search}")
    background_tasks.add_task(price_svc.bulk_update_prices, force_search=force_search)
    return {"message": "Bulk price update started in the background"}
