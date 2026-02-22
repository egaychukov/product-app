from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from app import exceptions
from app.models.products import Product as ProductModel
from app.models.reviews import Review as ReviewModel
from app.schemas.products import Product as ProductSchema, ProductCreate
from app.schemas.reviews import Review as ReviewSchema
from app.schemas.users import User
from app.services.categories import CategoryService


class ProductService:
    def __init__(self, db: AsyncSession, category_service: CategoryService):
        self.db = db
        self.category_service = category_service

    async def get_product(self, product_id: int) -> ProductSchema:
        product = await self._get_product_model(product_id)
        if product is None:
            raise exceptions.NotFoundError("product not found or inactive")

        return ProductSchema.model_validate(product)

    async def get_all_products(self) -> list[ProductSchema]:
        result = await self.db.scalars(
            select(ProductModel).where(ProductModel.is_active)
        )

        return [ProductSchema.model_validate(product) for product in result.all()]

    async def get_category_products(self, category_id: int) -> list[ProductSchema]:
        await self.category_service.get_category(category_id)

        result = await self.db.scalars(
            select(ProductModel).where(
                ProductModel.is_active, ProductModel.category_id == category_id
            )
        )

        return [ProductSchema.model_validate(product) for product in result.all()]

    async def get_rating(self, product_id: int) -> Decimal:
        rating = await self.db.scalar(
            select(func.avg(ReviewModel.grade)).where(
                ReviewModel.is_active, ReviewModel.product_id == product_id
            )
        )

        return rating if rating is not None else Decimal("0.00")

    async def get_product_reviews(self, product_id: int) -> list[ReviewSchema]:
        await self.get_product(product_id)

        product_reviews = await self._get_product_review_models(product_id)

        return [ReviewSchema.model_validate(review) for review in product_reviews]

    async def create_product(
        self, product_create: ProductCreate, seller_user: User
    ) -> ProductSchema:
        await self.category_service.get_category(product_create.category_id)

        product_to_add = ProductModel(
            **product_create.model_dump(), seller_id=seller_user.id
        )
        self.db.add(product_to_add)

        await self.db.commit()
        return ProductSchema.model_validate(product_to_add)

    async def delete_product(
        self, product_id: int, current_user: User
    ) -> ProductSchema:
        product_to_delete = await self._get_product_model(product_id)
        product_to_delete = self._validate_product_access(
            product_to_delete, current_user
        )

        product_reviews = await self._get_product_review_models(product_id)
        for review in product_reviews:
            review.is_active = False

        product_to_delete.is_active = False

        await self.db.commit()
        return ProductSchema.model_validate(product_to_delete)

    async def update_product(
        self, product_id: int, product_create: ProductCreate, current_user: User
    ) -> ProductSchema:
        product_to_update = await self._get_product_model(product_id)
        product_to_update = self._validate_product_access(
            product_to_update, current_user
        )

        await self.category_service.get_category(product_create.category_id)

        await self.db.execute(
            update(ProductModel)
            .where(ProductModel.id == product_id)
            .values(**product_create.model_dump(exclude_unset=True))
        )

        await self.db.commit()
        await self.db.refresh(product_to_update)
        return ProductSchema.model_validate(product_to_update)

    async def _get_product_model(self, product_id: int) -> ProductModel | None:
        return await self.db.scalar(
            select(ProductModel).where(
                ProductModel.is_active, ProductModel.id == product_id
            )
        )

    def _validate_product_access(
        self, product_to_update: ProductModel | None, current_user: User
    ) -> ProductModel:
        if product_to_update is None:
            raise exceptions.NotFoundError("product not found or inactive")
        if product_to_update.seller_id != current_user.id:
            raise exceptions.ForbiddenError("you can only update/delete your own products")

        return product_to_update

    async def _get_product_review_models(self, product_id: int) -> list[ReviewModel]:
        result = await self.db.scalars(
            select(ReviewModel).where(
                ReviewModel.is_active, ReviewModel.product_id == product_id
            )
        )

        return list(result.all())
