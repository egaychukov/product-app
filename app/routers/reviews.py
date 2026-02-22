from typing import Annotated

from fastapi import Depends, APIRouter, status

from app.db_depends import get_review_service
from app.schemas.reviews import Review as ReviewSchema, ReviewCreate
from app.schemas.users import User
from app.services.reviews import ReviewService
from app.auth import get_current_role, get_current_user
from app.enums import Role


router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/")
async def get_all_reviews(
    review_service: Annotated[ReviewService, Depends(get_review_service)],
) -> list[ReviewSchema]:
    """
    Get all active reviews.

    Returns:
        A list of ReviewSchema objects representing the reviews.
    """
    return await review_service.get_all_reviews()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_review(
    review_create: ReviewCreate,
    current_user: Annotated[User, Depends(get_current_role(Role.BUYER))],
    review_service: Annotated[ReviewService, Depends(get_review_service)],
) -> ReviewSchema:
    """
    Create a new review for a product.

    Args:
        review_create: ReviewCreate object containing product_id, grade, and optional comment.

    Returns:
        A ReviewSchema object representing the created review.

    Raises:
        HTTP 403: If the user is not a buyer.
        HTTP 404: If the product is not found or inactive.
        HTTP 422: If the request body is invalid.
    """
    created_review = await review_service.create_review(review_create, current_user)

    return created_review


@router.delete("/{review_id}")
async def delete_review(
    review_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    review_service: Annotated[ReviewService, Depends(get_review_service)],
) -> ReviewSchema:
    """
    Soft-delete a review.

    Args:
        review_id: ID of the review to delete.

    Returns:
        A ReviewSchema object representing the soft-deleted review.

    Raises:
        HTTP 403: If the user is not the author and not an admin.
        HTTP 404: If the review is not found or inactive.
    """
    deleted_review = await review_service.delete_review(review_id, current_user)

    return deleted_review
