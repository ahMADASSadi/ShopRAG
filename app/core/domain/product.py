from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class Product:
    id: int
    name: str
    description: str
    price: Decimal
    category: str
    sku: str
    stock: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    image_url: Optional[str] = None
