"""Product schema for request/response validation."""
from typing import Optional, List, TYPE_CHECKING
from pydantic import Field

from schemas.base_schema import BaseSchema

if TYPE_CHECKING:
    from schemas.category_schema import CategorySchema
    from schemas.order_detail_schema import OrderDetailSchema
    from schemas.review_schema import ReviewSchema


class ProductSchema(BaseSchema):
    """Schema for Product entity with validations."""

    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Product name (required)")
    price: Optional[float] = Field(None, gt=0, description="Product price (must be greater than 0, required)")
    stock: Optional[int] = Field(default=0, ge=0, description="Product stock quantity (must be >= 0)")

    category_id: Optional[int] = None  # Permitir None para productos sin categoría

    category: Optional['CategorySchema'] = None
    reviews: Optional[List['ReviewSchema']] = []
    order_details: Optional[List['OrderDetailSchema']] = []

    # Campos de solo lectura (calculados)
    category_name: Optional[str] = None
    rating: Optional[float] = Field(default=None, ge=0, le=5)

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
