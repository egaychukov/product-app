from typing import AsyncGenerator, Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.database import async_session_maker
from app.services.products import ProductService
from app.services.reviews import ReviewService
from app.services.categories import CategoryService
from app.repository.categories import CategoryRepository


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


def get_category_repository(
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> CategoryRepository:
    return CategoryRepository(db)


def get_category_service(
    category_repository: Annotated[CategoryRepository, Depends(get_category_repository)],
) -> CategoryService:
    return CategoryService(category_repository)


def get_product_service(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    category_service: Annotated[CategoryService, Depends(get_category_service)],
) -> ProductService:
    return ProductService(db, category_service)


def get_review_service(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    product_service: Annotated[ProductService, Depends(get_product_service)],
) -> ReviewService:
    return ReviewService(db, product_service)
