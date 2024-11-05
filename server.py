#!/usr/bin/env python
"""
server.py
Serves data for the TigerCart app.
"""

import json
from flask import Flask, jsonify, request
from config import get_debug_mode, SECRET_KEY
from database import get_main_db_connection, get_user_db_connection

app = Flask(__name__)
app.secret_key = SECRET_KEY


@app.route("/items", methods=["GET"])
def get_items():
    """Fetches and returns all items available in the store."""
    conn = get_main_db_connection()
    cursor = conn.cursor()
    items = cursor.execute("SELECT * FROM items").fetchall()
    conn.close()

    items_dict = {str(item["id"]): dict(item) for item in items}
    return jsonify(items_dict)


@app.route("/cart", methods=["GET", "POST"])
def manage_cart():
    """Logic to add/remove items and change quantities"""
    data = request.json
    user_id = data.get("user_id")
    conn = get_user_db_connection()
    cursor = conn.cursor()

    # Retrieve user's cart
    user = cursor.execute(
        "SELECT cart FROM users WHERE user_id = ?", (user_id,)
    ).fetchone()
    if user is None:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    cart = json.loads(user["cart"]) if user["cart"] else {}

    if request.method == "POST":
        item_id = str(data.get("item_id"))
        action = data.get("action")

        # Here, use get_main_db_connection() for the items table
        item_conn = get_main_db_connection()
        item_cursor = item_conn.cursor()
        item_exists = item_cursor.execute(
            "SELECT 1 FROM items WHERE id = ?", (item_id,)
        ).fetchone()
        item_conn.close()

        if not item_exists:
            conn.close()
            return (
                jsonify({"error": "Item not found in inventory"}),
                404,
            )

        # Proceed with modifying cart based on action
        if action == "add":
            cart[item_id] = {
                "quantity": cart.get(item_id, {}).get("quantity", 0) + 1
            }
        elif action == "delete":
            cart.pop(item_id, None)
        elif action == "update":
            quantity = data.get("quantity", 0)
            if quantity > 0:
                cart[item_id] = {"quantity": quantity}
            else:
                cart.pop(item_id, None)

        cursor.execute(
            "UPDATE users SET cart = ? WHERE user_id = ?",
            (json.dumps(cart), user_id),
        )
        conn.commit()
        conn.close()

    return jsonify(cart)


@app.route("/deliveries", methods=["GET"])
def get_deliveries():
    """Fetches and returns all deliveries with their details and earnings."""
    conn = get_main_db_connection()
    cursor = conn.cursor()
    orders = cursor.execute(
        """SELECT id, timestamp, user_id,
        total_items, cart, location
        FROM orders WHERE status = 'placed'"""
    ).fetchall()

    deliveries = {}
    for order in orders:
        # Load cart items from JSON
        cart = json.loads(order["cart"])
        # Get list of item_ids
        item_ids = list(cart.keys())

        # Fetch item details from items table
        if item_ids:
            placeholders = ','.join(['?'] * len(item_ids))
            cursor.execute(
                f"SELECT id, price FROM items WHERE id IN ({placeholders})",
                item_ids
            )
            items = cursor.fetchall()
            # Build a dict of item_id to price
            item_prices = {str(item['id']): item['price'] for item in items}
        else:
            item_prices = {}

        # Calculate subtotal
        subtotal = 0
        for item_id, item_info in cart.items():
            quantity = item_info.get('quantity', 0)
            price = item_prices.get(item_id, 0)
            subtotal += quantity * price

        earnings = round(subtotal * 0.1, 2)  # Calculate 10% earnings

        deliveries[str(order["id"])] = {
            "id": order["id"],
            "timestamp": order["timestamp"],
            "user_id": order["user_id"],
            "total_items": order["total_items"],
            "cart": cart,
            "location": order["location"],
            "earnings": earnings,
        }
    conn.close()
    return jsonify(deliveries)




@app.route("/delivery/<delivery_id>", methods=["GET"])
def get_delivery(delivery_id):
    """Fetches and returns details of a specific delivery."""
    conn = get_main_db_connection()
    cursor = conn.cursor()
    order = cursor.execute(
        "SELECT id, timestamp, user_id, total_items, cart, location FROM orders WHERE id = ?",
        (delivery_id,),
    ).fetchone()

    if order:
        # Parse the cart JSON to get item quantities
        cart_data = json.loads(order["cart"])

        # Fetch item details from the items table for each item in the cart
        detailed_cart = {}
        subtotal = 0

        for item_id, item_info in cart_data.items():
            item = cursor.execute(
                "SELECT name, price FROM items WHERE id = ?", (item_id,)
            ).fetchone()

            if item:
                # Calculate the item's total price based on its quantity
                item_total = item_info["quantity"] * item["price"]
                subtotal += item_total

                # Add complete item details to the cart
                detailed_cart[item_id] = {
                    "name": item["name"],
                    "price": item["price"],
                    "quantity": item_info["quantity"],
                    "total": item_total,
                }

        earnings = round(
            subtotal * 0.1, 2
        )  # Calculate earnings as 10% of subtotal

        # Prepare the delivery dictionary to return
        delivery = {
            "id": order["id"],
            "timestamp": order["timestamp"],
            "user_id": order["user_id"],
            "total_items": order["total_items"],
            "cart": detailed_cart,  # Use the fully detailed cart
            "location": order["location"],
            "subtotal": round(subtotal, 2),
            "earnings": earnings,
        }
        conn.close()
        return jsonify(delivery)

    conn.close()
    return jsonify({"error": "Delivery not found"}), 404


@app.route("/accept_delivery/<delivery_id>", methods=["POST"])
def accept_delivery(delivery_id):
    """Marks the delivery as accepted by changing its status."""
    conn = get_main_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE orders SET status = 'claimed' WHERE id = ?",
        (delivery_id,),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True}), 200  # Return a JSON response

@app.route("/decline_delivery/<delivery_id>", methods=["POST"])
def decline_delivery(delivery_id):
    """Declines the delivery by deleting the order."""
    conn = get_main_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM orders WHERE id = ?", (delivery_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True}), 200  # Return a JSON response



if __name__ == "__main__":
    app.run(port=5150, debug=get_debug_mode())
