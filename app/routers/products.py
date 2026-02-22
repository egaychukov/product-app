from typing import Annotated

from fastapi import APIRouter, status, Depends

from app.enums import Role
from app.db_depends import get_product_service
from app.schemas.products import Product as ProductSchema, ProductCreate
from app.schemas.users import User as UserSchema
from app.schemas.reviews import Review as ReviewSchema
from app.auth import get_current_role
from app.services.products import ProductService


router = APIRouter(prefix="/products", tags=["products"])


@router.get("/")
async def get_all_products(
    product_service: Annotated[ProductService, Depends(get_product_service)],
) -> list[ProductSchema]:
    return await product_service.get_all_products()


@router.get("/{product_id}")
async def get_product(
    product_id: int,
    product_service: Annotated[ProductService, Depends(get_product_service)],
) -> ProductSchema:
    return await product_service.get_product(product_id)


@router.get("/category/{category_id}")
async def get_category_products(
    category_id: int,
    product_service: Annotated[ProductService, Depends(get_product_service)],
) -> list[ProductSchema]:
    return await product_service.get_category_products(category_id)


@router.get("/{product_id}/reviews")
async def get_product_reviews(
    product_id: int,
    product_service: Annotated[ProductService, Depends(get_product_service)],
) -> list[ReviewSchema]:
    return await product_service.get_product_reviews(product_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(
    product_create: ProductCreate,
    product_service: Annotated[ProductService, Depends(get_product_service)],
    current_seller: Annotated[UserSchema, Depends(get_current_role(Role.SELLER))],
) -> ProductSchema:
    created_product = await product_service.create_product(
        product_create, current_seller
    )

    return created_product


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    product_service: Annotated[ProductService, Depends(get_product_service)],
    current_seller: Annotated[UserSchema, Depends(get_current_role(Role.SELLER))],
) -> ProductSchema:
    deleted_product = await product_service.delete_product(product_id, current_seller)

    return deleted_product


@router.put("/{product_id}")
async def update_product(
    product_id: int,
    product_create: ProductCreate,
    product_service: Annotated[ProductService, Depends(get_product_service)],
    current_seller: Annotated[UserSchema, Depends(get_current_role(Role.SELLER))],
) -> ProductSchema:
    updated_product = await product_service.update_product(
        product_id, product_create, current_seller
    )

    return updated_product
