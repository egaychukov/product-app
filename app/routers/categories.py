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
    updated_category = await category_service.update_category(
        category_id, category_create
    )

    return updated_category
