from typing import List, Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from loguru import logger

from app.api.deps import get_price_update_service, get_search_service
from app.services.price_update_service import PriceUpdateService
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
    price_svc: PriceUpdateService = Depends(get_price_update_service),
):
    logger.info(f"POST /price-updates/{product_id}/update force_search={force_search}")
    updated = price_svc.update_product_price(product_id, force_search=force_search)
    if updated is None:
        return PriceUpdateResponse(
            product_id=product_id,
            old_price=None,
            new_price=None,
            updated=False,
            message="No price update was necessary or product not found",
        )
    return PriceUpdateResponse(
        product_id=product_id,
        old_price=None,
        new_price=updated.price,
        updated=True,
        message=f"Price updated to {updated.price}",
    )


@router.post("/bulk-update", response_model=BulkUpdateResponse)
def bulk_update_prices(
    background_tasks: BackgroundTasks,
    price_svc: PriceUpdateService = Depends(get_price_update_service),
):
    logger.info("POST /price-updates/bulk-update")
    results = price_svc.bulk_update_prices()
    return BulkUpdateResponse(**results)
