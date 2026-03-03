from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func

from app.models.reviews import Review as ReviewModel
from app.models.products import Product as ProductModel
from app.schemas.reviews import Review as ReviewSchema, ReviewCreate


class ReviewRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_review(self, review_id: int) -> ReviewSchema | None:
        review = await self._get_model(review_id)
        return ReviewSchema.model_validate(review) if review else None

    async def get_all_reviews(self) -> list[ReviewSchema]:
        result = await self.db.scalars(
            select(ReviewModel).where(ReviewModel.is_active)
        )
        return [ReviewSchema.model_validate(review) for review in result.all()]

    async def create_review(
        self, review_create: ReviewCreate, user_id: int
    ) -> ReviewSchema:
        review_to_add = ReviewModel(
            **review_create.model_dump(),
            user_id=user_id,
        )
        self.db.add(review_to_add)
        await self.db.flush()

        await self._recalculate_product_rating(review_create.product_id)

        await self.db.commit()
        await self.db.refresh(review_to_add)
        return ReviewSchema.model_validate(review_to_add)

    async def delete_review(self, review_id: int) -> ReviewSchema | None:
        review_to_delete = await self._get_model(review_id)
        if review_to_delete is None:
            return None

        review_to_delete.is_active = False
        await self.db.flush()

        await self._recalculate_product_rating(review_to_delete.product_id)

        await self.db.commit()
        return ReviewSchema.model_validate(review_to_delete)

    async def _get_model(self, review_id: int) -> ReviewModel | None:
        return await self.db.scalar(
            select(ReviewModel).where(
                ReviewModel.is_active, ReviewModel.id == review_id
            )
        )

    async def _recalculate_product_rating(self, product_id: int) -> None:
        avg_result = await self.db.scalar(
            select(func.avg(ReviewModel.grade)).where(
                ReviewModel.is_active,
                ReviewModel.product_id == product_id,
            )
        )
        rating = Decimal(str(avg_result)) if avg_result is not None else Decimal("0.00")
        await self.db.execute(
            update(ProductModel)
            .where(ProductModel.id == product_id)
            .values(rating=rating)
        )
