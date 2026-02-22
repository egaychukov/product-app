from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.categories import Category as CategoryModel
from app.schemas.categories import Category as CategorySchema, CategoryCreate
from app import exceptions


class CategoryService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_category(self, category_id: int) -> CategorySchema:
        category = await self._get_category_model(category_id)
        
        return CategorySchema.model_validate(category)

    async def get_all_categories(self) -> list[CategorySchema]:
        result = await self.db.scalars(
            select(CategoryModel).where(CategoryModel.is_active)
        )

        return [CategorySchema.model_validate(category) for category in result.all()]

    async def create_category(self, category_create: CategoryCreate) -> CategorySchema:
        if category_create.parent_id is not None:
            await self._get_category_model(category_create.parent_id)

        category = CategoryModel(**category_create.model_dump())
        self.db.add(category)

        await self.db.commit()
        return CategorySchema.model_validate(category)

    async def delete_category(self, category_id: int) -> CategorySchema:
        category = await self._get_category_model(category_id)

        child_categories = await self._get_children_categories(category_id)
        if child_categories:
            raise exceptions.BadRequestError("cannot delete category with children")

        category.is_active = False

        await self.db.commit()
        return CategorySchema.model_validate(category)

    async def update_category(
        self, category_id: int, category_create: CategoryCreate
    ) -> CategorySchema:
        category_to_update = await self._get_category_model(category_id)

        if category_create.parent_id is not None:
            await self._get_category_model(category_create.parent_id)

            if category_create.parent_id == category_id:
                raise exceptions.BadRequestError("category cannot belong to itself")

        await self.db.execute(
            update(CategoryModel)
            .where(CategoryModel.id == category_id)
            .values(**category_create.model_dump(exclude_unset=True))
        )

        await self.db.commit()
        await self.db.refresh(category_to_update)
        return CategorySchema.model_validate(category_to_update)

    async def _get_category_model(self, category_id: int) -> CategoryModel:
        category = await self.db.scalar(
            select(CategoryModel).where(
                CategoryModel.is_active, CategoryModel.id == category_id
            )
        )

        if category is None:
            raise exceptions.NotFoundError("category not found or inactive")

        return category

    async def _get_children_categories(self, category_id: int) -> list[CategoryModel]:
        result = await self.db.scalars(
            select(CategoryModel).where(
                CategoryModel.is_active, CategoryModel.parent_id == category_id
            )
        )

        return list(result.all())
