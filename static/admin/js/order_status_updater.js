// JavaScript para acciones rápidas en el admin
function updateStatus(orderHistoryId, newStatus) {
    if (confirm(`¿Estás seguro de cambiar el estado a "${newStatus}"?`)) {
        // Obtener el token CSRF
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch('/admin/update-order-status/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({
                'order_history_id': orderHistoryId,
                'status': newStatus
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error al actualizar el estado: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error de conexión');
        });
    }
}

// Funciones adicionales para mejorar la experiencia del admin
document.addEventListener('DOMContentLoaded', function() {
    // Agregar tooltips a los badges de estado
    const statusBadges = document.querySelectorAll('[title]');
    statusBadges.forEach(badge => {
        badge.style.cursor = 'help';
    });
    
    // Mejorar la visualización de las imágenes de productos
    const productImages = document.querySelectorAll('img[width="50"]');
    productImages.forEach(img => {
        img.addEventListener('click', function() {
            const modal = document.createElement('div');
            modal.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.8);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999;
                cursor: pointer;
            `;
            
            const modalImg = document.createElement('img');
            modalImg.src = this.src;
            modalImg.style.cssText = `
                max-width: 90%;
                max-height: 90%;
                border-radius: 10px;
            `;
            
            modal.appendChild(modalImg);
            document.body.appendChild(modal);
            
            modal.addEventListener('click', function() {
                document.body.removeChild(modal);
            });
        });
    });
});

// Función para búsqueda rápida
function quickSearch(term) {
    const searchInput = document.querySelector('#searchbar');
    if (searchInput) {
        searchInput.value = term;
        searchInput.form.submit();
    }
}

// Función para filtros rápidos
function applyQuickFilter(filterName, filterValue) {
    const url = new URL(window.location);
    url.searchParams.set(filterName, filterValue);
    window.location = url;
}