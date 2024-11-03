document.addEventListener('DOMContentLoaded', () => {
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

function deleteItem(itemId) {
    if (confirm('Are you sure you want to remove this item from your cart?')) {
        fetch(`/delete_item/${itemId}`, { method: 'POST' })
            .then(response => response.json())
            .then(cart => {
                location.reload();  // Refresh to reflect the updated cart view
            });
    }
}

function placeOrder(itemsInCart) {
    fetch('/place_order', { method: 'POST' })
        .then(() => {
            if (itemsInCart === 0) {
                alert('No items in cart, please go back and make an order!')
            }
            else
                alert('Order placed successfully!');
            window.location.href = '/';
        });
}

function acceptDelivery(deliveryId) {
    alert('Delivery accepted');
    window.location.href = '/timeline'
}

function declineDelivery(deliveryId) {
    // Send a POST request to decline the delivery
    fetch(`/decline_delivery/${deliveryId}`, { method: 'POST' })
        .then(response => {
            if (response.ok) {
                alert('Delivery declined');
                window.location.href = '/deliver'; // Redirects back to the deliveries page
            } else {
                alert('Failed to decline the delivery');
            }
        })
        .catch(error => {
            console.error('Error declining delivery:', error);
        });
}

function markStepComplete(stepId) {
    const stepElement = document.getElementById(stepId);
    const circleElement = stepElement.querySelector('.circle');
    const buttonElement = stepElement.querySelector('button');

    // Change circle appearance and button status
    circleElement.classList.add('complete');
    buttonElement.textContent = 'Completed';
    buttonElement.style.backgroundColor = 'green';
}
