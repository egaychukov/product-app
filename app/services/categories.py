from app import exceptions
from app.repository.categories import CategoryRepository
from app.schemas.categories import Category as CategorySchema, CategoryCreate


class CategoryService:
    def __init__(
        self, category_repository: CategoryRepository
    ) -> None:
        self.category_repository = category_repository

    async def get_category(self, category_id: int) -> CategorySchema:
        category = await self.category_repository.get_category(category_id)

        if category is None:
            raise exceptions.NotFoundError("category not found or inactive")

        return category

    async def get_all_categories(self) -> list[CategorySchema]:
        return await self.category_repository.get_all_categories()

    async def create_category(self, category_create: CategoryCreate) -> CategorySchema:
        if category_create.parent_id is not None:
            await self.get_category(category_create.parent_id)

        return await self.category_repository.create_category(category_create)

    async def delete_category(self, category_id: int) -> CategorySchema:
        await self.get_category(category_id)

        child_categories = await self.category_repository.get_child_categories(
            category_id
        )
        if child_categories:
            raise exceptions.BadRequestError("cannot delete category with children")

        return await self.category_repository.delete_category(category_id)

    async def update_category(
        self, category_id: int, category_create: CategoryCreate
    ) -> CategorySchema:
        await self.get_category(category_id)

        if category_create.parent_id is not None:
            await self.get_category(category_create.parent_id)

            if category_create.parent_id == category_id:
                raise exceptions.BadRequestError("category cannot belong to itself")

        return await self.category_repository.update_category(
            category_id, category_create
        )
