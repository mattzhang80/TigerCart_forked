document.addEventListener('DOMContentLoaded', () => {
    // Event delegation for dynamically added buttons
    document.body.addEventListener('click', function(event) {
        if (event.target.classList.contains('add-to-cart')) {
            const itemId = event.target.getAttribute('data-item-id');
            fetch(`/add_to_cart/${itemId}`, {
                method: 'POST'
            }).then(response => {
                if (response.ok) {
                    alert('Item added to cart!');
                }
            });
        }
    });
});

function updateQuantity(itemId, action) {
    fetch(`/update_cart/${itemId}/${action}`, { method: 'POST' })
        .then(response => response.json())
        .then(cart => {
            location.reload();  // Refresh to reflect the updated cart view
        });
}

function placeOrder() {
    fetch('/place_order', { method: 'POST' })
        .then(() => {
            alert('Order placed successfully!');
            window.location.href = '/';
        });
}
