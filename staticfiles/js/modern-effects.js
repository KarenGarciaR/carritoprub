/* ===== MODERN EFFECTS FOR ALM REFACCIONARIA ===== */

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize all modern effects
    initScrollAnimations();
    initParallaxEffects();
    initSmoothTransitions();
    initLoadingEffects();
    initFormEnhancements();
    initCardHoverEffects();
    initTooltips();
    initLazyLoading();
    initScrollToTop();
    initThemeToggle();
    // enhanceSearch(); // Desactivado - conflicta con búsqueda del template
    
    console.log('✨ Modern effects initialized successfully!');
});

// 1. Scroll Animations
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe all product cards, feature cards, and main sections
    const elementsToAnimate = document.querySelectorAll(
        '.product-card, .feature-card, .cart-item, .box-element, .hero-section'
    );
    
    elementsToAnimate.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        observer.observe(el);
    });
}

// 2. Parallax Effects
function initParallaxEffects() {
    const parallaxElements = document.querySelectorAll('.hero-section, .parallax-bg');
    
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const rate = scrolled * -0.5;
        
        parallaxElements.forEach(element => {
            element.style.transform = `translateY(${rate}px)`;
        });
    });
}

// 3. Smooth Transitions
function initSmoothTransitions() {
    // Add smooth transitions to buttons and interactive elements
    const buttons = document.querySelectorAll('.btn, .social-btn, .quantity-btn');
    
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
        
        button.addEventListener('mousedown', function() {
            this.style.transform = 'translateY(0) scale(0.95)';
        });
        
        button.addEventListener('mouseup', function() {
            this.style.transform = 'translateY(-2px) scale(1)';
        });
    });
}

// 4. Loading Effects
function initLoadingEffects() {
    // Show loading state for AJAX requests
    const updateCartButtons = document.querySelectorAll('.update-cart');
    
    updateCartButtons.forEach(button => {
        button.addEventListener('click', function() {
            showButtonLoading(this);
            setTimeout(() => hideButtonLoading(this), 1000);
        });
    });
}

function showButtonLoading(button) {
    const originalContent = button.innerHTML;
    button.dataset.originalContent = originalContent;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    button.disabled = true;
    button.classList.add('loading');
}

function hideButtonLoading(button) {
    button.innerHTML = button.dataset.originalContent || button.innerHTML;
    button.disabled = false;
    button.classList.remove('loading');
}

// 5. Form Enhancements
function initFormEnhancements() {
    const formInputs = document.querySelectorAll('input, textarea, select');
    
    formInputs.forEach(input => {
        // Floating labels effect
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
        
        // Real-time validation indicators
        input.addEventListener('input', function() {
            if (this.checkValidity()) {
                this.classList.remove('invalid');
                this.classList.add('valid');
            } else {
                this.classList.remove('valid');
                this.classList.add('invalid');
            }
        });
    });
}

// 6. Card Hover Effects
function initCardHoverEffects() {
    const cards = document.querySelectorAll('.product-card, .cart-item, .feature-card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
            this.style.boxShadow = '0 15px 40px rgba(0,0,0,0.2)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '0 5px 20px rgba(0,0,0,0.1)';
        });
    });
}

// 7. Tooltips
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function(e) {
            showTooltip(e.target, e.target.dataset.tooltip);
        });
        
        element.addEventListener('mouseleave', function() {
            hideTooltip();
        });
    });
}

function showTooltip(element, text) {
    const tooltip = document.createElement('div');
    tooltip.className = 'custom-tooltip';
    tooltip.textContent = text;
    
    tooltip.style.cssText = `
        position: absolute;
        background: #2c3e50;
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 14px;
        z-index: 10000;
        pointer-events: none;
        opacity: 0;
        transform: translateY(10px);
        transition: all 0.3s ease;
    `;
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
    
    setTimeout(() => {
        tooltip.style.opacity = '1';
        tooltip.style.transform = 'translateY(0)';
    }, 10);
}

function hideTooltip() {
    const tooltip = document.querySelector('.custom-tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

// 8. Lazy Loading for Images
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// 9. Scroll to Top Button
function initScrollToTop() {
    // Create scroll to top button
    const scrollBtn = document.createElement('button');
    scrollBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    scrollBtn.className = 'scroll-to-top';
    scrollBtn.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, #FF8C00, #FF6B35);
        color: white;
        border: none;
        border-radius: 50%;
        cursor: pointer;
        z-index: 1000;
        opacity: 0;
        transform: translateY(100px);
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 140, 0, 0.3);
    `;
    
    document.body.appendChild(scrollBtn);
    
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            scrollBtn.style.opacity = '1';
            scrollBtn.style.transform = 'translateY(0)';
        } else {
            scrollBtn.style.opacity = '0';
            scrollBtn.style.transform = 'translateY(100px)';
        }
    });
    
    scrollBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// 10. Theme Toggle (Optional)
function initThemeToggle() {
    // Create theme toggle button
    const themeBtn = document.createElement('button');
    themeBtn.innerHTML = '<i class="fas fa-moon"></i>';
    themeBtn.className = 'theme-toggle';
    themeBtn.style.cssText = `
        position: fixed;
        top: 100px;
        right: 30px;
        width: 50px;
        height: 50px;
        background: white;
        color: #2c3e50;
        border: 2px solid #e1e8ed;
        border-radius: 50%;
        cursor: pointer;
        z-index: 1000;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    `;
    
    document.body.appendChild(themeBtn);
    
    themeBtn.addEventListener('click', () => {
        document.body.classList.toggle('dark-theme');
        const isDark = document.body.classList.contains('dark-theme');
        themeBtn.innerHTML = isDark ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
        
        // Save preference
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });
    
    // Load saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        themeBtn.innerHTML = '<i class="fas fa-sun"></i>';
    }
}

// 11. Page Transition Effects
function initPageTransitions() {
    // Add page enter animation
    document.body.style.opacity = '0';
    document.body.style.transform = 'translateY(20px)';
    
    window.addEventListener('load', () => {
        document.body.style.transition = 'all 0.5s ease';
        document.body.style.opacity = '1';
        document.body.style.transform = 'translateY(0)';
    });
}

// 12. Enhanced Cart Animations
function enhanceCartAnimations() {
    const cartIcon = document.getElementById('cart-icon');
    const cartTotal = document.getElementById('cart-total');
    
    if (cartIcon && cartTotal) {
        // Animate cart when items are added
        window.addEventListener('cartUpdated', () => {
            cartIcon.style.animation = 'bounce 0.6s ease';
            cartTotal.style.animation = 'pulse 0.6s ease';
            
            setTimeout(() => {
                cartIcon.style.animation = '';
                cartTotal.style.animation = '';
            }, 600);
        });
    }
}

// 13. Search Enhancement
function enhanceSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        let searchTimeout;
        
        // Asegurar que todos los productos estén visibles inicialmente
        const allProducts = document.querySelectorAll('.product-card');
        allProducts.forEach(product => {
            product.style.display = 'block';
        });
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const searchTerm = this.value.toLowerCase().trim();
            
            // Add loading state
            this.classList.add('loading');
            
            searchTimeout = setTimeout(() => {
                // Perform search
                filterProducts(searchTerm);
                this.classList.remove('loading');
            }, 300);
        });
    }
}

function filterProducts(searchTerm) {
    // Esta función está desactivada para evitar conflictos con la búsqueda del template store.html
    // La funcionalidad de búsqueda se maneja directamente en el template
    return;
}

// 14. Performance Monitoring
function initPerformanceMonitoring() {
    // Monitor page load performance
    window.addEventListener('load', () => {
        setTimeout(() => {
            const navigation = performance.getEntriesByType('navigation')[0];
            const loadTime = navigation.loadEventEnd - navigation.loadEventStart;
            
            if (loadTime > 3000) {
                console.warn('⚠️ Page load time is slow:', loadTime + 'ms');
            } else {
                console.log('✅ Page loaded in:', loadTime + 'ms');
            }
        }, 0);
    });
}

// Initialize performance monitoring
initPerformanceMonitoring();

// Export functions for external use
window.ModernEffects = {
    showButtonLoading,
    hideButtonLoading,
    showTooltip,
    hideTooltip,
    filterProducts
};