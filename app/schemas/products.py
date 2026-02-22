from typing import Annotated
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


class ProductCreate(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=100)]
    description: Annotated[str | None, Field(max_length=500)] = None
    price: Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]
    image_url: Annotated[str | None, Field(max_length=200)] = None
    stock: Annotated[int, Field(..., ge=0)]
    category_id: int


class Product(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: Annotated[Decimal, Field(gt=0, decimal_places=2)]
    image_url: str | None = None
    stock: int
    is_active: bool
    category_id: int
    rating: Annotated[Decimal, Field(max_digits=3, decimal_places=2)]

    model_config = ConfigDict(from_attributes=True)
