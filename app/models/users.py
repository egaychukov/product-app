from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    role: Mapped[str] = mapped_column(default="buyer")

    products: Mapped[list["Product"]] = relationship("Product", back_populates="seller")
