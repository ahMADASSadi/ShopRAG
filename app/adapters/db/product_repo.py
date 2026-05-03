from decimal import Decimal
from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import Session
from loguru import logger

from app.core.domain.product import Product
from app.core.ports.product_repository import ProductRepositoryPort
from app.adapters.db.models import ProductModel, PriceUpdateModel


class SQLAlchemyProductRepository(ProductRepositoryPort):
    def __init__(self, db: Session) -> None:
        self._db = db

    def _to_domain(self, model: ProductModel) -> Product:
        return Product(
            id=model.id,
            name=model.name,
            description=model.description or "",
            price=Decimal(str(model.price)),
            category=model.category,
            sku=model.sku,
            stock=model.stock,
            created_at=model.created_at,
            updated_at=model.updated_at,
            image_url=model.image_url,
        )

    def get_by_id(self, product_id: int) -> Optional[Product]:
        logger.debug(f"Fetching product with id={product_id}")
        model = self._db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if model is None:
            logger.warning(f"Product id={product_id} not found")
            return None
        return self._to_domain(model)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        logger.debug(f"Fetching all products skip={skip} limit={limit}")
        models = self._db.query(ProductModel).offset(skip).limit(limit).all()
        return [self._to_domain(m) for m in models]

    def create(self, product: Product) -> Product:
        logger.info(f"Creating product sku={product.sku}")
        model = ProductModel(
            name=product.name,
            description=product.description,
            price=product.price,
            category=product.category,
            sku=product.sku,
            stock=product.stock,
            image_url=product.image_url,
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        logger.success(f"Product created id={model.id} sku={model.sku}")
        return self._to_domain(model)

    def update_price(self, product_id: int, new_price: Decimal) -> Optional[Product]:
        logger.info(f"Updating price for product id={product_id} new_price={new_price}")
        model = self._db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if model is None:
            logger.warning(f"Product id={product_id} not found for price update")
            return None
        old_price = model.price
        model.price = new_price
        model.updated_at = datetime.utcnow()

        price_update = PriceUpdateModel(
            product_id=product_id,
            old_price=old_price,
            new_price=new_price,
            reason="Automatic price update from RAG search",
        )
        self._db.add(price_update)
        self._db.commit()
        self._db.refresh(model)
        logger.success(f"Price updated product id={product_id} old={old_price} new={new_price}")
        return self._to_domain(model)

    def delete(self, product_id: int) -> bool:
        logger.info(f"Deleting product id={product_id}")
        model = self._db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if model is None:
            logger.warning(f"Product id={product_id} not found for deletion")
            return False
        self._db.delete(model)
        self._db.commit()
        logger.success(f"Product id={product_id} deleted")
        return True
