import streamlit as st

import api_service
from config import get_setting


st.set_page_config(page_title="DS Online Store", layout="wide")


def init_session():
    defaults = {
        "username": None,
        "role": None,
        "cart": {},
        "api_key": get_setting("DS_STORE_API_KEY", "dev-store-key"),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def api_ready():
    try:
        api_service.get_stats()
        return True
    except Exception as exc:
        st.error(
            "The FastAPI backend is not reachable. Start it with: "
            "`python -m uvicorn main:app --reload`"
        )
        st.caption(str(exc))
        return False


def normalize_image(image_url):
    if image_url.startswith("/"):
        return api_service.BASE_URL.replace("/api", "") + image_url
    return image_url


def add_to_cart(product_id, quantity=1):
    if not st.session_state.username:
        st.warning("Please log in or create an account before adding items to the cart.")
        return
    cart = st.session_state.cart
    cart[str(product_id)] = cart.get(str(product_id), 0) + quantity
    st.session_state.cart = cart


def update_cart_quantity(product_id, quantity):
    cart = st.session_state.cart
    if quantity <= 0:
        cart.pop(str(product_id), None)
    else:
        cart[str(product_id)] = quantity
    st.session_state.cart = cart


def remove_from_cart(product_id):
    cart = st.session_state.cart
    cart.pop(str(product_id), None)
    st.session_state.cart = cart


def sidebar_auth():
    with st.sidebar:
        st.title("DS Online Store")
        if st.session_state.username:
            st.write(f"Signed in as **{st.session_state.username}**")
            st.caption(st.session_state.role.upper())
            if st.button("Log out", use_container_width=True):
                st.session_state.username = None
                st.session_state.role = None
                st.session_state.cart = {}
                st.rerun()
        else:
            auth_tab, register_tab = st.tabs(["Login", "Register"])
            with auth_tab:
                username = st.text_input("Username", key="login_user")
                password = st.text_input("Password", type="password", key="login_pass")
                if st.button("Sign in", use_container_width=True):
                    try:
                        user = api_service.login(username, password)
                        st.session_state.username = user["username"]
                        st.session_state.role = user["role"]
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
            with register_tab:
                username = st.text_input("New username", key="register_user")
                password = st.text_input("New password", type="password", key="register_pass")
                if st.button("Create account", use_container_width=True):
                    try:
                        user = api_service.register(username, password)
                        st.session_state.username = user["username"]
                        st.session_state.role = user["role"]
                        st.success("Account created.")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))


def hero(products):
    st.title("DS Online Store")
    st.caption("FastAPI backend, SQLite seed data, Pydantic validation, and a Streamlit storefront.")
    if products:
        lead = products[0]
        image_col, text_col = st.columns([1.1, 1])
        with image_col:
            st.image(normalize_image(lead["image_url"]), use_container_width=True)
        with text_col:
            st.subheader(lead["name"])
            st.write(lead["description"])
            st.metric("Price", f"${lead['price']:,.2f}")
            st.write(f"{lead['category']} | {lead['rating']:.1f} stars | {lead['stock']} in stock")
            if st.session_state.username and st.button("Add featured item", type="primary"):
                add_to_cart(lead["id"])
                st.toast(f"Added {lead['name']}")
            elif not st.session_state.username:
                st.info("Log in or sign up to shop and add products to your cart.")


def home_page():
    stats = api_service.get_stats()
    featured = api_service.get_featured_products()
    hero(featured)

    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Products", stats["product_count"])
    c2.metric("Categories", stats["category_count"])
    c3.metric("Inventory Value", f"${stats['inventory_value']:,.0f}")
    c4.metric("Average Rating", f"{stats['average_rating']:.1f}")

    st.subheader("Featured Products")
    render_product_grid(featured, allow_cart=bool(st.session_state.username))


def filters(categories):
    with st.sidebar:
        st.divider()
        st.subheader("Shop Filters")
        search = st.text_input("Search")
        category_names = ["All"] + [category["name"] for category in categories]
        selected_category = st.selectbox("Category", category_names)
        min_price, max_price = st.slider("Price range", 0, 1800, (0, 1800), step=25)
        min_rating = st.slider("Minimum rating", 0.0, 5.0, 0.0, step=0.1)
        in_stock = st.checkbox("In stock only", value=True)

    category_id = None
    if selected_category != "All":
        category_id = next(category["id"] for category in categories if category["name"] == selected_category)

    return {
        "search": search or None,
        "category_id": category_id,
        "min_price": min_price,
        "max_price": max_price,
        "min_rating": min_rating,
        "in_stock": in_stock,
    }


def render_product_grid(products, allow_cart=True):
    allow_cart = allow_cart and bool(st.session_state.username)
    if not products:
        st.info("No products match the current filters.")
        return

    cols = st.columns(4)
    for index, product in enumerate(products):
        with cols[index % 4]:
            with st.container(border=True):
                st.image(normalize_image(product["image_url"]), use_container_width=True)
                st.subheader(product["name"])
                st.caption(product["category"])
                st.write(product["description"])
                st.metric("Price", f"${product['price']:,.2f}")
                st.write(f"{product['rating']:.1f} stars | {product['stock']} left")
                if not allow_cart:
                    st.info("Log in or sign up to add this product to your cart.")
                    continue
                qty = st.number_input(
                    "Qty",
                    min_value=1,
                    max_value=max(product["stock"], 1),
                    value=1,
                    key=f"qty_{product['id']}",
                )
                disabled = product["stock"] <= 0
                if st.button("Add to cart", key=f"add_{product['id']}", disabled=disabled, use_container_width=True):
                    add_to_cart(product["id"], qty)
                    st.toast(f"Added {product['name']}")


def shop_page():
    if not require_login():
        return
    categories = api_service.get_categories()
    query = filters(categories)
    products = api_service.get_products(query)
    st.title("Shop")
    st.caption(f"{len(products)} products found")
    render_product_grid(products)


def cart_page():
    if not require_login():
        return
    st.title("Cart")
    st.caption("Review your items, adjust quantities, then complete the checkout form.")
    cart = st.session_state.cart
    products = api_service.get_products()
    product_map = {str(product["id"]): product for product in products}

    if not cart:
        st.info("Your cart is empty.")
        return

    rows = []
    for product_id, quantity in cart.items():
        product = product_map.get(product_id)
        if product:
            rows.append(
                {
                    "id": int(product_id),
                    "Product": product["name"],
                    "Quantity": quantity,
                    "Unit Price": product["price"],
                    "Line Total": product["price"] * quantity,
                    "Stock": product["stock"],
                }
            )

    st.subheader("Items")
    for row in rows:
        with st.container(border=True):
            item_cols = st.columns([3, 1, 1, 1])
            with item_cols[0]:
                st.write(row["Product"])
                st.caption(f"${row['Unit Price']:,.2f} each")
            with item_cols[1]:
                new_quantity = st.number_input(
                    "Quantity",
                    min_value=1,
                    max_value=max(row["Stock"], 1),
                    value=row["Quantity"],
                    key=f"cart_quantity_{row['id']}",
                )
                if new_quantity != row["Quantity"]:
                    update_cart_quantity(row["id"], new_quantity)
                    st.rerun()
            with item_cols[2]:
                st.metric("Line Total", f"${row['Unit Price'] * new_quantity:,.2f}")
            with item_cols[3]:
                st.write("")
                if st.button("Remove", key=f"remove_cart_{row['id']}", use_container_width=True):
                    remove_from_cart(row["id"])
                    st.rerun()

    subtotal = sum(row["Line Total"] for row in rows)
    tax = round(subtotal * 0.0825, 2)
    total = subtotal + tax

    c1, c2, c3 = st.columns(3)
    c1.metric("Subtotal", f"${subtotal:,.2f}")
    c2.metric("Tax", f"${tax:,.2f}")
    c3.metric("Total", f"${total:,.2f}")

    st.subheader("Checkout")
    with st.form("checkout_form"):
        customer_name = st.text_input("Full name", value=st.session_state.username or "")
        email = st.text_input("Email")
        address = st.text_area("Shipping address")
        payment_method = st.selectbox("Payment method", ["Credit Card", "Debit Card", "PayPal", "Cash on Delivery"])
        notes = st.text_area("Order notes", placeholder="Optional delivery notes")
        submitted = st.form_submit_button("Place order", type="primary")

    if submitted:
        if not customer_name.strip() or not email.strip() or not address.strip() or not payment_method:
            st.error("Please complete your name, email, address, and payment method.")
            return
        items = [{"product_id": int(product_id), "quantity": quantity} for product_id, quantity in cart.items()]
        try:
            order = api_service.checkout(customer_name, items)
            st.session_state.cart = {}
            st.success(f"Order #{order['id']} complete. Total: ${order['total']:,.2f}")
            if notes:
                st.info("Your order notes were received in the checkout form.")
            st.balloons()
        except Exception as exc:
            st.error(str(exc))


def analytics_page():
    if st.session_state.role != "admin":
        st.warning("Analytics is available to admins only.")
        return
    st.title("Analytics")
    products = api_service.get_products()
    orders = api_service.get_orders(st.session_state.api_key) if st.session_state.role == "admin" else []

    if not products:
        st.info("No data yet.")
        return

    left, right = st.columns(2)
    with left:
        counts = {}
        for product in products:
            counts[product["category"]] = counts.get(product["category"], 0) + 1
        category_counts = [
            {"Category": category, "Products": count}
            for category, count in counts.items()
        ]
        st.subheader("Products by Category")
        st.bar_chart(category_counts, x="Category", y="Products")
    with right:
        values = {}
        for product in products:
            values[product["category"]] = values.get(product["category"], 0) + product["price"] * product["stock"]
        category_value = [
            {"Category": category, "Value": value}
            for category, value in values.items()
        ]
        st.subheader("Inventory Value")
        st.bar_chart(category_value, x="Category", y="Value")

    st.subheader("Price vs Rating")
    st.scatter_chart(products, x="price", y="rating", size="stock", color="category")

    if orders:
        st.subheader("Recent Orders")
        st.dataframe(orders, use_container_width=True, hide_index=True)


def admin_page():
    if st.session_state.role != "admin":
        st.warning("Admin access only. Use admin / admin123 for the seeded admin account.")
        return

    st.title("Admin")
    st.caption("Manage products, featured products, categories, users, and store data from one place.")
    st.session_state.api_key = st.text_input(
        "API key",
        value=st.session_state.api_key,
        type="password",
    )
    tab_products, tab_featured, tab_categories, tab_users = st.tabs(
        ["Products", "Featured", "Categories", "Users"]
    )

    categories = api_service.get_categories()
    products = api_service.get_products()
    category_names = [category["name"] for category in categories]
    category_id_by_name = {category["name"]: category["id"] for category in categories}
    category_name_by_id = {category["id"]: category["name"] for category in categories}

    with tab_products:
        create_col, edit_col = st.columns(2)
        with create_col:
            st.subheader("Create Product")
            with st.form("create_product_form"):
                name = st.text_input("Name")
                category_name = st.selectbox("Category", category_names, key="create_product_category")
                description = st.text_area("Description")
                price = st.number_input("Price", min_value=0.0, step=1.0)
                stock = st.number_input("Stock", min_value=0, step=1)
                rating = st.slider("Rating", 0.0, 5.0, 4.0, step=0.1)
                image_url = st.text_input("Image URL", value="https://picsum.photos/seed/new-product/900/700")
                featured = st.checkbox("Featured")
                submitted = st.form_submit_button("Create product", type="primary")

            if submitted:
                product = {
                    "name": name,
                    "category_id": category_id_by_name[category_name],
                    "description": description,
                    "price": price,
                    "stock": stock,
                    "rating": rating,
                    "image_url": image_url,
                    "featured": featured,
                }
                try:
                    api_service.create_product(product, st.session_state.api_key)
                    st.success("Product created.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

        with edit_col:
            st.subheader("Edit Product")
            if not products:
                st.info("No products available.")
            else:
                selected_name = st.selectbox("Choose product", [product["name"] for product in products])
                selected_product = next(product for product in products if product["name"] == selected_name)
                category_index = category_names.index(category_name_by_id[selected_product["category_id"]])

                with st.form("edit_product_form"):
                    edit_name = st.text_input("Name", value=selected_product["name"])
                    edit_category = st.selectbox(
                        "Category",
                        category_names,
                        index=category_index,
                        key="edit_product_category",
                    )
                    edit_description = st.text_area("Description", value=selected_product["description"])
                    edit_price = st.number_input(
                        "Price",
                        min_value=0.0,
                        value=float(selected_product["price"]),
                        step=1.0,
                    )
                    edit_stock = st.number_input(
                        "Stock",
                        min_value=0,
                        value=int(selected_product["stock"]),
                        step=1,
                    )
                    edit_rating = st.slider(
                        "Rating",
                        0.0,
                        5.0,
                        float(selected_product["rating"]),
                        step=0.1,
                    )
                    edit_image_url = st.text_input("Image URL", value=selected_product["image_url"])
                    edit_featured = st.checkbox("Featured", value=selected_product["featured"])
                    save_product = st.form_submit_button("Save product changes", type="primary")

                if save_product:
                    product = {
                        "name": edit_name,
                        "category_id": category_id_by_name[edit_category],
                        "description": edit_description,
                        "price": edit_price,
                        "stock": edit_stock,
                        "rating": edit_rating,
                        "image_url": edit_image_url,
                        "featured": edit_featured,
                    }
                    try:
                        api_service.update_product(selected_product["id"], product, st.session_state.api_key)
                        st.success("Product updated.")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))

                if st.button("Delete this product", use_container_width=True):
                    try:
                        api_service.delete_product(selected_product["id"], st.session_state.api_key)
                        st.success("Product deleted.")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))

        st.subheader("Current Inventory")
        st.dataframe(products, use_container_width=True, hide_index=True)

    with tab_featured:
        st.subheader("Featured Products")
        st.caption("Featured products appear on the Home page.")
        if not products:
            st.info("No products available.")
        else:
            for product in products:
                with st.container(border=True):
                    cols = st.columns([2, 1, 1])
                    with cols[0]:
                        st.write(product["name"])
                        st.caption(product["category"])
                    with cols[1]:
                        st.write("Featured" if product["featured"] else "Not featured")
                    with cols[2]:
                        new_featured = not product["featured"]
                        label = "Remove featured" if product["featured"] else "Make featured"
                        if st.button(label, key=f"feature_toggle_{product['id']}", use_container_width=True):
                            updated = {
                                "name": product["name"],
                                "category_id": product["category_id"],
                                "description": product["description"],
                                "price": product["price"],
                                "stock": product["stock"],
                                "rating": product["rating"],
                                "image_url": product["image_url"],
                                "featured": new_featured,
                            }
                            try:
                                api_service.update_product(product["id"], updated, st.session_state.api_key)
                                st.success("Featured status updated.")
                                st.rerun()
                            except Exception as exc:
                                st.error(str(exc))

    with tab_categories:
        st.subheader("Create Category")
        new_category = st.text_input("Category name")
        if st.button("Add category"):
            try:
                api_service.create_category(new_category, st.session_state.api_key)
                st.success("Category created.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))
        st.dataframe(categories, use_container_width=True, hide_index=True)

    with tab_users:
        st.subheader("Users")
        try:
            users = api_service.get_users(st.session_state.api_key)
        except Exception as exc:
            st.error(str(exc))
            users = []

        create_user_col, edit_user_col = st.columns(2)
        with create_user_col:
            st.subheader("Create User")
            with st.form("create_user_form"):
                new_username = st.text_input("Username")
                new_password = st.text_input("Password", type="password")
                new_role = st.selectbox("Role", ["user", "admin"])
                create_user_submitted = st.form_submit_button("Create user", type="primary")

            if create_user_submitted:
                try:
                    api_service.create_user(
                        {
                            "username": new_username,
                            "password": new_password,
                            "role": new_role,
                        },
                        st.session_state.api_key,
                    )
                    st.success("User created.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

        with edit_user_col:
            st.subheader("Edit User")
            if not users:
                st.info("No users available.")
            else:
                user_labels = [f"{user['username']} ({user['role']})" for user in users]
                selected_user_label = st.selectbox("Choose user", user_labels)
                selected_user = users[user_labels.index(selected_user_label)]

                with st.form("edit_user_form"):
                    edit_username = st.text_input("Username", value=selected_user["username"])
                    edit_password = st.text_input("New password", type="password")
                    edit_role = st.selectbox(
                        "Role",
                        ["user", "admin"],
                        index=0 if selected_user["role"] == "user" else 1,
                    )
                    save_user = st.form_submit_button("Save user changes", type="primary")

                if save_user:
                    try:
                        api_service.update_user(
                            selected_user["id"],
                            {
                                "username": edit_username,
                                "password": edit_password or None,
                                "role": edit_role,
                            },
                            st.session_state.api_key,
                        )
                        if selected_user["username"] == st.session_state.username:
                            st.session_state.username = edit_username
                            st.session_state.role = edit_role
                        st.success("User updated.")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))

                if st.button("Delete this user", use_container_width=True):
                    try:
                        api_service.delete_user(selected_user["id"], st.session_state.api_key)
                        if selected_user["username"] == st.session_state.username:
                            st.session_state.username = None
                            st.session_state.role = None
                            st.session_state.cart = {}
                        st.success("User deleted.")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))

        st.subheader("User List")
        st.dataframe(users, use_container_width=True, hide_index=True)


def require_login():
    if st.session_state.username:
        return True
    st.warning("Please log in or create an account to use this page.")
    return False


def navigation_options():
    if st.session_state.role == "admin":
        return ["Home", "Shop", "Cart", "Analytics", "Admin"]
    if st.session_state.role == "user":
        return ["Home", "Shop", "Cart"]
    return ["Home"]


def main():
    init_session()
    if not api_ready():
        return

    sidebar_auth()
    page = st.sidebar.radio("Navigation", navigation_options())
    cart_status = st.sidebar.empty()

    if page == "Home":
        home_page()
    elif page == "Shop":
        shop_page()
    elif page == "Cart":
        cart_page()
    elif page == "Analytics":
        analytics_page()
    elif page == "Admin":
        admin_page()

    if st.session_state.username:
        cart_status.metric("Cart Items", sum(st.session_state.cart.values()))
    else:
        cart_status.info("Guests can browse the home page. Log in or sign up to shop.")


if __name__ == "__main__":
    main()
