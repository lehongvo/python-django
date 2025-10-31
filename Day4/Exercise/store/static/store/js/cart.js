// Cart functionality for TechStore 2025

// Shopping Cart (stored in localStorage AND database)
const Cart = {
    get: () => {
        const cart = localStorage.getItem('cart');
        return cart ? JSON.parse(cart) : [];
    },
    
    add: async (productId, quantity = 1) => {
        const cart = Cart.get();
        const existingItem = cart.find(item => item.product_id === productId);
        
        if (existingItem) {
            existingItem.quantity += quantity;
        } else {
            cart.push({ product_id: productId, quantity });
        }
        
        localStorage.setItem('cart', JSON.stringify(cart));
        await Cart.updateCount();
        return cart;
    },
    
    remove: async (productId) => {
        const cart = Cart.get().filter(item => item.product_id !== productId);
        localStorage.setItem('cart', JSON.stringify(cart));
        await Cart.updateCount();
        return cart;
    },
    
    clear: async () => {
        localStorage.removeItem('cart');
        await Cart.updateCount();
    },
    
    updateCount: async () => {
        let items = Cart.get();
        let count = items.reduce((sum, item) => sum + item.quantity, 0);
        
        // If local cart is empty, try fetching server cart (after login)
        if (count === 0) {
            try {
                const res = await fetch('/api/cart/list/');
                if (res.ok) {
                    const data = await res.json();
                    if (data && Array.isArray(data.items) && data.items.length > 0) {
                        items = data.items.map(i => ({ product_id: i.product_id, quantity: i.quantity }));
                        localStorage.setItem('cart', JSON.stringify(items));
                        count = items.reduce((sum, item) => sum + item.quantity, 0);
                    }
                }
            } catch (e) {
                // not logged in or network issue
            }
        } else {
            // Sync local cart to server if has items
            try {
                await fetch('/api/cart/sync/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        cart: items
                    })
                });
            } catch (error) {
                console.log('Cart sync error (not logged in):', error);
            }
        }
        
        const cartBadges = document.querySelectorAll('.cart-badge');
        cartBadges.forEach(badge => {
            if (badge) {
                badge.textContent = count;
                badge.style.display = count > 0 ? 'flex' : 'none';
            }
        });
    },
    
    getCount: () => {
        return Cart.get().reduce((sum, item) => sum + item.quantity, 0);
    }
};

// API Functions
async function addToCart(productId, quantity = 1) {
    try {
        const response = await fetch('/api/cart/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'include',
            body: JSON.stringify({
                product_id: productId,
                quantity: quantity
            })
        });
        
        // If not authenticated, redirect to login
        if (response.status === 401) {
            showNotification('Please log in to add items to cart', 'error');
            setTimeout(() => window.location.href = '/login/', 800);
            return null;
        }

        const data = await response.json();
        
        if (response.ok) {
            // Add to local cart
            Cart.add(productId, quantity);
            showNotification('Product added to cart successfully!', 'success');
            return data;
        } else {
            // Check if login is required
            if (data.requires_login) {
                showNotification('Please log in to add items to cart', 'error');
                setTimeout(() => window.location.href = '/login/', 1500);
            } else {
                showNotification(data.error || 'Failed to add to cart', 'error');
            }
            return null;
        }
    } catch (error) {
        console.error('Cart error:', error);
        showNotification('Please log in to add items to cart', 'error');
        return null;
    }
}

async function buyNow(productId, quantity = 1) {
    try {
        const response = await fetch('/api/buy-now/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'include',
            body: JSON.stringify({
                product_id: productId,
                quantity: quantity
            })
        });
        
        // If not authenticated, redirect to login
        if (response.status === 401) {
            showNotification('Please log in to purchase products', 'error');
            setTimeout(() => window.location.href = '/login/', 800);
            return null;
        }

        const data = await response.json();
        
        if (response.ok) {
            showNotification('Redirecting to checkout...', 'success');
            if (data.redirect) {
                setTimeout(() => window.location.href = data.redirect, 1000);
            }
            return data;
        } else {
            // Check if login is required
            if (data.requires_login) {
                showNotification('Please log in to purchase products', 'error');
                setTimeout(() => window.location.href = '/login/', 1500);
            } else {
                showNotification(data.error || 'Failed to process order', 'error');
            }
            return null;
        }
    } catch (error) {
        console.error('Buy now error:', error);
        showNotification('Please try again later', 'error');
        return null;
    }
}

// Notification system
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `fixed top-20 right-4 z-50 px-6 py-4 rounded-lg shadow-lg transform translate-x-0 transition-all duration-300 ${
        type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
    }`;
    notification.innerHTML = `
        <div class="flex items-center">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} mr-3"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('translate-x-full', 'opacity-0');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Helper function to get cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize cart count on page load
document.addEventListener('DOMContentLoaded', () => {
    Cart.updateCount();
    
    // Clear cart badge when user logs out
    const logoutButtons = document.querySelectorAll('[onclick="logout()"]');
    logoutButtons.forEach(button => {
        button.addEventListener('click', () => {
            Cart.clear();
        });
    });
    
    // Add event listeners for all Add to Cart buttons
    document.querySelectorAll('[data-add-to-cart]').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const productId = this.dataset.productId;
            const quantity = parseInt(this.dataset.quantity) || 1;
            
            // Show loading state
            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Adding...';
            const self = this;
            // Failsafe: ensure the button always resets after a short delay
            setTimeout(() => {
                if (self.disabled) {
                    self.disabled = false;
                    self.innerHTML = '<i class="fas fa-shopping-cart mr-2"></i>Add';
                }
            }, 4000);
            
            const adder = (typeof window.addToCart === 'function')
                ? window.addToCart(productId, quantity)
                : (async function(){
                    const res = await fetch('/api/cart/add/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        credentials: 'include',
                        body: JSON.stringify({ product_id: productId, quantity })
                    });
                    if (res.status === 401) {
                        showNotification('Please log in to add items to cart', 'error');
                        setTimeout(() => window.location.href = '/login/', 800);
                        return;
                    }
                    if (res.ok) {
                        await Cart.add(productId, quantity);
                        showNotification('Product added to cart successfully!', 'success');
                    }
                })();

            Promise.resolve(adder)
                .then(() => {
                    // Guarantee a follow-up sync like on Home page
                    return Cart.updateCount();
                })
                .catch(() => {})
                .finally(() => {
                    self.disabled = false;
                    self.innerHTML = '<i class="fas fa-shopping-cart mr-2"></i>Add';
            });
        });
    });
    
    // Add event listeners for all Buy Now buttons
    document.querySelectorAll('[data-buy-now]').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            const quantity = parseInt(this.dataset.quantity) || 1;
            
            // Show loading state
            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';
            
            buyNow(productId, quantity).then(() => {
                this.disabled = false;
                this.innerHTML = '<i class="fas fa-bolt mr-2"></i>Buy Now';
            });
        });
    });
    
    // Quantity controls
    document.querySelectorAll('.quantity-control').forEach(button => {
        button.addEventListener('click', function() {
            const input = this.closest('.quantity-group').querySelector('input[type="number"]');
            const currentValue = parseInt(input.value);
            
            if (this.classList.contains('decrease') && currentValue > 1) {
                input.value = currentValue - 1;
            } else if (this.classList.contains('increase')) {
                const max = parseInt(input.max || 999);
                if (currentValue < max) {
                    input.value = currentValue + 1;
                }
            }
        });
    });
});

