#!/usr/bin/env python
"""
app.py
Authors: TigerCart team
"""

from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    jsonify,
)

app = Flask(__name__)

# Temporary cart storage
cart = {}

# Sample items (load from database later)
sample_items = {
    "1": {"name": "Coke", "price": 1.09, "category": "drinks"},
    "2": {"name": "Diet Coke", "price": 1.29, "category": "drinks"},
    "3": {
        "name": "Tropicana Orange Juice",
        "price": 0.89,
        "category": "drinks",
    },
    "4": {
        "name": "Lay’s Potato Chips",
        "price": 1.59,
        "category": "food",
    },
    "5": {"name": "Snickers Bar", "price": 0.99, "category": "food"},
    "6": {"name": "Notebook", "price": 2.49, "category": "other"},
}


@app.route("/")
def home():
    """Render the home page."""
    return render_template("home.html")


@app.route("/shop")
def shop():
    """Render the shop page showing all items."""
    return render_template("shop.html")


@app.route("/category_view/<category>")
def category_view(category):
    """
    Render a category view page with items filtered by category.

    Parameters:
        category (str): The category to filter items by.

    Returns:
        Rendered template for the category view
        with items in that category.
    """
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
    """
    Render the cart view with current items, subtotal,
    delivery fee, and total.

    Returns:
        Rendered template for the cart view.
    """
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
    """
    Add an item to the cart or increment its quantity
    if it already exists.

    Parameters:
        item_id (str): The ID of the item to add to the cart.

    Returns:
        JSON response with the updated cart contents.
    """
    if item_id in cart:
        cart[item_id]["quantity"] += 1
    else:
        cart[item_id] = {"quantity": 1}
    return jsonify(cart)


@app.route("/delete_item/<item_id>", methods=["POST"])
def delete_item(item_id):
    """
    Delete an item from the cart.

    Parameters:
        item_id (str): The ID of the item to delete.

    Returns:
        JSON response with the updated cart contents.
    """
    if item_id in cart:
        del cart[item_id]
    return jsonify(cart)


@app.route("/update_cart/<item_id>/<action>", methods=["POST"])
def update_cart(item_id, action):
    """
    Update the quantity of an item in the cart based on the action.

    Parameters:
        item_id (str): The ID of the item to update.
        action (str): The action to perform ('increase' or 'decrease').

    Returns:
        JSON response with the updated cart contents.
    """
    if action == "increase":
        cart[item_id]["quantity"] += 1
    elif action == "decrease" and cart[item_id]["quantity"] > 1:
        cart[item_id]["quantity"] -= 1
    elif action == "decrease" and cart[item_id]["quantity"] == 1:
        del cart[item_id]
    return jsonify(cart)


@app.route("/order_confirmation")
def order_confirmation():
    """Render the order confirmation page."""
    itemsInCart = len(cart)
    return render_template("order_confirmation.html", itemsInCart=itemsInCart)


@app.route("/place_order", methods=["POST"])
def place_order():
    """
    Place an order by clearing the cart.

    Returns:
        Redirect to the home page.
    """
    cart.clear()
    return redirect(url_for("home"))


@app.route("/deliver")
def deliver():
    """
    Render the delivery page with available delivery tasks.

    Returns:
        Rendered template for the deliver page with sample deliveries.
    """
    deliveries = [
        {
            "id": "1",
            "item_count": 5,
            "location": "Firestone Library, B-Floor",
            "earnings": 1.61,
        },
        {
            "id": "2",
            "item_count": 1,
            "location": "Friend Center 001",
            "earnings": 0.05,
        },
        {
            "id": "3",
            "item_count": 20,
            "location": "Stadium Drive Garage",
            "earnings": 7.89,
        },
    ]
    return render_template("deliver.html", deliveries=deliveries)


@app.route("/delivery/<delivery_id>")
def delivery_details(delivery_id):
    """
    Render details for a specific delivery.

    Parameters:
        delivery_id (str): The ID of the delivery to display.

    Returns:
        Rendered template for the delivery details page.
    """
    delivery = {
        "id": delivery_id,
        "location": "Firestone Library, B-Floor",
        "delivery_items": [
            {"name": "Diet Coke", "price": 1.28, "quantity": 2},
            {
                "name": "Lay’s Potato Chips",
                "price": 1.59,
                "quantity": 1,
            },
            # Add more items as needed
        ],
        "total": 16.14,
        "earnings": 1.61,
    }
    return render_template("delivery_details.html", delivery=delivery)


if __name__ == "__main__":
    app.run(debug=True)
