from fastapi import APIRouter

from database import get_db_connection
from models.stats import DashboardStats


router = APIRouter()


@router.get("/", response_model=DashboardStats)
def get_stats():
    with get_db_connection() as conn:
        row = conn.execute(
            """
            SELECT
                COUNT(*) AS product_count,
                COUNT(DISTINCT category_id) AS category_count,
                COALESCE(SUM(price * stock), 0) AS inventory_value,
                COALESCE(AVG(rating), 0) AS average_rating,
                SUM(CASE WHEN stock <= 10 THEN 1 ELSE 0 END) AS low_stock_count
            FROM products
            """
        ).fetchone()
    return dict(row)
