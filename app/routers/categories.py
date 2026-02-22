from typing import Annotated

from fastapi import APIRouter, status, Depends

from app.enums import Role
from app.auth import get_current_role
from app.db_depends import get_category_service
from app.schemas.categories import Category as CategorySchema, CategoryCreate
from app.services.categories import CategoryService


router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/")
async def get_all_categories(
    category_service: Annotated[CategoryService, Depends(get_category_service)],
) -> list[CategorySchema]:
    """
    Get all active categories.

    Returns:
        A list of CategorySchema objects representing the categories.
    """
    return await category_service.get_all_categories()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_role(Role.ADMIN))],
)
async def create_category(
    category_create: CategoryCreate,
    category_service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategorySchema:
    """
    Create a new category.

    Args:
        category_create: CategoryCreate object containing the category data.

    Returns:
        A CategorySchema object representing the created category.

    Raises:
        HTTP 403: If the user is not an admin.
        HTTP 404: If the parent category is not found.
        HTTP 422: If the category data is invalid.
    """
    created_category = await category_service.create_category(category_create)

    return created_category


@router.delete(
    "/{category_id}",
    dependencies=[Depends(get_current_role(Role.ADMIN))],
)
async def delete_category(
    category_id: int,
    category_service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategorySchema:
    """
    Soft-delete a category.

    Args:
        category_id: ID of the category to delete.

    Returns:
        A CategorySchema representing the soft-deleted category.

    Raises:
        HTTP 400: If the category has children.
        HTTP 403: If the user is not an admin.
        HTTP 404: If the category is not found or is inactive.
    """
    deleted_category = await category_service.delete_category(category_id)

    return deleted_category


@router.put(
    "/{category_id}",
    dependencies=[Depends(get_current_role(Role.ADMIN))],
)
async def update_category(
    category_id: int,
    category_create: CategoryCreate,
    category_service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategorySchema:
    """
    Update a category.

    Args:
        category_id: ID of the category to update.
        category_create: CategoryCreate object containing the category data.

    Returns:
        A CategorySchema object representing the updated category.

    Raises:
        HTTP 400: If the category is set as its own parent.
        HTTP 403: If the user is not an admin.
        HTTP 404: If the category or the new parent category are missing/inactive.
        HTTP 422: If the category data is invalid.
    """
    updated_category = await category_service.update_category(
        category_id, category_create
    )

    return updated_category
