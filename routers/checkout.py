from fastapi import APIRouter, Depends, HTTPException, Query

from auth.security import get_api_key
from database import calculate_checkout, get_db_connection
from models.checkout import CheckoutRequest, CheckoutSummary, Order


router = APIRouter()


@router.post("/", response_model=Order)
def checkout(request: CheckoutRequest, _: str = Depends(get_api_key)):
    if not request.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    with get_db_connection() as conn:
        priced_items = []
        for item in request.items:
            row = conn.execute(
                "SELECT id, price, stock FROM products WHERE id = ?",
                (item.product_id,),
            ).fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
            if row["stock"] < item.quantity:
                raise HTTPException(status_code=400, detail=f"Product {item.product_id} is low on stock")
            priced_items.append(
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": row["price"],
                }
            )

        totals = calculate_checkout(priced_items)
        cursor = conn.execute(
            "INSERT INTO orders (customer_name, subtotal, tax, total) VALUES (?, ?, ?, ?)",
            (request.customer_name, totals["subtotal"], totals["tax"], totals["total"]),
        )
        order_id = cursor.lastrowid

        for item in priced_items:
            conn.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                (order_id, item["product_id"], item["quantity"], item["unit_price"]),
            )
            conn.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ?",
                (item["quantity"], item["product_id"]),
            )
        conn.commit()
        row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    return dict(row)


@router.get("/preview", response_model=CheckoutSummary)
def checkout_preview(product_id: int, quantity: int = Query(default=1, ge=1)):
    with get_db_connection() as conn:
        row = conn.execute("SELECT price FROM products WHERE id = ?", (product_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return calculate_checkout([{"unit_price": row["price"], "quantity": quantity}])
