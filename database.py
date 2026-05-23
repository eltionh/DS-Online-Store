import os
import sqlite3
import urllib.request
from pathlib import Path

from config import get_setting


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "store.db"
STATIC_DIR = BASE_DIR / "static"
PRODUCT_IMAGE_DIR = STATIC_DIR / "product_images"


SEED_CATEGORIES = [
    "Computers",
    "Phones",
    "Accessories",
    "Fitness",
    "Drinks",
    "Audio",
]


SEED_PRODUCTS = [
    {
        "name": "AeroBook Pro 14",
        "category": "Computers",
        "description": "Lightweight laptop with a bright display, long battery life, and fast everyday performance.",
        "price": 1199.0,
        "stock": 18,
        "rating": 4.8,
        "image_url": "https://picsum.photos/seed/aerobook-pro/900/700",
    },
    {
        "name": "Nebula Gaming PC",
        "category": "Computers",
        "description": "RGB desktop tower built for smooth gaming, streaming, and creative projects.",
        "price": 1549.0,
        "stock": 9,
        "rating": 4.7,
        "image_url": "https://picsum.photos/seed/gaming-pc/900/700",
    },
    {
        "name": "PixelWave Phone",
        "category": "Phones",
        "description": "Modern smartphone with a sharp camera, vivid screen, and all-day battery.",
        "price": 799.0,
        "stock": 27,
        "rating": 4.6,
        "image_url": "https://picsum.photos/seed/pixelwave-phone/900/700",
    },
    {
        "name": "QuietBeat Headphones",
        "category": "Audio",
        "description": "Wireless headphones with active noise control and plush travel-ready comfort.",
        "price": 249.0,
        "stock": 34,
        "rating": 4.5,
        "image_url": "https://picsum.photos/seed/headphones/900/700",
    },
    {
        "name": "FlowKeys Mechanical Keyboard",
        "category": "Accessories",
        "description": "Hot-swappable keyboard with tactile switches, clean lighting, and a compact layout.",
        "price": 149.0,
        "stock": 41,
        "rating": 4.4,
        "image_url": "https://picsum.photos/seed/mechanical-keyboard/900/700",
    },
    {
        "name": "StudioView 27 Monitor",
        "category": "Accessories",
        "description": "Color-rich 27-inch monitor for school, design work, gaming, and multitasking.",
        "price": 329.0,
        "stock": 16,
        "rating": 4.3,
        "image_url": "https://picsum.photos/seed/monitor/900/700",
    },
    {
        "name": "FlexForm Dumbbell Set",
        "category": "Fitness",
        "description": "Adjustable home gym dumbbells with a compact stand and quick weight changes.",
        "price": 219.0,
        "stock": 12,
        "rating": 4.2,
        "image_url": "https://picsum.photos/seed/dumbbells/900/700",
    },
    {
        "name": "SparkRush Energy Pack",
        "category": "Drinks",
        "description": "Twelve-pack of sparkling energy drinks with crisp citrus flavor.",
        "price": 24.0,
        "stock": 88,
        "rating": 4.1,
        "image_url": "https://picsum.photos/seed/energy-drink/900/700",
    },
]


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_database():
    PRODUCT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                category_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                price REAL NOT NULL CHECK(price >= 0),
                stock INTEGER NOT NULL DEFAULT 0 CHECK(stock >= 0),
                rating REAL NOT NULL DEFAULT 0 CHECK(rating >= 0 AND rating <= 5),
                image_url TEXT NOT NULL,
                featured INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'user'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                subtotal REAL NOT NULL,
                tax REAL NOT NULL,
                total REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
            """
        )

        for category in SEED_CATEGORIES:
            conn.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))

        product_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if product_count == 0:
            category_ids = {
                row["name"]: row["id"]
                for row in conn.execute("SELECT id, name FROM categories").fetchall()
            }
            for index, product in enumerate(SEED_PRODUCTS):
                conn.execute(
                    """
                    INSERT INTO products
                        (name, category_id, description, price, stock, rating, image_url, featured)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        product["name"],
                        category_ids[product["category"]],
                        product["description"],
                        product["price"],
                        product["stock"],
                        product["rating"],
                        product["image_url"],
                        1 if index < 4 else 0,
                    ),
                )

        conn.execute(
            "INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')"
        )
        conn.execute(
            "INSERT OR IGNORE INTO users (username, password, role) VALUES ('student', 'student123', 'user')"
        )
        conn.commit()


def row_to_product(row):
    return {
        "id": row["id"],
        "name": row["name"],
        "category_id": row["category_id"],
        "category": row["category"],
        "description": row["description"],
        "price": row["price"],
        "stock": row["stock"],
        "rating": row["rating"],
        "image_url": row["image_url"],
        "featured": bool(row["featured"]),
    }


def calculate_checkout(items):
    subtotal = sum(item["unit_price"] * item["quantity"] for item in items)
    tax = round(subtotal * 0.0825, 2)
    total = round(subtotal + tax, 2)
    return {"subtotal": round(subtotal, 2), "tax": tax, "total": total}


def local_image_url(filename):
    return f"/static/product_images/{filename}"


def download_seed_images():
    create_database()
    with get_db_connection() as conn:
        rows = conn.execute("SELECT id, name, image_url FROM products").fetchall()
        for row in rows:
            if row["image_url"].startswith("/static/"):
                continue
            filename = "".join(char.lower() if char.isalnum() else "-" for char in row["name"]).strip("-")
            filename = f"{filename}.jpg"
            target = PRODUCT_IMAGE_DIR / filename
            try:
                urllib.request.urlretrieve(row["image_url"], target)
            except Exception:
                continue
            conn.execute(
                "UPDATE products SET image_url = ? WHERE id = ?",
                (local_image_url(filename), row["id"]),
            )
        conn.commit()


if get_setting("DS_STORE_INIT_ON_IMPORT", "0") == "1":
    create_database()
