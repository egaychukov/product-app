from typing import AsyncGenerator, Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.database import async_session_maker
from app.repository.categories import CategoryRepository
from app.repository.products import ProductRepository
from app.repository.reviews import ReviewRepository
from app.services.products import ProductService
from app.services.reviews import ReviewService
from app.services.categories import CategoryService


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


def get_product_repository(
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> ProductRepository:
    return ProductRepository(db)


def get_product_service(
    product_repository: Annotated[ProductRepository, Depends(get_product_repository)],
    category_service: Annotated[CategoryService, Depends(get_category_service)],
) -> ProductService:
    return ProductService(product_repository, category_service)


def get_review_repository(
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> ReviewRepository:
    return ReviewRepository(db)


def get_review_service(
    review_repository: Annotated[ReviewRepository, Depends(get_review_repository)],
    product_service: Annotated[ProductService, Depends(get_product_service)],
) -> ReviewService:
    return ReviewService(review_repository, product_service)
