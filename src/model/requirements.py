from pydantic import BaseModel, Field
from typing import List, Optional

class ManufacturingRequirements(BaseModel):
    product_type: str  # Broad category: electronics, consumer_goods, industrial, apparel, etc.
    product_description: Optional[str] = None  # Specific product: "jackets", "kitchen organizers", etc.
    materials: List[str] = Field(default_factory=list)
    moq: int
    geography: Optional[str] = None
    certifications: List[str] = Field(default_factory=list)
    budget_tier: Optional[str] = None
