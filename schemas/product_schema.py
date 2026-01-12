"""Product schema for request/response validation."""
from typing import Optional, List, TYPE_CHECKING
from pydantic import Field

from schemas.base_schema import BaseSchema

if TYPE_CHECKING:
    from schemas.category_schema import CategorySchema
    from schemas.order_detail_schema import OrderDetailSchema


class ProductSchemaBase(BaseSchema):
    """
    Base Product schema without relationships to avoid circular references.
    Used when products are embedded in other schemas (e.g., OrderDetailSchema).
    """

    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Product name")
    price: Optional[float] = Field(None, gt=0, description="Product price (must be positive)")
    stock: Optional[int] = Field(None, ge=0, description="Available stock quantity")
    category_id: Optional[int] = Field(None, description="Category ID")


class ReviewEmbedded(BaseSchema):
    """
    Embedded review schema for use within ProductSchema.
    Excludes product reference to prevent circular recursion.
    """

    rating: Optional[float] = Field(None, ge=0, le=5, description="Rating from 0 to 5")
    comment: Optional[str] = Field(None, max_length=1000, description="Review comment")
    product_id: Optional[int] = Field(None, description="Product ID")


class ProductSchema(ProductSchemaBase):
    """
    Full Product schema with embedded reviews (non-recursive).

    Note: reviews are embedded using ReviewEmbedded which doesn't reference
    back to ProductSchema, breaking the circular reference.
    """

    # Category name for display (computed field, not stored)
    category_name: Optional[str] = Field(None, description="Category name (read-only)")

    # Average rating (computed from reviews)
    rating: Optional[float] = Field(None, ge=0, le=5, description="Average rating")

    # Embedded reviews without circular reference
    reviews: Optional[List[ReviewEmbedded]] = Field(default=None, description="Product reviews")

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
