from typing import List

from fastapi import APIRouter, Depends

from auth.security import get_api_key
from database import get_db_connection
from models.checkout import Order


router = APIRouter()


@router.get("/", response_model=List[Order])
def get_orders(_: str = Depends(get_api_key)):
    with get_db_connection() as conn:
        rows = conn.execute("SELECT * FROM orders ORDER BY created_at DESC").fetchall()
    return [dict(row) for row in rows]
