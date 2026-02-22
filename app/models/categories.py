from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(default=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))

    products: Mapped[list["Product"]] = relationship(back_populates="category")

    parent: Mapped["Category | None"] = relationship(back_populates="children", remote_side=[id])
    children: Mapped[list["Category"]] = relationship(back_populates="parent")

    def __repr__(self):
        return f"Category(id={self.id}, name={self.name}, parent_id={self.parent_id})"
