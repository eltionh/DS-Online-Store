import sqlite3
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from auth.security import get_api_key
from database import get_db_connection
from models.category import Category, CategoryCreate


router = APIRouter()


@router.get("/", response_model=List[Category])
def get_categories():
    with get_db_connection() as conn:
        rows = conn.execute("SELECT id, name FROM categories ORDER BY name").fetchall()
    return [dict(row) for row in rows]


@router.post("/", response_model=Category)
def create_category(category: CategoryCreate, _: str = Depends(get_api_key)):
    with get_db_connection() as conn:
        try:
            cursor = conn.execute("INSERT INTO categories (name) VALUES (?)", (category.name,))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail="Category already exists")
    return Category(id=cursor.lastrowid, name=category.name)
