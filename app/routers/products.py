from typing import Annotated

from fastapi import APIRouter, status, Depends, Query

from app.enums import Role
from app.db_depends import get_product_service
from app.schemas.products import Product as ProductSchema, ProductCreate
from app.schemas.users import User as UserSchema
from app.schemas.reviews import Review as ReviewSchema
from app.auth import get_current_role
from app.services.products import ProductService
from app.schemas.pagination import Page


router = APIRouter(prefix="/products", tags=["products"])


@router.get("/")
async def get_products(
    product_service: Annotated[ProductService, Depends(get_product_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> Page[ProductSchema]:
    """
    Get a page of active products defined by the pagination parameters.

    Args:
        page: Number (not index) of the requested page.
        page_size: Length of the requested page.

    Returns:
        A page of ProductSchema objects representing active products.
    """
    return await product_service.get_products(page, page_size)


@router.get("/{product_id}")
async def get_product(
    product_id: int,
    product_service: Annotated[ProductService, Depends(get_product_service)],
) -> ProductSchema:
    """
    Get a product by its ID.

    Args:
        product_id: ID of the product to get.

    Returns:
        A ProductSchema object representing the product.

    Raises:
        HTTP 404: If the product is not found or inactive.
    """
    return await product_service.get_product(product_id)


@router.get("/category/{category_id}")
async def get_category_products(
    category_id: int,
    product_service: Annotated[ProductService, Depends(get_product_service)],
) -> list[ProductSchema]:
    """
    Get active products of the category specified.

    Args:
        category_id: ID of the category whose products are listed.

    Returns:
        A list of ProductSchema objects representing products of the category.

    Raises:
        HTTP 404: If the category is not found or inactive.
    """
    return await product_service.get_category_products(category_id)


@router.get("/{product_id}/reviews")
async def get_product_reviews(
    product_id: int,
    product_service: Annotated[ProductService, Depends(get_product_service)],
) -> list[ReviewSchema]:
    """
    Get reviews of a product.

    Args:
        product_id: ID of the product whose reviews are fetched.

    Returns:
        A list of ReviewSchema objects representing reviews of the product.

    Raises:
        HTTP 404: If the product is not found or inactive.
    """
    return await product_service.get_product_reviews(product_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(
    product_create: ProductCreate,
    product_service: Annotated[ProductService, Depends(get_product_service)],
    current_seller: Annotated[UserSchema, Depends(get_current_role(Role.SELLER))],
) -> ProductSchema:
    """
    Create a new product.

    Args:
        product_create: ProductCreate object containing new product data.
        current_seller: User data of the seller creating the product.

    Returns:
        A ProductSchema object representing the new product.

    Raises:
        HTTP 403: If the user is not a seller.
        HTTP 404: If the category is not found or inactive.
        HTTP 422: If the product data is invalid.
    """
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
    """
    Soft-delete a product.

    Args:
        product_id: ID of the product to delete.
        current_seller: User data of the user deleting the product.

    Returns:
        A ProductSchema object representing the soft-deleted product.

    Raises:
        HTTP 403: If the user is not a seller or not the product owner.
        HTTP 404: If the product is not found or inactive.
    """
    deleted_product = await product_service.delete_product(product_id, current_seller)

    return deleted_product


@router.put("/{product_id}")
async def update_product(
    product_id: int,
    product_create: ProductCreate,
    product_service: Annotated[ProductService, Depends(get_product_service)],
    current_seller: Annotated[UserSchema, Depends(get_current_role(Role.SELLER))],
) -> ProductSchema:
    """
    Update a product.

    Args:
        product_id: ID of the product to update.
        product_create: ProductCreate object containing new product data.
        current_seller: User data of the seller updating the product.

    Returns:
        A ProductSchema object representing the updated product state.

    Raises:
        HTTP 403: If the user is not a seller or not the product owner.
        HTTP 404: If the product or the new category are not found or inactive.
        HTTP 422: If the product data is invalid.
    """
    updated_product = await product_service.update_product(
        product_id, product_create, current_seller
    )

    return updated_product
