from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app import exceptions
from app.schemas.reviews import Review as ReviewSchema, ReviewCreate
from app.schemas.users import User
from app.models.reviews import Review as ReviewModel
from app.models.products import Product as ProductModel
from app.services.products import ProductService
from app.enums import Role


class ReviewService:
    def __init__(self, db: AsyncSession, product_service: ProductService):
        self.db = db
        self.product_service = product_service

    async def get_all_reviews(self) -> list[ReviewSchema]:
        result = await self.db.scalars(select(ReviewModel).where(ReviewModel.is_active))
        
        return [ReviewSchema.model_validate(review) for review in result.all()]

    async def create_review(
        self, review_create: ReviewCreate, author: User
    ) -> ReviewSchema:
        await self.product_service.get_product(review_create.product_id)

        review_to_add = ReviewModel(
            **review_create.model_dump(),
            user_id=author.id,
        )
        self.db.add(review_to_add)

        await self.db.flush()
        await self._recalculate_product_rating(review_create.product_id)

        await self.db.commit()
        return ReviewSchema.model_validate(review_to_add)

    async def delete_review(self, review_id: int, current_user: User) -> ReviewSchema:
        review_to_delete = await self._get_review_model(review_id)
        if review_to_delete is None:
            raise exceptions.NotFoundError("review not found or inactive")
        if (
            review_to_delete.user_id != current_user.id
            and current_user.role != Role.ADMIN
        ):
            raise exceptions.ForbiddenError("only author or admins can delete reviews")

        review_to_delete.is_active = False

        await self.db.flush()
        await self._recalculate_product_rating(review_to_delete.product_id)

        await self.db.commit()
        return ReviewSchema.model_validate(review_to_delete)

    async def _get_review_model(self, review_id: int) -> ReviewModel | None:
        return await self.db.scalar(
            select(ReviewModel).where(
                ReviewModel.is_active, ReviewModel.id == review_id
            )
        )

    async def _recalculate_product_rating(self, product_id: int) -> None:
        current_rating = await self.product_service.get_rating(product_id)
        await self.db.execute(
            update(ProductModel)
            .where(ProductModel.is_active, ProductModel.id == product_id)
            .values(rating=current_rating)
        )
