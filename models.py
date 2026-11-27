from dataclasses import dataclass
from typing import Optional

@dataclass
class Checkout:
    status: str
    item: str
    price: str
    site: str
    quantity: str
    profile: str
    cancel_reason: str = "N/A"
    image_url: Optional[str] = None
