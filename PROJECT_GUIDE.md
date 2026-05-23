# DS Online Store Project Guide

This guide explains the project in student-friendly language.

## Big Picture

This project has two apps that work together:

1. The backend is `main.py`. It uses FastAPI to create API endpoints.
2. The frontend is `app.py`. It uses Streamlit to show pages, buttons, forms, tables, and charts.

The frontend does not talk to the database directly. It calls the backend through `api_service.py`.

The backend talks to the SQLite database through `database.py`.

## Request Flow

Example: clicking Add to Cart after logging in.

1. Streamlit shows products in `app.py`.
2. The logged-in user clicks Add to Cart.
3. `app.py` stores the product ID and quantity in `st.session_state.cart`.
4. When the user checks out, `app.py` calls `api_service.checkout()`.
5. `api_service.py` sends a POST request to FastAPI.
6. FastAPI receives the request in `routers/checkout.py`.
7. Pydantic checks the request shape using `models/checkout.py`.
8. The checkout router reads product prices from SQLite.
9. The order is saved in `store.db`.
10. The frontend shows a success message.

## `.env`

The `.env` file stores local settings:

- `DS_STORE_API_URL`: where the frontend should send API requests
- `DS_STORE_API_KEY`: secret key for protected API routes
- `DS_STORE_INIT_ON_IMPORT`: optional database initialization flag

The project does not use `python-dotenv`. Instead, `config.py` reads `.env` with normal Python file code.

## `config.py`

`config.py` has two main functions:

- `load_env()`: reads `.env` and puts values into `os.environ`
- `get_setting()`: gets one setting by name

This lets files like `api_service.py` and `auth/security.py` use the same settings.

## `main.py`

`main.py` creates the FastAPI app.

Important parts:

- `app = FastAPI(...)` creates the backend application.
- `app.mount("/static", ...)` allows product images to be served.
- `app.include_router(...)` connects route files from the `routers/` folder.
- `startup()` runs `create_database()` when the API starts.

This matches the lesson style where `main.py` stays small and routers hold most API logic.

## `database.py`

`database.py` handles SQLite.

Important parts:

- `get_db_connection()` opens a SQLite connection.
- `create_database()` creates tables if they do not exist.
- Seed categories, products, and users are inserted here.
- `row_to_product()` converts a SQLite row into a dictionary for the API.
- `calculate_checkout()` calculates subtotal, tax, and total.
- `download_seed_images()` downloads product images.

Tables created:

- `categories`
- `products`
- `users`
- `orders`
- `order_items`

Seeded users:

- `admin` / `admin123`
- `student` / `student123`

## `auth/security.py`

This file protects admin/write API routes.

It reads the API key from `.env`.

If a request does not send the correct `api-key` header, FastAPI returns an unauthorized error.

Protected actions include:

- creating categories
- creating products
- updating products
- deleting products
- viewing users
- viewing orders

## `models/`

The `models/` folder contains Pydantic classes.

Pydantic models describe what data should look like.

Examples:

- `models/product.py`: product data such as name, price, stock, rating
- `models/category.py`: category data
- `models/user.py`: login and user data
- `models/checkout.py`: cart item and order data
- `models/stats.py`: dashboard statistics

Why Pydantic matters:

- It validates incoming API data.
- It documents API responses.
- It makes FastAPI docs easier to understand.

## `routers/`

The `routers/` folder contains API endpoints.

Each router focuses on one feature.

- `routers/products.py`: product list, featured products, create, update, delete
- `routers/categories.py`: category list and create
- `routers/users.py`: register, login, and admin user list
- `routers/checkout.py`: checkout and checkout preview
- `routers/orders.py`: admin order history
- `routers/stats.py`: dashboard numbers
- `routers/api_key.py`: check whether an API key is valid

This structure keeps the project organized as it grows.

## `api_service.py`

This file belongs to the frontend side.

Streamlit should not contain long `requests.get()` or `requests.post()` code everywhere.

Instead, `app.py` calls helper functions:

- `get_products()`
- `get_categories()`
- `login()`
- `register()`
- `checkout()`
- `get_stats()`

Each helper sends an HTTP request to the FastAPI backend.

## `app.py`

`app.py` is the Streamlit website.

It uses only Streamlit components, not custom HTML or CSS.

Main parts:

- `init_session()`: creates session values such as username, role, and cart
- `api_ready()`: checks if the backend is running
- `sidebar_auth()`: login, register, and logout controls
- `home_page()`: public home page
- `shop_page()`: product browsing for logged-in users
- `cart_page()`: cart and checkout for logged-in users
- `analytics_page()`: charts for logged-in users
- `admin_page()`: admin tools for admin users only
- `navigation_options()`: decides which pages each role can see

Authorization in Streamlit:

- Guests only see Home.
- Guests do not see Add to Cart buttons.
- Regular users see Home, Shop, and Cart.
- Admin users see Home, Shop, Cart, Analytics, and Admin.
- Analytics is admin-only.

The Cart page uses product cards instead of only a table. Each cart item has:

- a quantity input
- a line total
- a remove button

The checkout area is a form. The user fills in:

- full name
- email
- shipping address
- payment method
- optional notes

The backend currently stores the order totals and customer name. The other checkout fields are collected by the frontend to practice building complete forms.

## Admin CRUD

The Admin page is for admin users only.

CRUD means:

- Create
- Read
- Update
- Delete

Admin product tools:

- create a product
- edit product name, category, description, price, stock, rating, image URL, and featured status
- delete a product
- view the inventory table

Admin featured tools:

- make any product featured
- remove a product from featured

Admin user tools:

- create a user
- edit username, password, and role
- delete a user
- view all users

The API protects user and product write routes with the API key from `.env`.

## `seed_images.py`

This script runs `download_seed_images()` from `database.py`.

It downloads product images and updates the database to use local image paths.

Run it with:

```powershell
python seed_images.py
```

## How To Study This Project

Start with this order:

1. Read `main.py` to see how FastAPI starts.
2. Read `database.py` to understand the tables.
3. Read one model file, such as `models/product.py`.
4. Read one router file, such as `routers/products.py`.
5. Read `api_service.py` to see how Streamlit calls FastAPI.
6. Read `app.py` to see how pages are shown to users.

The most important idea:

The frontend asks for data. The backend validates the request. The backend reads or writes SQLite. Then the backend sends a response back to the frontend.
