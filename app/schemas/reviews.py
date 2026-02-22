from typing import Annotated
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class ReviewCreate(BaseModel):
    product_id: int
    comment: str | None = None
    grade: Annotated[int, Field(ge=1, le=5)]


class Review(BaseModel):
    id: int
    comment: str | None = None
    comment_date: datetime
    grade: int
    is_active: bool
    user_id: int
    product_id: int

    model_config = ConfigDict(from_attributes=True)
