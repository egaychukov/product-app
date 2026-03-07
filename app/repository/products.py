from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from app.models.products import Product as ProductModel
from app.models.reviews import Review as ReviewModel
from app.schemas.products import Product as ProductSchema, ProductCreate
from app.schemas.users import User
from app.schemas.reviews import Review as ReviewSchema


class ProductRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_product(self, product_id: int) -> ProductSchema | None:
        product = await self._get_model(product_id)

        return ProductSchema.model_validate(product) if product else None

    async def get_products(self, page: int, page_size: int) -> list[ProductSchema]:
        result = await self.db.scalars(
            select(ProductModel)
            .where(ProductModel.is_active)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .order_by(ProductModel.id)
        )

        return [ProductSchema.model_validate(product) for product in result.all()]

    async def get_category_products(self, category_id: int) -> list[ProductSchema]:
        result = await self.db.scalars(
            select(ProductModel).where(
                ProductModel.is_active, ProductModel.category_id == category_id
            )
        )

        return [ProductSchema.model_validate(product) for product in result.all()]

    async def get_active_product_count(self) -> int:
        count = await self.db.scalar(
            select(func.count("*"))
            .select_from(ProductModel)
            .where(ProductModel.is_active)
        )

        return count or 0

    async def get_rating(self, product_id: int) -> Decimal | None:
        return await self.db.scalar(
            select(func.avg(ReviewModel.grade)).where(
                ReviewModel.is_active, ReviewModel.product_id == product_id
            )
        )

    async def get_product_reviews(self, product_id: int) -> list[ReviewSchema]:
        product_reviews = await self._get_product_review_models(product_id)

        return [ReviewSchema.model_validate(review) for review in product_reviews]

    async def create_product(
        self, product_create: ProductCreate, seller_user: User
    ) -> ProductSchema:
        product_to_add = ProductModel(
            **product_create.model_dump(), seller_id=seller_user.id
        )
        self.db.add(product_to_add)

        await self.db.commit()
        await self.db.refresh(product_to_add)
        return ProductSchema.model_validate(product_to_add)

    async def delete_product(self, product_id: int) -> ProductSchema | None:
        product_to_delete = await self._get_model(product_id)
        if product_to_delete is None:
            return None

        product_reviews = await self._get_product_review_models(product_id)
        for review in product_reviews:
            review.is_active = False

        product_to_delete.is_active = False

        await self.db.commit()
        return ProductSchema.model_validate(product_to_delete)

    async def update_product(
        self, product_id: int, product_create: ProductCreate
    ) -> ProductSchema | None:
        product_to_update = await self._get_model(product_id)
        if product_to_update is None:
            return None

        await self.db.execute(
            update(ProductModel)
            .where(ProductModel.id == product_id)
            .values(**product_create.model_dump(exclude_unset=True))
        )

        await self.db.commit()
        await self.db.refresh(product_to_update)
        return ProductSchema.model_validate(product_to_update)

    async def _get_model(self, product_id: int) -> ProductModel | None:
        return await self.db.scalar(
            select(ProductModel).where(
                ProductModel.is_active, ProductModel.id == product_id
            )
        )

    async def _get_product_review_models(self, product_id: int) -> list[ReviewModel]:
        result = await self.db.scalars(
            select(ReviewModel).where(
                ReviewModel.is_active, ReviewModel.product_id == product_id
            )
        )

        return list(result.all())
