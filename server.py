#!/usr/bin/env python
"""
server.py
Serves data for the TigerCart app.
"""

from flask import Flask, jsonify, request, session
import json
from database import get_main_db_connection, get_user_db_connection

app = Flask(__name__)
app.secret_key = (
    "your_secret_key"  # Set a secure secret key for sessions
)


@app.route("/items", methods=["GET"])
def get_items():
    conn = get_main_db_connection()
    cursor = conn.cursor()
    items = cursor.execute("SELECT * FROM items").fetchall()
    conn.close()

    # Convert each Row object to a dictionary
    items_dict = {str(item["id"]): dict(item) for item in items}
    return jsonify(items_dict)


@app.route("/cart", methods=["GET", "POST"])
def manage_cart():
    user_id = session.get("user_id")
    conn = get_user_db_connection()
    cursor = conn.cursor()

    # Retrieve the current user's cart from the users table
    user = cursor.execute(
        "SELECT cart FROM users WHERE user_id = ?", (user_id,)
    ).fetchone()
    if user is None:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    # Parse the cart as a dictionary or set it to an empty dictionary
    try:
        cart = json.loads(user["cart"]) if user["cart"] else {}
    except json.JSONDecodeError:
        cart = {}

    if request.method == "POST":
        # Update the cart based on the action in the POST request
        cart_data = request.json
        item_id = cart_data.get("item_id")
        action = cart_data.get("action")

        # Modify cart structure according to action
        if action == "add":
            cart[item_id] = {
                "quantity": cart.get(item_id, {}).get("quantity", 0) + 1
            }
        elif action == "delete":
            cart.pop(item_id, None)
        elif action == "update":
            quantity = cart_data.get("quantity")
            if quantity > 0:
                cart[item_id] = {"quantity": quantity}
            else:
                cart.pop(item_id, None)

        # Save the updated cart as a JSON string in the database
        cursor.execute(
            "UPDATE users SET cart = ? WHERE user_id = ?",
            (json.dumps(cart), user_id),
        )
        conn.commit()

    conn.close()
    return jsonify(cart)


@app.route("/deliveries", methods=["GET"])
def get_deliveries():
    conn = get_main_db_connection()
    cursor = conn.cursor()
    orders = cursor.execute(
        "SELECT * FROM orders WHERE status = 'placed'"
    ).fetchall()
    deliveries = {}
    for order in orders:
        subtotal = sum(
            int(quantity) * float(price)
            for quantity, price in zip(
                order["quantities"].split(","),
                order["prices"].split(","),
            )
        )
        earnings = round(subtotal * 0.1, 2)
        deliveries[str(order["id"])] = {
            **dict(order),
            "subtotal": round(subtotal, 2),
            "earnings": earnings,
        }
    conn.close()
    return jsonify(deliveries)


@app.route("/delivery/<delivery_id>", methods=["GET"])
def get_delivery(delivery_id):
    conn = get_main_db_connection()
    cursor = conn.cursor()
    order = cursor.execute(
        "SELECT * FROM orders WHERE id = ?", (delivery_id,)
    ).fetchone()
    if order:
        total = sum(
            int(quantity) * float(price)
            for quantity, price in zip(
                order["quantities"].split(","),
                order["prices"].split(","),
            )
        )
        order_dict = dict(order)
        order_dict["total"] = f"{total:.2f}"
        order_dict["earnings"] = f"{(total * 0.1):.2f}"
        conn.close()
        return jsonify(order_dict)
    conn.close()
    return jsonify({"error": "Delivery not found"}), 404


if __name__ == "__main__":
    app.run(port=5150, debug=True)
