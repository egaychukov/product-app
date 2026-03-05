from decimal import Decimal
from datetime import datetime

import pytest
from pytest_mock import MockFixture

from app import exceptions
from app.enums import Role
from app.schemas.products import Product as ProductSchema, ProductCreate
from app.schemas.users import User as UserSchema
from app.schemas.reviews import Review as ReviewSchema
from app.services.products import ProductService


@pytest.mark.asyncio
async def test_get_product_success(mocker: MockFixture):
    # arrange
    product_id = 1
    expected_product = ProductSchema(
        id=product_id,
        name="prod",
        description=None,
        price=10,
        image_url=None,
        stock=5,
        is_active=True,
        category_id=1,
        rating=0,
        seller_id=1,
    )

    mock_repository = mocker.MagicMock()
    mock_repository.get_product = mocker.AsyncMock(return_value=expected_product)
    mock_category_service = mocker.MagicMock()

    product_service = ProductService(mock_repository, mock_category_service)

    # act
    actual_product = await product_service.get_product(product_id)

    # assert
    assert actual_product == expected_product
    mock_repository.get_product.assert_awaited_once_with(product_id)


@pytest.mark.asyncio
async def test_get_product_not_found_raises(mocker: MockFixture):
    # arrange
    product_id = 1

    mock_repository = mocker.MagicMock()
    mock_repository.get_product = mocker.AsyncMock(return_value=None)
    mock_category_service = mocker.MagicMock()

    product_service = ProductService(mock_repository, mock_category_service)

    # act
    with pytest.raises(exceptions.NotFoundError):
        await product_service.get_product(product_id)

    # assert
    mock_repository.get_product.assert_awaited_once_with(product_id)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "expected_products",
    [
        ([],),
        (
            [
                ProductSchema(
                    id=1,
                    name="prod1",
                    description=None,
                    price=10,
                    image_url=None,
                    stock=5,
                    is_active=True,
                    category_id=1,
                    rating=0,
                    seller_id=1,
                ),
                ProductSchema(
                    id=2,
                    name="prod2",
                    description=None,
                    price=20,
                    image_url=None,
                    stock=10,
                    is_active=True,
                    category_id=1,
                    rating=0,
                    seller_id=2,
                ),
            ],
        ),
    ],
)
async def test_get_all_products_success(
    expected_products: list[ProductSchema], mocker: MockFixture
):
    # arrange
    mock_repository = mocker.MagicMock()
    mock_repository.get_all_products = mocker.AsyncMock(return_value=expected_products)
    mock_category_service = mocker.MagicMock()

    product_service = ProductService(mock_repository, mock_category_service)

    # act
    actual_products = await product_service.get_all_products()

    # assert
    assert actual_products == expected_products
    mock_repository.get_all_products.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_category_products_success(mocker: MockFixture):
    # arrange
    category_id = 1
    expected_products = [
        ProductSchema(
            id=1,
            name="prod1",
            description=None,
            price=10,
            image_url=None,
            stock=5,
            is_active=True,
            category_id=category_id,
            rating=0,
            seller_id=1,
        )
    ]

    mock_repository = mocker.MagicMock()
    mock_repository.get_category_products = mocker.AsyncMock(
        return_value=expected_products
    )
    mock_category_service = mocker.MagicMock()
    mock_category_service.get_category = mocker.AsyncMock()

    product_service = ProductService(mock_repository, mock_category_service)

    # act
    actual_products = await product_service.get_category_products(category_id)

    # assert
    assert actual_products == expected_products
    mock_category_service.get_category.assert_awaited_once_with(category_id)
    mock_repository.get_category_products.assert_awaited_once_with(category_id)


@pytest.mark.asyncio
async def test_get_category_products_category_not_found(mocker: MockFixture):
    # arrange
    category_id = 1

    mock_repository = mocker.MagicMock()
    mock_repository.get_category_products = mocker.AsyncMock()
    mock_category_service = mocker.MagicMock()
    mock_category_service.get_category = mocker.AsyncMock(
        side_effect=exceptions.NotFoundError("category not found or inactive")
    )

    product_service = ProductService(mock_repository, mock_category_service)

    # act
    with pytest.raises(exceptions.NotFoundError):
        await product_service.get_category_products(category_id)

    # assert
    mock_category_service.get_category.assert_awaited_once_with(category_id)
    mock_repository.get_category_products.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_rating_with_existing_rating(mocker: MockFixture):
    # arrange
    product_id = 1
    expected_rating = Decimal("4.50")

    mock_repository = mocker.MagicMock()
    mock_repository.get_rating = mocker.AsyncMock(return_value=expected_rating)
    mock_category_service = mocker.MagicMock()

    product_service = ProductService(mock_repository, mock_category_service)

    # act
    actual_rating = await product_service.get_rating(product_id)

    # assert
    assert actual_rating == expected_rating
    mock_repository.get_rating.assert_awaited_once_with(product_id)


@pytest.mark.asyncio
async def test_get_rating_with_no_reviews_returns_zero(mocker: MockFixture):
    # arrange
    product_id = 1
    
    mock_repository = mocker.MagicMock()
    mock_repository.get_rating = mocker.AsyncMock(return_value=None)
    mock_category_service = mocker.MagicMock()

    product_service = ProductService(mock_repository, mock_category_service)

    # act
    actual_rating = await product_service.get_rating(product_id)

    # assert
    assert actual_rating == Decimal("0.00")
    mock_repository.get_rating.assert_awaited_once_with(product_id)


@pytest.mark.asyncio
async def test_get_product_reviews_success(mocker: MockFixture):
    # arrange
    product_id = 1
    product = ProductSchema(
        id=product_id,
        name="prod",
        description=None,
        price=10,
        image_url=None,
        stock=5,
        is_active=True,
        category_id=1,
        rating=0,
        seller_id=1,
    )
    reviews = [
        ReviewSchema(
            id=1,
            comment="good",
            comment_date=datetime.now(),
            grade=5,
            is_active=True,
            user_id=1,
            product_id=product_id,
        )
    ]
    mock_repository = mocker.MagicMock()
    mock_repository.get_product_reviews = mocker.AsyncMock(return_value=reviews)
    mock_repository.get_product = mocker.AsyncMock(return_value=product)
    mock_category_service = mocker.MagicMock()

    product_service = ProductService(mock_repository, mock_category_service)

    # act
    actual_reviews = await product_service.get_product_reviews(product_id)

    # assert
    assert actual_reviews == reviews
    mock_repository.get_product.assert_awaited_once_with(product_id)
    mock_repository.get_product_reviews.assert_awaited_once_with(product_id)


@pytest.mark.asyncio
async def test_get_product_reviews_product_not_found(mocker: MockFixture):
    # arrange
    product_id = 1
    mock_repository = mocker.MagicMock()
    mock_repository.get_product = mocker.AsyncMock(return_value=None)
    mock_repository.get_product_reviews = mocker.AsyncMock()
    mock_category_service = mocker.MagicMock()

    product_service = ProductService(mock_repository, mock_category_service)

    # act
    with pytest.raises(exceptions.NotFoundError):
        await product_service.get_product_reviews(product_id)

    # assert
    mock_repository.get_product.assert_awaited_once_with(product_id)
    mock_repository.get_product_reviews.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_product_success(mocker: MockFixture):
    # arrange
    category_id = 1
    seller = UserSchema(id=1, email="seller@example.com", is_active=True, role=Role.SELLER)
    product_create = ProductCreate(
        name="prod",
        description=None,
        price=10,
        image_url=None,
        stock=5,
        category_id=category_id,
    )
    expected_product = ProductSchema(
        id=1,
        name=product_create.name,
        description=product_create.description,
        price=product_create.price,
        image_url=product_create.image_url,
        stock=product_create.stock,
        is_active=True,
        category_id=category_id,
        rating=0,
        seller_id=seller.id,
    )

    mock_repository = mocker.MagicMock()
    mock_repository.create_product = mocker.AsyncMock(return_value=expected_product)
    mock_category_service = mocker.MagicMock()
    mock_category_service.get_category = mocker.AsyncMock()

    product_service = ProductService(mock_repository, mock_category_service)

    # act
    actual_product = await product_service.create_product(product_create, seller)

    # assert
    assert actual_product == expected_product
    mock_category_service.get_category.assert_awaited_once_with(category_id)
    mock_repository.create_product.assert_awaited_once_with(product_create, seller)


@pytest.mark.asyncio
async def test_create_product_category_not_found(mocker: MockFixture):
    # arrange
    category_id = 1
    seller = UserSchema(id=1, email="seller@example.com", is_active=True, role=Role.SELLER)
    product_create = ProductCreate(
        name="prod",
        description=None,
        price=10,
        image_url=None,
        stock=5,
        category_id=category_id,
    )

    mock_repository = mocker.MagicMock()
    mock_repository.create_product = mocker.AsyncMock()
    mock_category_service = mocker.MagicMock()
    mock_category_service.get_category = mocker.AsyncMock(
        side_effect=exceptions.NotFoundError("category not found or inactive")
    )

    product_service = ProductService(mock_repository, mock_category_service)

    # act
    with pytest.raises(exceptions.NotFoundError):
        await product_service.create_product(product_create, seller)

    # assert
    mock_category_service.get_category.assert_awaited_once_with(category_id)
    mock_repository.create_product.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_product_success(mocker: MockFixture):
    # arrange
    product_id = 1
    seller = UserSchema(id=1, email="seller@example.com", is_active=True, role=Role.SELLER)
    expected_product = ProductSchema(
        id=product_id,
        name="prod",
        description=None,
        price=10,
        image_url=None,
        stock=5,
        is_active=True,
        category_id=1,
        rating=0,
        seller_id=seller.id,
    )

    mock_repository = mocker.MagicMock()
    mock_repository.get_product = mocker.AsyncMock(return_value=expected_product)
    mock_repository.delete_product = mocker.AsyncMock(return_value=expected_product)
    mock_category_service = mocker.MagicMock()

    product_service = ProductService(mock_repository, mock_category_service)

    # act
    actual_product = await product_service.delete_product(product_id, seller)

    # assert
    assert actual_product == expected_product
    mock_repository.get_product.assert_awaited_once_with(product_id)
    mock_repository.delete_product.assert_awaited_once_with(product_id)


@pytest.mark.asyncio
async def test_delete_product_forbidden_for_non_owner(mocker: MockFixture):
    # arrange
    product_id = 1
    owner = 1
    current_user = UserSchema(id=2, email="user@example.com", is_active=True, role=Role.SELLER)
    product = ProductSchema(
        id=product_id,
        name="prod",
        description=None,
        price=10,
        image_url=None,
        stock=5,
        is_active=True,
        category_id=1,
        rating=0,
        seller_id=owner,
    )

    mock_repository = mocker.MagicMock()
    mock_repository.get_product = mocker.AsyncMock(return_value=product)
    mock_repository.delete_product = mocker.AsyncMock()
    mock_category_service = mocker.MagicMock()

    product_service = ProductService(mock_repository, mock_category_service)

    # act
    with pytest.raises(exceptions.ForbiddenError):
        await product_service.delete_product(product_id, current_user)

    # assert
    mock_repository.get_product.assert_awaited_once_with(product_id)
    mock_repository.delete_product.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_product_not_found(mocker: MockFixture):
    # arrange
    product_id = 1
    current_user = UserSchema(id=1, email="user@example.com", is_active=True, role=Role.SELLER)

    mock_repository = mocker.MagicMock()
    mock_repository.get_product = mocker.AsyncMock(return_value=None)
    mock_repository.delete_product = mocker.AsyncMock()
    mock_category_service = mocker.MagicMock()

    product_service = ProductService(mock_repository, mock_category_service)

    # act
    with pytest.raises(exceptions.NotFoundError):
        await product_service.delete_product(product_id, current_user)

    # assert
    mock_repository.get_product.assert_awaited_once_with(product_id)
    mock_repository.delete_product.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_product_success(mocker: MockFixture):
    # arrange
    product_id = 1
    new_category_id = 2
    seller = UserSchema(id=1, email="seller@example.com", is_active=True, role=Role.SELLER)
    product = ProductSchema(
        id=product_id,
        name="prod",
        description=None,
        price=10,
        image_url=None,
        stock=5,
        is_active=True,
        category_id=1,
        rating=0,
        seller_id=seller.id,
    )
    product_update = ProductCreate(
        name="new-name",
        description="new-desc",
        price=20,
        image_url=None,
        stock=10,
        category_id=new_category_id,
    )
    updated_product = product.model_copy(update={"name": product_update.name, "category_id": new_category_id})

    mock_repository = mocker.MagicMock()
    mock_repository.get_product = mocker.AsyncMock(return_value=product)
    mock_repository.update_product = mocker.AsyncMock(return_value=updated_product)
    mock_category_service = mocker.MagicMock()
    mock_category_service.get_category = mocker.AsyncMock()

    product_service = ProductService(mock_repository, mock_category_service)

    # act
    actual_product = await product_service.update_product(
        product_id, product_update, seller
    )

    # assert
    assert actual_product == updated_product
    mock_repository.get_product.assert_awaited_once_with(product_id)
    mock_category_service.get_category.assert_awaited_once_with(new_category_id)
    mock_repository.update_product.assert_awaited_once_with(product_id, product_update)


@pytest.mark.asyncio
async def test_update_product_forbidden_for_non_owner(mocker: MockFixture):
    # arrange
    product_id = 1
    owner = 1
    current_user = UserSchema(id=2, email="user@example.com", is_active=True, role=Role.SELLER)
    product = ProductSchema(
        id=product_id,
        name="prod",
        description=None,
        price=10,
        image_url=None,
        stock=5,
        is_active=True,
        category_id=1,
        rating=0,
        seller_id=owner,
    )
    product_update = ProductCreate(
        name="new-name",
        description="new-desc",
        price=20,
        image_url=None,
        stock=10,
        category_id=1,
    )

    mock_repository = mocker.MagicMock()
    mock_repository.get_product = mocker.AsyncMock(return_value=product)
    mock_repository.update_product = mocker.AsyncMock()
    mock_category_service = mocker.MagicMock()
    mock_category_service.get_category = mocker.AsyncMock()

    product_service = ProductService(mock_repository, mock_category_service)

    # act
    with pytest.raises(exceptions.ForbiddenError):
        await product_service.update_product(product_id, product_update, current_user)

    # assert
    mock_repository.get_product.assert_awaited_once_with(product_id)
    mock_category_service.get_category.assert_not_awaited()
    mock_repository.update_product.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_product_not_found(mocker: MockFixture):
    # arrange
    product_id = 1
    current_user = UserSchema(id=1, email="user@example.com", is_active=True, role=Role.SELLER)
    product_update = ProductCreate(
        name="new-name",
        description="new-desc",
        price=20,
        image_url=None,
        stock=10,
        category_id=1,
    )

    mock_repository = mocker.MagicMock()
    mock_repository.get_product = mocker.AsyncMock(return_value=None)
    mock_repository.update_product = mocker.AsyncMock()
    mock_category_service = mocker.MagicMock()
    mock_category_service.get_category = mocker.AsyncMock()

    product_service = ProductService(mock_repository, mock_category_service)

    # act
    with pytest.raises(exceptions.NotFoundError):
        await product_service.update_product(product_id, product_update, current_user)

    # assert
    mock_repository.get_product.assert_awaited_once_with(product_id)
    mock_category_service.get_category.assert_not_awaited()
    mock_repository.update_product.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_product_category_not_found(mocker: MockFixture):
    # arrange
    product_id = 1
    new_category_id = 2
    seller = UserSchema(id=1, email="seller@example.com", is_active=True, role=Role.SELLER)
    product = ProductSchema(
        id=product_id,
        name="prod",
        description=None,
        price=10,
        image_url=None,
        stock=5,
        is_active=True,
        category_id=1,
        rating=0,
        seller_id=seller.id,
    )
    product_update = ProductCreate(
        name="new-name",
        description="new-desc",
        price=20,
        image_url=None,
        stock=10,
        category_id=new_category_id,
    )

    mock_repository = mocker.MagicMock()
    mock_repository.get_product = mocker.AsyncMock(return_value=product)
    mock_repository.update_product = mocker.AsyncMock()
    mock_category_service = mocker.MagicMock()
    mock_category_service.get_category = mocker.AsyncMock(
        side_effect=exceptions.NotFoundError("category not found or inactive")
    )

    product_service = ProductService(mock_repository, mock_category_service)

    # act
    with pytest.raises(exceptions.NotFoundError):
        await product_service.update_product(product_id, product_update, seller)

    # assert
    mock_repository.get_product.assert_awaited_once_with(product_id)
    mock_category_service.get_category.assert_awaited_once_with(new_category_id)
    mock_repository.update_product.assert_not_awaited()
