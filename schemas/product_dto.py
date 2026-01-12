from typing import Optional
from pydantic import BaseModel, ConfigDict


class ProductCreateDTO(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0
    category_id: int
    image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)