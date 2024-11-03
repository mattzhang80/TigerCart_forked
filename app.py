#!/usr/bin/env python
"""
app.py
Authors: TigerCart team
"""

from flask import Flask, render_template, redirect, url_for, jsonify
import requests
from config import get_debug_mode

app = Flask(__name__)

# Define the base URL for the server
SERVER_URL = "http://localhost:5150"
REQUEST_TIMEOUT = 5  # Timeout in seconds for all requests


@app.route("/")
def home():
    """Render the home page."""
    return render_template("home.html")


@app.route("/shop")
def shop():
    """Render the shop page showing all items from server.py."""
    response = requests.get(
        f"{SERVER_URL}/items", timeout=REQUEST_TIMEOUT
    )
    sample_items = response.json()
    return render_template("shop.html", items=sample_items)


@app.route("/category_view/<category>")
def category_view(category):
    """Render a category view page with items filtered by category."""
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
    """Render the cart view with current items, subtotal, delivery fee, and total."""
    items_response = requests.get(
        f"{SERVER_URL}/items", timeout=REQUEST_TIMEOUT
    )
    cart_response = requests.get(
        f"{SERVER_URL}/cart", timeout=REQUEST_TIMEOUT
    )
    sample_items = items_response.json()
    cart = cart_response.json()

    subtotal = sum(
        details["quantity"] * sample_items[item_id]["price"]
        for item_id, details in cart.items()
    )
    delivery_fee = round(subtotal * 0.1, 2)
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
    """Add an item to the cart or increment its quantity if it already exists."""
    response = requests.post(
        f"{SERVER_URL}/cart",
        json={"item_id": item_id, "action": "add"},
        timeout=REQUEST_TIMEOUT,
    )
    return jsonify(response.json())


@app.route("/delete_item/<item_id>", methods=["POST"])
def delete_item(item_id):
    """Delete an item from the cart."""
    response = requests.post(
        f"{SERVER_URL}/cart",
        json={"item_id": item_id, "action": "delete"},
        timeout=REQUEST_TIMEOUT,
    )
    return jsonify(response.json())


@app.route("/update_cart/<item_id>/<action>", methods=["POST"])
def update_cart(item_id, action):
    """Update the quantity of an item in the cart based on the action."""
    response = requests.get(
        f"{SERVER_URL}/cart", timeout=REQUEST_TIMEOUT
    )
    cart = response.json()

    if action == "increase":
        requests.post(
            f"{SERVER_URL}/cart",
            json={"item_id": item_id, "action": "add"},
            timeout=REQUEST_TIMEOUT,
        )
    elif action == "decrease":
        quantity = cart.get(item_id, {}).get("quantity", 0)
        if quantity > 1:
            requests.post(
                f"{SERVER_URL}/cart",
                json={
                    "item_id": item_id,
                    "quantity": quantity - 1,
                    "action": "update",
                },
                timeout=REQUEST_TIMEOUT,
            )
        elif quantity == 1:
            requests.post(
                f"{SERVER_URL}/cart",
                json={"item_id": item_id, "action": "delete"},
                timeout=REQUEST_TIMEOUT,
            )
    return jsonify(cart)


@app.route("/order_confirmation")
def order_confirmation():
    """Render the order confirmation page."""
    response = requests.get(
        f"{SERVER_URL}/cart", timeout=REQUEST_TIMEOUT
    )
    items_in_cart = len(response.json())
    return render_template(
        "order_confirmation.html", items_in_cart=items_in_cart
    )


@app.route("/place_order", methods=["POST"])
def place_order():
    """Place an order by clearing the cart."""
    requests.post(
        f"{SERVER_URL}/cart", json={}, timeout=REQUEST_TIMEOUT
    )  # Empty cart in server
    return redirect(url_for("home"))


@app.route("/deliver")
def deliver():
    """Render the delivery page with available delivery tasks."""
    response = requests.get(
        f"{SERVER_URL}/deliveries", timeout=REQUEST_TIMEOUT
    )
    deliveries = response.json()
    return render_template(
        "deliver.html", deliveries=deliveries.values()
    )


@app.route("/delivery/<delivery_id>")
def delivery_details(delivery_id):
    """Render details for a specific delivery."""
    response = requests.get(
        f"{SERVER_URL}/delivery/{delivery_id}", timeout=REQUEST_TIMEOUT
    )
    if response.status_code == 200:
        delivery = response.json()
        return render_template(
            "delivery_details.html", delivery=delivery
        )
    return "Delivery not found", 404


@app.route("/timeline")
def delivery_timeline():
    """Render the delivery timeline page for deliverers."""
    return render_template("deliverer_timeline.html")


if __name__ == "__main__":
    app.run(port=8000, debug=get_debug_mode())
