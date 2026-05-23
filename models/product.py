from typing import Optional

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    category_id: int
    description: str = Field(min_length=5, max_length=500)
    price: float = Field(ge=0)
    stock: int = Field(ge=0)
    rating: float = Field(ge=0, le=5)
    image_url: str
    featured: bool = False


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int
    category: str


class ProductFilters(BaseModel):
    search: Optional[str] = None
    category_id: Optional[int] = None
    min_price: Optional[float] = Field(default=None, ge=0)
    max_price: Optional[float] = Field(default=None, ge=0)
    min_rating: Optional[float] = Field(default=None, ge=0, le=5)
    in_stock: bool = False
