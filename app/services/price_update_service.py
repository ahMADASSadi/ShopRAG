from decimal import Decimal
from typing import List, Optional

from loguru import logger

from app.config import get_settings
from app.core.domain.product import Product
from app.core.domain.similar_product import SimilarProduct
from app.core.ports.product_repository import ProductRepositoryPort
from app.services.search_service import SearchService

settings = get_settings()


class PriceUpdateService:
    def __init__(
        self,
        product_repo: ProductRepositoryPort,
        search_service: SearchService,
    ) -> None:
        self._product_repo = product_repo
        self._search_service = search_service

    def _calculate_suggested_price(
        self,
        current_price: Decimal,
        similar_products: List[SimilarProduct],
    ) -> Optional[Decimal]:
        valid_prices = [
            sp.price
            for sp in similar_products
            if sp.price and sp.price > Decimal("0")
        ]
        if not valid_prices:
            logger.warning("No valid prices found in similar products")
            return None

        avg_price = sum(valid_prices) / len(valid_prices)
        margin = Decimal(str(settings.PRICE_UPDATE_MARGIN))
        lower = avg_price * (Decimal("1") - margin)
        upper = avg_price * (Decimal("1") + margin)

        if lower <= current_price <= upper:
            logger.info(f"Current price {current_price} is within acceptable range [{lower:.2f}, {upper:.2f}]")
            return None

        suggested = avg_price.quantize(Decimal("0.01"))
        logger.info(
            f"Suggested price update: current={current_price} avg_market={avg_price:.2f} "
            f"suggested={suggested}"
        )
        return suggested

    def update_product_price(self, product_id: int, force_search: bool = True) -> Optional[Product]:
        logger.info(f"PriceUpdateService: updating price for product_id={product_id}")

        if force_search:
            similar_products = self._search_service.search_and_store_similar(product_id)
        else:
            similar_products = self._search_service.get_similar_products(product_id)

        if not similar_products:
            logger.warning(f"PriceUpdateService: no similar products for product_id={product_id}, skipping update")
            return None

        product = self._product_repo.get_by_id(product_id)
        if product is None:
            logger.error(f"PriceUpdateService: product_id={product_id} not found")
            return None

        suggested_price = self._calculate_suggested_price(product.price, similar_products)
        if suggested_price is None:
            logger.info(f"PriceUpdateService: no price update needed for product_id={product_id}")
            return product

        updated_product = self._product_repo.update_price(product_id, suggested_price)
        logger.success(
            f"PriceUpdateService: updated product_id={product_id} "
            f"from {product.price} to {suggested_price}"
        )
        return updated_product

    def bulk_update_prices(self) -> dict:
        logger.info("PriceUpdateService: starting bulk price update")
        products = self._product_repo.get_all()
        results = {"updated": 0, "skipped": 0, "failed": 0}

        for product in products:
            try:
                result = self.update_product_price(product.id)
                if result and result.price != product.price:
                    results["updated"] += 1
                else:
                    results["skipped"] += 1
            except Exception as exc:
                logger.error(f"PriceUpdateService: failed to update product_id={product.id}: {exc}")
                results["failed"] += 1

        logger.success(f"PriceUpdateService: bulk update complete: {results}")
        return results
