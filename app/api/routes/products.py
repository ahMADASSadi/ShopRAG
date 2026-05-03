from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from loguru import logger

from app.api.deps import get_product_service
from app.core.domain.product import Product
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=100)
    sku: str = Field(..., min_length=1, max_length=100)
    stock: int = Field(default=0, ge=0)
    image_url: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: Decimal
    category: str
    sku: str
    stock: int
    image_url: Optional[str]

    class Config:
        from_attributes = True


@router.get("/", response_model=List[ProductResponse])
def list_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    service: ProductService = Depends(get_product_service),
):
    logger.info(f"GET /products skip={skip} limit={limit}")
    products = service.list_products(skip=skip, limit=limit)
    return [ProductResponse(**p.__dict__) for p in products]


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    service: ProductService = Depends(get_product_service),
):
    logger.info(f"GET /products/{product_id}")
    product = service.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse(**product.__dict__)


@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(
    data: ProductCreate,
    service: ProductService = Depends(get_product_service),
):
    logger.info(f"POST /products name={data.name} sku={data.sku}")
    product = Product(
        id=0,
        name=data.name,
        description=data.description or "",
        price=data.price,
        category=data.category,
        sku=data.sku,
        stock=data.stock,
        image_url=data.image_url,
    )
    created = service.create_product(product)
    return ProductResponse(**created.__dict__)


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    service: ProductService = Depends(get_product_service),
):
    logger.info(f"DELETE /products/{product_id}")
    deleted = service.delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
