import re
from decimal import Decimal, InvalidOperation
from typing import List

from duckduckgo_search import DDGS
from loguru import logger

from app.core.domain.similar_product import SimilarProduct
from app.core.ports.web_searcher import WebSearcherPort
from app.config import get_settings

settings = get_settings()


def _extract_price(text: str) -> Decimal:
    """Extract a price from a text snippet."""
    patterns = [
        r'\$\s*([\d,]+\.?\d*)',
        r'([\d,]+\.?\d*)\s*USD',
        r'price[:\s]*([\d,]+\.?\d*)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            price_str = match.group(1).replace(',', '')
            try:
                return Decimal(price_str)
            except InvalidOperation:
                continue
    return Decimal("0.00")


class DuckDuckGoSearcher(WebSearcherPort):
    def search_similar_products(
        self,
        product_name: str,
        product_id: int,
        max_results: int = 5,
    ) -> List[SimilarProduct]:
        query = f"{product_name} price buy online"
        logger.info(f"Searching web for: '{query}' (product_id={product_id})")
        similar_products: List[SimilarProduct] = []

        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))

            for idx, result in enumerate(results):
                title = result.get("title", "")
                body = result.get("body", "")
                url = result.get("href", "")

                price = _extract_price(body) or _extract_price(title)
                similarity_score = max(0.0, 1.0 - idx * 0.1)

                similar_products.append(
                    SimilarProduct(
                        product_id=product_id,
                        source_name=result.get("source", url.split("/")[2] if url else "unknown"),
                        source_url=url,
                        price=price,
                        similarity_score=similarity_score,
                        title=title,
                        currency="USD",
                    )
                )
                logger.debug(f"Found similar product: '{title}' price={price} url={url}")

        except Exception as exc:
            logger.error(f"Web search failed for product_id={product_id}: {exc}")

        logger.success(f"Found {len(similar_products)} similar products for product_id={product_id}")
        return similar_products
