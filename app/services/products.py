from decimal import Decimal

from app import exceptions
from app.schemas.products import Product as ProductSchema, ProductCreate
from app.schemas.reviews import Review as ReviewSchema
from app.schemas.users import User
from app.repository.products import ProductRepository
from app.services.categories import CategoryService
from app.schemas.pagination import Page


class ProductService:
    def __init__(
        self, product_repository: ProductRepository, category_service: CategoryService
    ) -> None:
        self.product_repository = product_repository
        self.category_service = category_service

    async def get_product(self, product_id: int) -> ProductSchema:
        product = await self.product_repository.get_product(product_id)
        if product is None:
            raise exceptions.NotFoundError("product not found or inactive")

        return product

    async def get_products(self, page: int, page_size: int) -> Page[ProductSchema]:
        items = await self.product_repository.get_products(page, page_size)
        total = await self.product_repository.get_active_product_count()

        return Page(items=items, total=total, page=page, page_size=page_size)

    async def get_category_products(self, category_id: int) -> list[ProductSchema]:
        await self.category_service.get_category(category_id)

        return await self.product_repository.get_category_products(category_id)

    async def get_rating(self, product_id: int) -> Decimal:
        rating = await self.product_repository.get_rating(product_id)

        return rating if rating is not None else Decimal("0.00")

    async def get_product_reviews(self, product_id: int) -> list[ReviewSchema]:
        await self.get_product(product_id)

        return await self.product_repository.get_product_reviews(product_id)

    async def create_product(
        self, product_create: ProductCreate, seller_user: User
    ) -> ProductSchema:
        await self.category_service.get_category(product_create.category_id)

        return await self.product_repository.create_product(product_create, seller_user)

    async def delete_product(
        self, product_id: int, current_user: User
    ) -> ProductSchema:
        product_to_delete = await self.get_product(product_id)
        if product_to_delete.seller_id != current_user.id:
            raise exceptions.ForbiddenError("you can only delete your own products")

        return await self.product_repository.delete_product(product_id)

    async def update_product(
        self, product_id: int, product_create: ProductCreate, current_user: User
    ) -> ProductSchema:
        product_to_update = await self.get_product(product_id)
        if product_to_update.seller_id != current_user.id:
            raise exceptions.ForbiddenError("you can only update your own products")

        await self.category_service.get_category(product_create.category_id)

        return await self.product_repository.update_product(product_id, product_create)
