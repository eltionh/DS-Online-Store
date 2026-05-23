import sqlite3
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from auth.security import get_api_key
from database import get_db_connection, row_to_product
from models.product import Product, ProductCreate


router = APIRouter()


def product_query(
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    in_stock: bool = False,
    featured: Optional[bool] = None,
):
    clauses = []
    params = []

    if search:
        clauses.append("(p.name LIKE ? OR p.description LIKE ?)")
        search_value = f"%{search}%"
        params.extend([search_value, search_value])
    if category_id:
        clauses.append("p.category_id = ?")
        params.append(category_id)
    if min_price is not None:
        clauses.append("p.price >= ?")
        params.append(min_price)
    if max_price is not None:
        clauses.append("p.price <= ?")
        params.append(max_price)
    if min_rating is not None:
        clauses.append("p.rating >= ?")
        params.append(min_rating)
    if in_stock:
        clauses.append("p.stock > 0")
    if featured is not None:
        clauses.append("p.featured = ?")
        params.append(1 if featured else 0)

    sql = """
        SELECT p.id, p.name, p.category_id, c.name AS category, p.description,
               p.price, p.stock, p.rating, p.image_url, p.featured
        FROM products p
        JOIN categories c ON c.id = p.category_id
    """
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY p.featured DESC, p.rating DESC, p.name"
    return sql, params


@router.get("/", response_model=List[Product])
def get_products(
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    min_price: Optional[float] = Query(default=None, ge=0),
    max_price: Optional[float] = Query(default=None, ge=0),
    min_rating: Optional[float] = Query(default=None, ge=0, le=5),
    in_stock: bool = False,
):
    sql, params = product_query(search, category_id, min_price, max_price, min_rating, in_stock)
    with get_db_connection() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [row_to_product(row) for row in rows]


@router.get("/featured", response_model=List[Product])
def get_featured_products():
    sql, params = product_query(featured=True)
    with get_db_connection() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [row_to_product(row) for row in rows]


@router.post("/", response_model=Product)
def create_product(product: ProductCreate, _: str = Depends(get_api_key)):
    with get_db_connection() as conn:
        category = conn.execute("SELECT id FROM categories WHERE id = ?", (product.category_id,)).fetchone()
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        try:
            cursor = conn.execute(
                """
                INSERT INTO products
                    (name, category_id, description, price, stock, rating, image_url, featured)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    product.name,
                    product.category_id,
                    product.description,
                    product.price,
                    product.stock,
                    product.rating,
                    product.image_url,
                    1 if product.featured else 0,
                ),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail="Product already exists")
        row = conn.execute(
            """
            SELECT p.id, p.name, p.category_id, c.name AS category, p.description,
                   p.price, p.stock, p.rating, p.image_url, p.featured
            FROM products p
            JOIN categories c ON c.id = p.category_id
            WHERE p.id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()
    return row_to_product(row)


@router.put("/{product_id}", response_model=Product)
def update_product(product_id: int, product: ProductCreate, _: str = Depends(get_api_key)):
    with get_db_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE products
            SET name = ?, category_id = ?, description = ?, price = ?, stock = ?,
                rating = ?, image_url = ?, featured = ?
            WHERE id = ?
            """,
            (
                product.name,
                product.category_id,
                product.description,
                product.price,
                product.stock,
                product.rating,
                product.image_url,
                1 if product.featured else 0,
                product_id,
            ),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        conn.commit()
        row = conn.execute(
            """
            SELECT p.id, p.name, p.category_id, c.name AS category, p.description,
                   p.price, p.stock, p.rating, p.image_url, p.featured
            FROM products p
            JOIN categories c ON c.id = p.category_id
            WHERE p.id = ?
            """,
            (product_id,),
        ).fetchone()
    return row_to_product(row)


@router.delete("/{product_id}")
def delete_product(product_id: int, _: str = Depends(get_api_key)):
    with get_db_connection() as conn:
        cursor = conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        conn.commit()
    return {"detail": "Product deleted"}
