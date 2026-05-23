from pydantic import BaseModel


class DashboardStats(BaseModel):
    product_count: int
    category_count: int
    inventory_value: float
    average_rating: float
    low_stock_count: int
