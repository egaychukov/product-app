from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    comment: Mapped[str | None]
    comment_date: Mapped[datetime] = mapped_column(default=datetime.now)
    grade: Mapped[int]
    is_active: Mapped[bool] = mapped_column(default=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))

    product: Mapped["Product"] = relationship(back_populates="reviews")
