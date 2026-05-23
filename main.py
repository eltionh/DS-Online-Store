from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database import create_database
from routers import api_key, categories, checkout, orders, products, stats, users


app = FastAPI(
    title="DS Online Store API",
    description="A Python-only store API using FastAPI, Pydantic, and sqlite3.",
    version="2.0.0",
)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(checkout.router, prefix="/api/checkout", tags=["Checkout"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(stats.router, prefix="/api/stats", tags=["Stats"])
app.include_router(api_key.router, prefix="/api/validate_key", tags=["API Key"])
app.include_router(users.router, prefix="/api", tags=["Users"])


@app.on_event("startup")
def startup():
    create_database()


@app.get("/")
def health_check():
    return {"message": "DS Online Store API is running"}
