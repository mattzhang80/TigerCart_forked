from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

# Temporary cart storage
cart = {}

# Sample items (load from database later)
items = {
    "1": {"name": "Coke", "price": 1.09},
    "2": {"name": "Diet Coke", "price": 1.29},
    "3": {"name": "Tropicana Orange Juice", "price": 0.89}
}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/shop')
def shop():
    return render_template('shop.html', items=items)

@app.route('/category/<category>')
def category(category):
    # Filter or load items based on the category
    items_in_category = {k: v for k, v in items.items() if v.get("category") == category}
    return render_template('category.html', category=category, items=items_in_category)

@app.route('/cart_view')
def cart_view():
    subtotal = sum(details['quantity'] * items[item_id]['price'] for item_id, details in cart.items())
    delivery_fee = round(subtotal * 0.1, 2)
    total = round(subtotal + delivery_fee, 2)
    return render_template('cart_view.html', cart=cart, items=items, subtotal=subtotal, delivery_fee=delivery_fee, total=total)

@app.route('/add_to_cart/<item_id>', methods=['POST'])
def add_to_cart(item_id):
    if item_id in cart:
        cart[item_id]['quantity'] += 1
    else:
        cart[item_id] = {'quantity': 1}
    return jsonify(cart)

@app.route('/update_cart/<item_id>/<action>', methods=['POST'])
def update_cart(item_id, action):
    if action == 'increase':
        cart[item_id]['quantity'] += 1
    elif action == 'decrease' and cart[item_id]['quantity'] > 1:
        cart[item_id]['quantity'] -= 1
    elif action == 'decrease' and cart[item_id]['quantity'] == 1:
        del cart[item_id]
    return jsonify(cart)

@app.route('/order_confirmation')
def order_confirmation():
    return render_template('order_confirmation.html')

@app.route('/place_order', methods=['POST'])
def place_order():
    # Clear the cart to simulate placing the order
    cart.clear()
    return redirect(url_for('home'))

@app.route('/deliver')
def deliver():
    # Placeholder data for available deliveries; replace with actual data as needed
    deliveries = [
        {"id": "1", "item_count": 5, "location": "Firestone Library, B-Floor", "earnings": 1.61},
        {"id": "2", "item_count": 1, "location": "Friend Center 001", "earnings": 0.05},
        {"id": "3", "item_count": 20, "location": "Stadium Drive Garage", "earnings": 7.89}
    ]
    return render_template('deliver.html', deliveries=deliveries)


@app.route('/delivery/<delivery_id>')
def delivery_details(delivery_id):
    # Simulated data structure for a delivery
    delivery = {
        "id": delivery_id,
        "location": "Firestone Library, B-Floor",
        "delivery_items": [
            {"name": "Diet Coke", "price": 1.28, "quantity": 2},
            {"name": "Lay’s Potato Chips", "price": 1.59, "quantity": 1},
            # Add more items as needed
        ],
        "total": 16.14,
        "earnings": 1.61
    }
    return render_template('delivery_details.html', delivery=delivery)

if __name__ == '__main__':
    app.run(debug=True)

