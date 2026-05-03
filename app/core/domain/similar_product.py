from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class SimilarProduct:
    product_id: int
    source_name: str
    source_url: str
    price: Decimal
    similarity_score: float
    title: str
    currency: str = "USD"
    image_url: Optional[str] = None
