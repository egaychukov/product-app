from datetime import datetime

import pytest
from pytest_mock import MockFixture

from app import exceptions
from app.enums import Role
from app.schemas.reviews import Review as ReviewSchema, ReviewCreate
from app.schemas.users import User as UserSchema
from app.services.reviews import ReviewService


test_datetime = datetime.now()


@pytest.mark.asyncio
async def test_get_all_reviews_success(mocker: MockFixture):
    # arrange
    reviews = [
        ReviewSchema(
            id=1,
            comment="good",
            comment_date=test_datetime,
            grade=5,
            is_active=True,
            user_id=1,
            product_id=1,
        ),
        ReviewSchema(
            id=2,
            comment="ok",
            comment_date=test_datetime,
            grade=3,
            is_active=True,
            user_id=2,
            product_id=1,
        ),
    ]
    mock_repository = mocker.MagicMock()
    mock_repository.get_all_reviews = mocker.AsyncMock(return_value=reviews)
    mock_product_service = mocker.MagicMock()

    review_service = ReviewService(mock_repository, mock_product_service)

    # act
    actual_reviews = await review_service.get_all_reviews()

    # assert
    assert actual_reviews == reviews
    mock_repository.get_all_reviews.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_review_success(mocker: MockFixture):
    # arrange
    review_create = ReviewCreate(product_id=1, comment="nice", grade=5)
    author = UserSchema(
        id=1, email="user@example.com", is_active=True, role=Role.BUYER
    )
    expected_review = ReviewSchema(
        id=1,
        comment=review_create.comment,
        comment_date=test_datetime,
        grade=review_create.grade,
        is_active=True,
        user_id=author.id,
        product_id=review_create.product_id,
    )

    mock_repository = mocker.MagicMock()
    mock_repository.create_review = mocker.AsyncMock(return_value=expected_review)
    mock_product_service = mocker.MagicMock()
    mock_product_service.get_product = mocker.AsyncMock()

    review_service = ReviewService(mock_repository, mock_product_service)

    # act
    actual_review = await review_service.create_review(review_create, author)

    # assert
    assert actual_review == expected_review
    mock_product_service.get_product.assert_awaited_once_with(
        review_create.product_id
    )
    mock_repository.create_review.assert_awaited_once_with(review_create, author.id)


@pytest.mark.asyncio
async def test_create_review_product_not_found(mocker: MockFixture):
    # arrange
    review_create = ReviewCreate(product_id=1, comment="nice", grade=5)
    author = UserSchema(
        id=1, email="user@example.com", is_active=True, role=Role.BUYER
    )

    mock_repository = mocker.MagicMock()
    mock_repository.create_review = mocker.AsyncMock()
    mock_product_service = mocker.MagicMock()
    mock_product_service.get_product = mocker.AsyncMock(
        side_effect=exceptions.NotFoundError("product not found or inactive")
    )

    review_service = ReviewService(mock_repository, mock_product_service)

    # act
    with pytest.raises(exceptions.NotFoundError):
        await review_service.create_review(review_create, author)

    # assert
    mock_product_service.get_product.assert_awaited_once_with(
        review_create.product_id
    )
    mock_repository.create_review.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_review_success_by_author(mocker: MockFixture):
    # arrange
    review_id = 1
    current_user = UserSchema(
        id=1, email="author@example.com", is_active=True, role=Role.BUYER
    )
    expected_review = ReviewSchema(
        id=review_id,
        comment="nice",
        comment_date=test_datetime,
        grade=5,
        is_active=True,
        user_id=current_user.id,
        product_id=1,
    )

    mock_repository = mocker.MagicMock()
    mock_repository.get_review = mocker.AsyncMock(return_value=expected_review)
    mock_repository.delete_review = mocker.AsyncMock(return_value=expected_review)
    mock_product_service = mocker.MagicMock()

    review_service = ReviewService(mock_repository, mock_product_service)

    # act
    actual_review = await review_service.delete_review(review_id, current_user)

    # assert
    assert actual_review == expected_review
    mock_repository.get_review.assert_awaited_once_with(review_id)
    mock_repository.delete_review.assert_awaited_once_with(review_id)


@pytest.mark.asyncio
async def test_delete_review_success_by_admin(mocker: MockFixture):
    # arrange
    review_id = 1
    author_id = 1
    current_user = UserSchema(
        id=2, email="admin@example.com", is_active=True, role=Role.ADMIN
    )
    expected_review = ReviewSchema(
        id=review_id,
        comment="nice",
        comment_date=test_datetime,
        grade=5,
        is_active=True,
        user_id=author_id,
        product_id=1,
    )

    mock_repository = mocker.MagicMock()
    mock_repository.get_review = mocker.AsyncMock(return_value=expected_review)
    mock_repository.delete_review = mocker.AsyncMock(return_value=expected_review)
    mock_product_service = mocker.MagicMock()

    review_service = ReviewService(mock_repository, mock_product_service)

    # act
    actual_review = await review_service.delete_review(review_id, current_user)

    # assert
    assert actual_review == expected_review
    mock_repository.get_review.assert_awaited_once_with(review_id)
    mock_repository.delete_review.assert_awaited_once_with(review_id)


@pytest.mark.asyncio
async def test_delete_review_not_found(mocker: MockFixture):
    # arrange
    review_id = 1
    current_user = UserSchema(
        id=1, email="author@example.com", is_active=True, role=Role.BUYER
    )

    mock_repository = mocker.MagicMock()
    mock_repository.get_review = mocker.AsyncMock(return_value=None)
    mock_repository.delete_review = mocker.AsyncMock()
    mock_product_service = mocker.MagicMock()

    review_service = ReviewService(mock_repository, mock_product_service)

    # act
    with pytest.raises(exceptions.NotFoundError):
        await review_service.delete_review(review_id, current_user)

    # assert
    mock_repository.get_review.assert_awaited_once_with(review_id)
    mock_repository.delete_review.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_review_forbidden_for_non_author_non_admin(mocker: MockFixture):
    # arrange
    review_id = 1
    author_id = 1
    current_user = UserSchema(
        id=2, email="user@example.com", is_active=True, role=Role.BUYER
    )
    review = ReviewSchema(
        id=review_id,
        comment="nice",
        comment_date=test_datetime,
        grade=5,
        is_active=True,
        user_id=author_id,
        product_id=1,
    )

    mock_repository = mocker.MagicMock()
    mock_repository.get_review = mocker.AsyncMock(return_value=review)
    mock_repository.delete_review = mocker.AsyncMock()
    mock_product_service = mocker.MagicMock()

    review_service = ReviewService(mock_repository, mock_product_service)

    # act
    with pytest.raises(exceptions.ForbiddenError):
        await review_service.delete_review(review_id, current_user)

    # assert
    mock_repository.get_review.assert_awaited_once_with(review_id)
    mock_repository.delete_review.assert_not_awaited()
