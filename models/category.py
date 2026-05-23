from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(min_length=2, max_length=60)


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int
