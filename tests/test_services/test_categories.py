import pytest
from pytest_mock import MockFixture
from unittest.mock import call

from app import exceptions
from app.schemas.categories import Category as CategorySchema, CategoryCreate
from app.services.categories import CategoryService


@pytest.mark.asyncio
async def test_get_category_success(mocker: MockFixture):
    # arrange
    test_id = 1
    expected_category = CategorySchema(id=1, name="cat1", is_active=True)
    mock_repository = mocker.MagicMock()
    mock_repository.get_category = mocker.AsyncMock(return_value=expected_category)

    category_service = CategoryService(mock_repository)

    # act
    actual_category = await category_service.get_category(test_id)

    # assert
    assert actual_category == expected_category
    mock_repository.get_category.assert_awaited_once_with(test_id)


@pytest.mark.asyncio
async def test_get_category_non_existent_category(mocker: MockFixture):
    # arrange
    test_id = 1
    mock_repository = mocker.MagicMock()
    mock_repository.get_category = mocker.AsyncMock(return_value=None)

    category_service = CategoryService(mock_repository)

    # act
    with pytest.raises(exceptions.NotFoundError):
        await category_service.get_category(test_id)

    # assert
    mock_repository.get_category.assert_awaited_once_with(test_id)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "expected_categories",
    [
        ([],),
        (
            [
                CategorySchema(id=1, name="cat1", is_active=True, parent_id=None),
            ],
        ),
        (
            [
                CategorySchema(id=1, name="cat1", is_active=True, parent_id=None),
                CategorySchema(id=2, name="cat2", is_active=True, parent_id=1),
            ],
        ),
    ],
)
async def test_get_all_categories_success(
    expected_categories: list[CategorySchema], mocker: MockFixture
):
    # arrange
    mock_repository = mocker.MagicMock()
    mock_repository.get_all_categories = mocker.AsyncMock(
        return_value=expected_categories
    )

    category_service = CategoryService(mock_repository)

    # act
    actual_categories = await category_service.get_all_categories()

    # assert
    assert actual_categories == expected_categories
    mock_repository.get_all_categories.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_category_success(mocker: MockFixture):
    # arrange
    test_id, test_is_active = 2, True
    parent_category = CategorySchema(id=1, name="cat1", parent_id=None, is_active=True)
    category_create = CategoryCreate(name="cat2", parent_id=1)

    def mock_persist(category_create: CategoryCreate) -> CategorySchema:
        return CategorySchema(id=test_id, is_active=test_is_active, **category_create.model_dump())

    mock_repository = mocker.MagicMock()
    mock_repository.get_category = mocker.AsyncMock(return_value=parent_category)
    mock_repository.create_category = mocker.AsyncMock(side_effect=mock_persist)

    category_service = CategoryService(mock_repository)
    
    # act
    actual_category = await category_service.create_category(category_create)

    # assert
    assert actual_category.id == test_id
    assert actual_category.is_active == test_is_active
    assert actual_category.name == category_create.name
    assert actual_category.parent_id == category_create.parent_id
    mock_repository.get_category.assert_awaited_once_with(category_create.parent_id)
    mock_repository.create_category.assert_awaited_once_with(category_create)


@pytest.mark.asyncio
async def test_create_category_root_category(mocker: MockFixture):
    # arrange
    test_id, test_is_active = 2, True
    category_create = CategoryCreate(name="cat2", parent_id=None)

    def mock_persist(category_create: CategoryCreate) -> CategorySchema:
        return CategorySchema(id=test_id, is_active=test_is_active, **category_create.model_dump())

    mock_repository = mocker.MagicMock()
    mock_repository.get_category = mocker.AsyncMock()
    mock_repository.create_category = mocker.AsyncMock(side_effect=mock_persist)

    category_service = CategoryService(mock_repository)
    
    # act
    actual_category = await category_service.create_category(category_create)

    # assert
    assert actual_category.id == test_id
    assert actual_category.is_active == test_is_active
    assert actual_category.name == category_create.name
    assert actual_category.parent_id == category_create.parent_id
    mock_repository.get_category.assert_not_awaited()
    mock_repository.create_category.assert_awaited_once_with(category_create)


@pytest.mark.asyncio
async def test_create_category_no_parent_found(mocker: MockFixture):
    # arrange
    category_create = CategoryCreate(name="cat1", parent_id=1)

    mock_repository = mocker.MagicMock()
    mock_repository.get_category = mocker.AsyncMock(return_value=None)
    mock_repository.create_category = mocker.AsyncMock()

    category_service = CategoryService(mock_repository)
    
    # act
    with pytest.raises(exceptions.NotFoundError):
        await category_service.create_category(category_create)

    # assert
    mock_repository.get_category.assert_awaited_once_with(category_create.parent_id)
    mock_repository.create_category.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_category_success(mocker: MockFixture):
    # arrange
    test_id = 1
    expected_category = CategorySchema(id=test_id, name="cat1", parent_id=None, is_active=True)
    
    mock_repository = mocker.MagicMock()
    mock_repository.get_category = mocker.AsyncMock(return_value=expected_category)
    mock_repository.get_child_categories = mocker.AsyncMock(return_value=[])
    mock_repository.delete_category = mocker.AsyncMock(return_value=expected_category)

    category_service = CategoryService(mock_repository)

    # act
    actual_category = await category_service.delete_category(test_id)

    # assert
    assert actual_category == expected_category
    mock_repository.get_category.assert_awaited_once_with(test_id)
    mock_repository.get_child_categories.assert_awaited_once_with(test_id)
    mock_repository.delete_category.assert_awaited_once_with(test_id)
    

@pytest.mark.asyncio
async def test_delete_category_not_found(mocker: MockFixture):
    # arrange
    test_id = 1
    
    mock_repository = mocker.AsyncMock()
    mock_repository.get_category = mocker.AsyncMock(return_value=None)

    category_service = CategoryService(mock_repository)

    # act
    with pytest.raises(exceptions.NotFoundError):
        await category_service.delete_category(test_id)

    # assert
    mock_repository.get_category.assert_awaited_once_with(test_id)
    mock_repository.get_child_categories.assert_not_awaited()
    mock_repository.delete_category.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_category_children_exist(mocker: MockFixture):
    # arrange
    test_id = 1
    expected_category = CategorySchema(id=test_id, name="cat1", parent_id=None, is_active=True)
    child_category = CategorySchema(id=2, name="cat2", parent_id=test_id, is_active=True)
    
    mock_repository = mocker.MagicMock()
    mock_repository.get_category = mocker.AsyncMock(return_value=expected_category)
    mock_repository.get_child_categories = mocker.AsyncMock(return_value=[child_category])
    mock_repository.delete_category = mocker.AsyncMock()

    category_service = CategoryService(mock_repository)

    # act
    with pytest.raises(exceptions.BadRequestError):
        await category_service.delete_category(test_id)

    # assert
    mock_repository.get_category.assert_awaited_once_with(test_id)
    mock_repository.get_child_categories.assert_awaited_once_with(test_id)
    mock_repository.delete_category.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_category_success(mocker: MockFixture):
    # arrange
    parent_test_id, test_id = 1, 2
    parent_category = CategorySchema(id=parent_test_id, name="cat1", parent_id=None, is_active=True)
    expected_category = CategorySchema(id=test_id, name="cat2", parent_id=parent_test_id, is_active=True)
    category_create = CategoryCreate(name=expected_category.name, parent_id=expected_category.parent_id)

    mock_repository = mocker.MagicMock()
    mock_repository.get_category = mocker.AsyncMock(side_effect=[expected_category, parent_category])
    mock_repository.update_category = mocker.AsyncMock(return_value=expected_category)

    category_service = CategoryService(mock_repository)

    # act
    actual_category = await category_service.update_category(test_id, category_create)

    # assert
    assert actual_category == expected_category
    mock_repository.get_category.assert_has_awaits([call(test_id), call(parent_test_id)])
    mock_repository.update_category.assert_awaited_once_with(test_id, category_create)


@pytest.mark.asyncio
async def test_update_category_parent_not_defined(mocker: MockFixture):
    # arrange
    test_id = 1
    expected_category = CategorySchema(id=test_id, name="cat1", parent_id=None, is_active=True)
    category_create = CategoryCreate(name=expected_category.name, parent_id=expected_category.parent_id)

    mock_repository = mocker.MagicMock()
    mock_repository.get_category = mocker.AsyncMock(return_value=expected_category)
    mock_repository.update_category = mocker.AsyncMock(return_value=expected_category)

    category_service = CategoryService(mock_repository)

    # act
    actual_category = await category_service.update_category(test_id, category_create)

    # assert
    assert actual_category == expected_category
    mock_repository.get_category.assert_awaited_once_with(test_id)
    mock_repository.update_category.assert_awaited_once_with(test_id, category_create)


@pytest.mark.asyncio
async def test_update_category_not_found(mocker: MockFixture):
    # arrange
    test_parent_id, test_id = 1, 2
    category_create = CategoryCreate(name="cat1", parent_id=test_parent_id)

    mock_repository = mocker.MagicMock()
    mock_repository.get_category = mocker.AsyncMock(return_value=None)
    mock_repository.update_category = mocker.AsyncMock()

    category_service = CategoryService(mock_repository)

    # act
    with pytest.raises(exceptions.NotFoundError):
        await category_service.update_category(test_id, category_create)

    # assert
    mock_repository.get_category.assert_awaited_once_with(test_id)
    mock_repository.update_category.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_category_parent_not_found(mocker: MockFixture):
    # arrange
    parent_test_id, test_id = 1, 2
    expected_category = CategorySchema(id=test_id, name="cat2", parent_id=parent_test_id, is_active=True)
    category_create = CategoryCreate(name=expected_category.name, parent_id=expected_category.parent_id)

    mock_repository = mocker.MagicMock()
    mock_repository.get_category = mocker.AsyncMock(side_effect=[expected_category, None])
    mock_repository.update_category = mocker.AsyncMock()

    category_service = CategoryService(mock_repository)

    # act
    with pytest.raises(exceptions.NotFoundError):
        await category_service.update_category(test_id, category_create)

    # assert
    mock_repository.get_category.assert_has_awaits([call(test_id), call(parent_test_id)])
    mock_repository.update_category.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_category_category_is_parent_of_itself(mocker: MockFixture):
    # arrange
    test_id = 1
    expected_category = CategorySchema(id=test_id, name="cat2", parent_id=test_id, is_active=True)
    category_create = CategoryCreate(name=expected_category.name, parent_id=expected_category.parent_id)

    mock_repository = mocker.MagicMock()
    mock_repository.get_category = mocker.AsyncMock(return_value=expected_category)
    mock_repository.update_category = mocker.AsyncMock()

    category_service = CategoryService(mock_repository)

    # act
    with pytest.raises(exceptions.BadRequestError):
        await category_service.update_category(test_id, category_create)

    # assert
    mock_repository.get_category.assert_has_awaits([call(test_id), call(test_id)])
    mock_repository.update_category.assert_not_awaited()
