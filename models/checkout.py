from typing import List

from pydantic import BaseModel, Field


class CartItem(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, le=99)


class CheckoutRequest(BaseModel):
    customer_name: str = Field(min_length=2, max_length=80)
    items: List[CartItem]


class CheckoutSummary(BaseModel):
    subtotal: float
    tax: float
    total: float


class Order(CheckoutSummary):
    id: int
    customer_name: str
    created_at: str
