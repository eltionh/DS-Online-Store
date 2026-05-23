# DS Online Store

DS Online Store is a Python-only full stack project built with the same structure as `lesson31-33`.

It uses:

- FastAPI for the backend API
- Pydantic for data validation
- sqlite3 for the database
- Streamlit for the frontend
- requests for frontend-to-backend API calls
- Python standard library code for reading `.env`

No custom CSS or HTML is used in the Streamlit app.

## Project Structure

- `main.py`: starts the FastAPI app and connects all routers
- `app.py`: Streamlit frontend
- `api_service.py`: frontend helper functions that call the backend API
- `database.py`: SQLite tables, seed data, database helper functions
- `config.py`: reads values from `.env`
- `.env`: local settings such as API URL and API key
- `auth/security.py`: API key protection for admin/write routes
- `models/`: Pydantic models
- `routers/`: FastAPI route files grouped by feature
- `static/product_images/`: downloaded seed product images
- `seed_images.py`: downloads images for seeded products
- `PROJECT_GUIDE.md`: student explanation of the codebase

## Install

Open PowerShell in the project folder:

```powershell
cd C:\Users\Student\Desktop\DS-Online-Store
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install requirements:

```powershell
pip install -r requirements.txt
```

If you do not use the requirements file, install directly:

```powershell
pip install fastapi uvicorn streamlit requests pydantic
```

## Environment File

The project includes `.env`:

```env
DS_STORE_API_URL=http://127.0.0.1:8000/api
DS_STORE_API_KEY=dev-store-key
DS_STORE_INIT_ON_IMPORT=0
```

The app reads this file through `config.py`.

## Seeded Credentials

Admin user:

- Username: `admin`
- Password: `admin123`
- Role: `admin`

Regular user:

- Username: `student`
- Password: `student123`
- Role: `user`

API key:

- `dev-store-key`

## Run The Project

Start the backend API:

```powershell
python -m uvicorn main:app --reload
```

Open another PowerShell terminal in the same folder, then start Streamlit:

```powershell
streamlit run app.py
```

Default URLs:

- Backend API: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs
- Streamlit frontend: http://localhost:8501

If port `8501` is busy, Streamlit may use another port such as `8502`.

## Optional Image Seed

Download product images into `static/product_images`:

```powershell
python seed_images.py
```

## Authorization Rules

- Guest users can only see the Home page.
- Guest users cannot see or click Add to Cart buttons.
- Guest users cannot open Shop, Cart, Analytics, or Admin pages.
- Logged-in regular users can use Home, Shop, and Cart.
- Analytics is admin-only.
- Admin users can use Home, Shop, Cart, Analytics, and Admin.
- Admin/write API routes require the API key from `.env`.

## User Features

- Browse featured products on Home.
- Browse and filter products in Shop after login.
- Add products to cart after login.
- Edit product quantities directly in Cart.
- Remove cart items with item buttons.
- Complete a checkout form with name, email, address, payment method, and notes.

## Admin Features

- Create, edit, and delete products.
- Mark products as featured or remove them from featured products.
- Create categories.
- Create, edit, and delete users.
- View analytics charts and recent orders.
