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


def fetch_user_name(user_id, cursor_users):
    """Fetches the user name for a given user_id from the users database."""
    user = cursor_users.execute(
        "SELECT name FROM users WHERE user_id = ?", (user_id,)
    ).fetchone()
    return user["name"] if user else "Unknown User"


def fetch_detailed_cart(cart, cursor_orders):
    """Fetches detailed item information for each item in the cart."""
    detailed_cart = {}
    subtotal = 0

    for item_id, item_info in cart.items():
        item_data = cursor_orders.execute(
            "SELECT name, price FROM items WHERE id = ?", (item_id,)
        ).fetchone()
        if item_data:
            item_price = item_data["price"]
            quantity = item_info["quantity"]
            item_total = quantity * item_price
            subtotal += item_total

            detailed_cart[item_id] = {
                "name": item_data["name"],
                "price": item_price,
                "quantity": quantity,
                "total": item_total,
            }

    return detailed_cart, subtotal


@app.route("/deliveries", methods=["GET"])
def get_deliveries():
    """Fetches and returns all deliveries with user names, item details, and earnings."""
    conn_orders = get_main_db_connection()
    cursor_orders = conn_orders.cursor()
    conn_users = get_user_db_connection()
    cursor_users = conn_users.cursor()

    orders = cursor_orders.execute(
        """
        SELECT id, timestamp, user_id, total_items, cart, location
        FROM orders
        WHERE status = 'placed'
        """
    ).fetchall()

    deliveries = {}

    for order in orders:
        user_name = fetch_user_name(order["user_id"], cursor_users)

        # Load and fetch detailed item information for each cart item
        cart = json.loads(order["cart"])
        detailed_cart, subtotal = fetch_detailed_cart(
            cart, cursor_orders
        )

        earnings = round(subtotal * 0.1, 2)  # Calculate 10% earnings

        deliveries[str(order["id"])] = {
            "id": order["id"],
            "timestamp": order["timestamp"],
            "user_id": order["user_id"],
            "user_name": user_name,
            "total_items": order["total_items"],
            "cart": detailed_cart,
            "location": order["location"],
            "subtotal": round(subtotal, 2),
            "earnings": earnings,
        }

    conn_orders.close()
    conn_users.close()

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


@app.route('/get_shopper_timeline/<delivery_id>', methods=['GET'])
def get_shopper_timeline():
    """Get where the deliverer is in the timeline"""
    # note have not implemented deliverer change in timeline status
    # so always going to be default value of 'U-Store' for rn
    conn = get_main_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT timeline
        FROM orders
        WHERE id = ?
    ''', (1,))

    timeline_status = cursor.fetchone()
    conn.close()

    if timeline_status:
        # Assuming `timeline` is stored as a JSON string or simple text
        serialized_timeline = timeline_status[0]  # Extract the first element of the row
        return jsonify(timeline=serialized_timeline), 200  # Return a JSON response
    
    return jsonify({'error': 'Order not found'}), 404


if __name__ == "__main__":
    app.run(port=5150, debug=get_debug_mode())
