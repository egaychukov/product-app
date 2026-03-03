from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.categories import Category as CategoryModel
from app.schemas.categories import Category as CategorySchema, CategoryCreate


class CategoryRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_category(self, category_id: int) -> CategorySchema | None:
        category = await self._get_model(category_id)

        return CategorySchema.model_validate(category) if category else None 

    async def get_all_categories(self) -> list[CategorySchema]:
        result = await self.db.scalars(
            select(CategoryModel).where(CategoryModel.is_active)
        )

        return [CategorySchema.model_validate(category) for category in result.all()]

    async def create_category(self, category_create: CategoryCreate) -> CategorySchema:
        category = CategoryModel(**category_create.model_dump())
        self.db.add(category)

        await self.db.commit()
        await self.db.refresh(category)
        return CategorySchema.model_validate(category)
    
    async def get_child_categories(self, category_id: int) -> list[CategorySchema]:
        result = await self.db.scalars(
            select(CategoryModel).where(
                CategoryModel.is_active, CategoryModel.parent_id == category_id
            )
        )

        return [CategorySchema.model_validate(category) for category in result.all()]

    async def delete_category(self, category_id: int) -> CategorySchema | None:
        category = await self._get_model(category_id)
        if category is None:
            return None
        
        category.is_active = False

        await self.db.commit()
        return CategorySchema.model_validate(category)

    async def update_category(self, category_id: int, category_create: CategoryCreate) -> CategorySchema | None:
        category = await self._get_model(category_id)
        if category is None:
            return None

        await self.db.execute(
            update(CategoryModel)
            .where(CategoryModel.id == category_id)
            .values(**category_create.model_dump(exclude_unset=True))
        )

        await self.db.commit()
        await self.db.refresh(category)
        return CategorySchema.model_validate(category)

    async def _get_model(self, category_id: int) -> CategoryModel | None:
        return await self.db.scalar(
            select(CategoryModel).where(
                CategoryModel.is_active, CategoryModel.id == category_id
            )
        )
