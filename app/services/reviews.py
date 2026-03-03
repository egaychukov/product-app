from app import exceptions
from app.enums import Role
from app.repository.reviews import ReviewRepository
from app.schemas.reviews import Review as ReviewSchema, ReviewCreate
from app.schemas.users import User
from app.services.products import ProductService


class ReviewService:
    def __init__(
        self,
        review_repository: ReviewRepository,
        product_service: ProductService,
    ) -> None:
        self.review_repository = review_repository
        self.product_service = product_service

    async def get_all_reviews(self) -> list[ReviewSchema]:
        return await self.review_repository.get_all_reviews()

    async def create_review(
        self, review_create: ReviewCreate, author: User
    ) -> ReviewSchema:
        await self.product_service.get_product(review_create.product_id)
    
        return await self.review_repository.create_review(
            review_create, author.id
        )

    async def delete_review(self, review_id: int, current_user: User) -> ReviewSchema:
        review = await self.review_repository.get_review(review_id)
        if review is None:
            raise exceptions.NotFoundError("review not found or inactive")
        if review.user_id != current_user.id and current_user.role != Role.ADMIN:
            raise exceptions.ForbiddenError(
                "only author or admins can delete reviews"
            )

        return await self.review_repository.delete_review(review_id)
