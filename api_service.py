import requests

from config import get_setting


BASE_URL = get_setting("DS_STORE_API_URL", "http://127.0.0.1:8000/api")
API_KEY = get_setting("DS_STORE_API_KEY", "dev-store-key")


def _headers(api_key=None):
    return {"api-key": api_key or API_KEY}


def _handle(response):
    if response.ok:
        return response.json()
    try:
        detail = response.json().get("detail", response.text)
    except ValueError:
        detail = response.text
    raise RuntimeError(detail)


def get_categories():
    return _handle(requests.get(f"{BASE_URL}/categories/", timeout=10))


def create_category(name, api_key=None):
    return _handle(
        requests.post(
            f"{BASE_URL}/categories/",
            json={"name": name},
            headers=_headers(api_key),
            timeout=10,
        )
    )


def get_products(filters=None):
    return _handle(requests.get(f"{BASE_URL}/products/", params=filters or {}, timeout=10))


def get_featured_products():
    return _handle(requests.get(f"{BASE_URL}/products/featured", timeout=10))


def create_product(product, api_key=None):
    return _handle(
        requests.post(
            f"{BASE_URL}/products/",
            json=product,
            headers=_headers(api_key),
            timeout=10,
        )
    )


def update_product(product_id, product, api_key=None):
    return _handle(
        requests.put(
            f"{BASE_URL}/products/{product_id}",
            json=product,
            headers=_headers(api_key),
            timeout=10,
        )
    )


def delete_product(product_id, api_key=None):
    return _handle(
        requests.delete(
            f"{BASE_URL}/products/{product_id}",
            headers=_headers(api_key),
            timeout=10,
        )
    )


def login(username, password):
    return _handle(
        requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": username, "password": password},
            timeout=10,
        )
    )


def register(username, password):
    return _handle(
        requests.post(
            f"{BASE_URL}/auth/register",
            json={"username": username, "password": password},
            timeout=10,
        )
    )


def checkout(customer_name, items):
    return _handle(
        requests.post(
            f"{BASE_URL}/checkout/",
            json={"customer_name": customer_name, "items": items},
            headers=_headers(),
            timeout=10,
        )
    )


def get_orders(api_key=None):
    return _handle(requests.get(f"{BASE_URL}/orders/", headers=_headers(api_key), timeout=10))


def get_stats():
    return _handle(requests.get(f"{BASE_URL}/stats/", timeout=10))


def get_users(api_key=None):
    return _handle(requests.get(f"{BASE_URL}/users/", headers=_headers(api_key), timeout=10))


def create_user(user, api_key=None):
    return _handle(
        requests.post(
            f"{BASE_URL}/users/",
            json=user,
            headers=_headers(api_key),
            timeout=10,
        )
    )


def update_user(user_id, user, api_key=None):
    return _handle(
        requests.put(
            f"{BASE_URL}/users/{user_id}",
            json=user,
            headers=_headers(api_key),
            timeout=10,
        )
    )


def delete_user(user_id, api_key=None):
    return _handle(
        requests.delete(
            f"{BASE_URL}/users/{user_id}",
            headers=_headers(api_key),
            timeout=10,
        )
    )
