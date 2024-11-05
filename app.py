#!/usr/bin/env python
"""
app.py
Authors: TigerCart team
"""

import json
import requests
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    session,
    jsonify,
)
from config import get_debug_mode, SECRET_KEY
from database import get_main_db_connection, get_user_db_connection

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Define the base URL for the server
SERVER_URL = "http://localhost:5150"
REQUEST_TIMEOUT = 5  # Timeout in seconds for all requests
DELIVERY_FEE_PERCENTAGE = 0.1


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page to authenticate the user."""
    if request.method == "POST":
        user_id = request.form.get("user_id")
        session["user_id"] = user_id
        user = (
            get_user_db_connection()
            .execute(
                "SELECT name FROM users WHERE user_id = ?", (user_id,)
            )
            .fetchone()
        )
        session["user_name"] = user["name"] if user else "Guest"
        return redirect(url_for("home"))

    users = (
        get_user_db_connection()
        .execute("SELECT * FROM users")
        .fetchall()
    )
    return render_template("login.html", users=users)


@app.route("/logout", methods=["POST"])
def logout():
    """Logs the user out and clears the session."""
    session["user_id"] = None
    return "", 204


@app.route("/")
def home():
    """Home page. Redirects to login if user is not logged in."""
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("home.html")


@app.route("/shop")
def shop():
    """Displays items available in the shop."""
    response = requests.get(
        f"{SERVER_URL}/items", timeout=REQUEST_TIMEOUT
    )
    sample_items = response.json()
    return render_template("shop.html", items=sample_items)


@app.route("/category_view/<category>")
def category_view(category):
    """Displays items in a specific category."""
    response = requests.get(
        f"{SERVER_URL}/items", timeout=REQUEST_TIMEOUT
    )
    sample_items = response.json()
    items_in_category = {
        k: v
        for k, v in sample_items.items()
        if v.get("category") == category
    }
    return render_template(
        "category_view.html", category=category, items=items_in_category
    )


@app.route("/cart_view")
def cart_view():
    """Displays the cart view with item subtotals and total cost."""
    items_response = requests.get(
        f"{SERVER_URL}/items", timeout=REQUEST_TIMEOUT
    )
    cart_response = requests.get(
        f"{SERVER_URL}/cart",
        json={"user_id": session["user_id"]},
        timeout=REQUEST_TIMEOUT,
    )

    sample_items = items_response.json()
    cart = cart_response.json()

    subtotal = sum(
        details.get("quantity", 0)
        * sample_items.get(item_id, {}).get("price", 0)
        for item_id, details in cart.items()
        if isinstance(details, dict)
    )
    delivery_fee = round(subtotal * DELIVERY_FEE_PERCENTAGE, 2)
    total = round(subtotal + delivery_fee, 2)

    return render_template(
        "cart_view.html",
        cart=cart,
        items=sample_items,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total=total,
    )


@app.route("/add_to_cart/<item_id>", methods=["POST"])
def add_to_cart(item_id):
    """Adds an item to the cart."""
    response = requests.post(
        f"{SERVER_URL}/cart",
        json={
            "user_id": session["user_id"],
            "item_id": item_id,
            "action": "add",
        },
        timeout=REQUEST_TIMEOUT,
    )
    return jsonify(response.json())


@app.route("/delete_item/<item_id>", methods=["POST"])
def delete_item(item_id):
    """Deletes an item from the cart."""
    response = requests.post(
        f"{SERVER_URL}/cart",
        json={
            "user_id": session["user_id"],
            "item_id": item_id,
            "action": "delete",
        },
        timeout=REQUEST_TIMEOUT,
    )
    return jsonify(response.json())


@app.route("/update_cart/<item_id>/<action>", methods=["POST"])
def update_cart(item_id, action):
    """Updates the cart by increasing or decreasing item quantities."""
    user_id = session["user_id"]
    if action == "increase":
        requests.post(
            f"{SERVER_URL}/cart",
            json={
                "user_id": user_id,
                "item_id": item_id,
                "action": "add",
            },
            timeout=REQUEST_TIMEOUT,
        )
    elif action == "decrease":
        # Get the current cart to check the item's quantity
        cart_response = requests.get(
            f"{SERVER_URL}/cart",
            json={"user_id": user_id},
            timeout=REQUEST_TIMEOUT,
        )
        cart = cart_response.json()

        quantity = cart.get(item_id, {}).get("quantity", 0)
        if quantity > 1:
            # Decrease quantity by 1
            requests.post(
                f"{SERVER_URL}/cart",
                json={
                    "user_id": user_id,
                    "item_id": item_id,
                    "quantity": quantity - 1,
                    "action": "update",
                },
                timeout=REQUEST_TIMEOUT,
            )
        elif quantity == 1:
            # Remove the item if quantity reaches 1
            requests.post(
                f"{SERVER_URL}/cart",
                json={
                    "user_id": user_id,
                    "item_id": item_id,
                    "action": "delete",
                },
                timeout=REQUEST_TIMEOUT,
            )
    return jsonify({"success": True})


@app.route("/order_confirmation")
def order_confirmation():
    """Displays the order confirmation page with items in cart."""
    response = requests.get(
        f"{SERVER_URL}/cart",
        json={"user_id": session["user_id"]},
        timeout=REQUEST_TIMEOUT,
    )
    items_in_cart = len(response.json())
    return render_template(
        "order_confirmation.html", items_in_cart=items_in_cart
    )


@app.route("/place_order", methods=["POST"])
def place_order():
    """Places an order and clears the user's cart."""
    conn = get_main_db_connection()
    user_conn = get_user_db_connection()
    cursor = conn.cursor()
    user_cursor = user_conn.cursor()

    user_id = session.get("user_id")
    data = request.get_json()
    delivery_location = data.get("delivery_location")

    if not delivery_location:
        return jsonify({"error": "Delivery location is required"}), 400

    user = user_cursor.execute(
        "SELECT cart FROM users WHERE user_id = ?", (user_id,)
    ).fetchone()
    cart = json.loads(user["cart"]) if user and user["cart"] else {}

    if not cart:
        return jsonify({"error": "Cart is empty"}), 400

    total_items = sum(details["quantity"] for details in cart.values())

    # Insert the delivery information into the orders table
    cursor.execute(
        """INSERT INTO orders
        (status, user_id, total_items, cart, location)
        VALUES (?, ?, ?, ?, ?)""",
        (
            "placed",
            user_id,
            total_items,
            json.dumps(cart),
            delivery_location,
        ),
    )

    # Clear the user's cart after placing the order
    user_cursor.execute(
        "UPDATE users SET cart = '{}' WHERE user_id = ?", (user_id,)
    )
    conn.commit()
    user_conn.commit()
    conn.close()
    user_conn.close()

    return redirect(url_for("home"))


@app.route("/deliver")
def deliver():
    """Displays all deliveries available for claiming."""
    response = requests.get(
        f"{SERVER_URL}/deliveries", timeout=REQUEST_TIMEOUT
    )
    deliveries = response.json()
    return render_template(
        "deliver.html", deliveries=deliveries.values()
    )


@app.route("/delivery/<delivery_id>")
def delivery_details(delivery_id):
    """Displays details of a specific delivery."""
    response = requests.get(
        f"{SERVER_URL}/delivery/{delivery_id}", timeout=REQUEST_TIMEOUT
    )
    if response.status_code == 200:
        delivery = response.json()
        return render_template(
            "delivery_details.html", delivery=delivery
        )
    return "Delivery not found", 404


@app.route("/accept_delivery/<delivery_id>", methods=["POST"])
def accept_delivery(delivery_id):
    """Accepts a delivery by forwarding the request to the backend server."""
    response = requests.post(
        f"{SERVER_URL}/accept_delivery/{delivery_id}",
        timeout=REQUEST_TIMEOUT,
    )
    if response.status_code == 200:
        # Redirect to the delivery timeline or confirmation page
        return redirect(
            url_for("delivery_timeline", delivery_id=delivery_id)
        )
    return "Error accepting delivery", response.status_code


@app.route("/decline_delivery/<delivery_id>", methods=["POST"])
def decline_delivery(delivery_id):
    """Declines a delivery by forwarding the request to the backend server."""
    response = requests.post(
        f"{SERVER_URL}/decline_delivery/{delivery_id}",
        timeout=REQUEST_TIMEOUT,
    )
    if response.status_code == 200:
        return redirect(url_for("deliver"))
    return "Error declining delivery", response.status_code


@app.route("/delivery_timeline/<delivery_id>")
def delivery_timeline(delivery_id):
    """Displays a timeline for the accepted delivery."""
    # Fetch necessary data for the delivery timeline
    response = requests.get(
        f"{SERVER_URL}/delivery/{delivery_id}",
        timeout=REQUEST_TIMEOUT,
    )
    if response.status_code == 200:
        delivery = response.json()
        return render_template(
            "deliverer_timeline.html", delivery=delivery
        )
    return "Delivery not found", 404


if __name__ == "__main__":
    app.run(port=8000, debug=get_debug_mode())
