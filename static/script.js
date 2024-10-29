document.addEventListener('DOMContentLoaded', () => {
    const messageElement = document.getElementById('js-working');
    messageElement.textContent += ' yes';
});

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', () => {
            const itemId = button.getAttribute('data-item-id');
            fetch(`/add_to_cart/${itemId}`, {
                method: 'POST'
            }).then(response => {
                if (response.ok) {
                    alert('Item added to cart!');
                }
            });
        });
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
