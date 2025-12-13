"""
Schema for Review entity validation
"""
from typing import Optional, TYPE_CHECKING
from pydantic import Field
from schemas.base_schema import BaseSchema

if TYPE_CHECKING:
    from schemas.product_schema import ProductSchema


class ReviewSchemaBase(BaseSchema):
    """
    Review schema without product relationship to avoid circular reference.
    Used when reviews are embedded in ProductSchema.
    """

    rating: Optional[float] = Field(
        None,
        ge=0,
        le=5,
        description="Rating from 0 to 5"
    )

    comment: Optional[str] = Field(
        None,
        max_length=1000,
        description="Review comment"
    )

    product_id: Optional[int] = Field(
        None,
        description="Product ID"
    )


class ReviewSchema(ReviewSchemaBase):
    """
    Full Review schema with optional product reference.
    Note: 'product' field excluded to prevent circular reference.
    Use product_id to reference the product.
    """

    rating: float = Field(
        ...,
        ge=1.0,
        le=5.0,
        description="Rating from 1 to 5 stars (required)"
    )

    comment: Optional[str] = Field(
        None,
        min_length=10,
        max_length=1000,
        description="Review comment (optional, 10-1000 characters)"
    )

    product_id: int = Field(
        ...,
        description="Product ID reference (required)"
    )

    product: Optional['ProductSchema'] = None
