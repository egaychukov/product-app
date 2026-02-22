from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict


class CategoryCreate(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=50)]
    parent_id: int | None = None


class Category(BaseModel):
    id: int
    name: str
    parent_id: int | None = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
