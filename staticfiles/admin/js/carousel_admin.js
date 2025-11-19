// JavaScript para mejorar el admin del carrusel
(function() {
    'use strict';
    
    // Esperar a que el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCarouselAdmin);
    } else {
        initCarouselAdmin();
    }
    
    function initCarouselAdmin() {
        console.log('🎠 Carousel Admin JS loaded');
        
        // Mejorar campos de color
        const colorInputs = document.querySelectorAll('input[name="background_color"], input[name="text_color"]');
        colorInputs.forEach(function(input) {
            const wrapper = document.createElement('div');
            wrapper.className = 'color-picker-wrapper';
            wrapper.style.display = 'inline-flex';
            wrapper.style.alignItems = 'center';
            wrapper.style.gap = '10px';
            
            // Envolver el input
            input.parentNode.insertBefore(wrapper, input);
            wrapper.appendChild(input);
            
            // Crear input de tipo color
            const colorPicker = document.createElement('input');
            colorPicker.type = 'color';
            colorPicker.value = input.value || '#000000';
            colorPicker.style.width = '50px';
            colorPicker.style.height = '30px';
            colorPicker.style.border = 'none';
            colorPicker.style.cursor = 'pointer';
            
            wrapper.appendChild(colorPicker);
            
            // Sincronizar valores
            colorPicker.addEventListener('change', function() {
                input.value = this.value;
            });
            
            input.addEventListener('change', function() {
                colorPicker.value = this.value;
            });
        });
        
        // Validación de imagen
        const imageInput = document.querySelector('input[name="image"]');
        if (imageInput) {
            imageInput.addEventListener('change', function(e) {
                const file = this.files[0];
                if (!file) return;
                
                // Validar tipo de archivo
                const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
                if (!validTypes.includes(file.type)) {
                    alert('⚠️ Por favor selecciona un archivo de imagen válido (JPG, PNG, GIF, WebP)');
                    this.value = '';
                    return;
                }
                
                // Validar tamaño (máximo 5MB)
                const maxSize = 5 * 1024 * 1024; // 5MB
                if (file.size > maxSize) {
                    alert('⚠️ La imagen es demasiado grande. Por favor selecciona una imagen menor a 5MB.');
                    this.value = '';
                    return;
                }
                
                // Mostrar vista previa
                const reader = new FileReader();
                reader.onload = function(e) {
                    showImagePreview(e.target.result, imageInput);
                };
                reader.readAsDataURL(file);
                
                console.log('✅ Imagen seleccionada:', file.name, 'Tamaño:', (file.size / 1024 / 1024).toFixed(2) + 'MB');
            });
            
            // Agregar texto de ayuda
            const helpText = document.createElement('div');
            helpText.className = 'help';
            helpText.style.marginTop = '10px';
            helpText.style.padding = '10px';
            helpText.style.background = '#f0f8ff';
            helpText.style.border = '1px solid #b8daff';
            helpText.style.borderRadius = '4px';
            helpText.innerHTML = `
                <strong>💡 Consejos para subir imágenes:</strong><br>
                • Tamaño recomendado: 1200x600 píxeles (ratio 2:1)<br>
                • Formatos soportados: JPG, PNG, GIF, WebP<br>
                • Tamaño máximo: 5MB<br>
                • Para mejores resultados, usa imágenes de alta calidad
            `;
            
            const imageField = imageInput.closest('.form-row');
            if (imageField) {
                imageField.appendChild(helpText);
            }
        }
        
        // Función para mostrar vista previa de imagen
        function showImagePreview(src, input) {
            let preview = document.getElementById('image-upload-preview');
            if (!preview) {
                preview = document.createElement('div');
                preview.id = 'image-upload-preview';
                preview.style.marginTop = '15px';
                preview.style.padding = '10px';
                preview.style.background = '#f8f9fa';
                preview.style.borderRadius = '5px';
                preview.style.border = '1px solid #dee2e6';
                input.parentNode.appendChild(preview);
            }
            
            preview.innerHTML = `
                <p style="margin: 0 0 10px 0; font-weight: bold; color: #007bff;">📷 Vista previa de la imagen:</p>
                <img src="${src}" style="max-width: 300px; max-height: 200px; object-fit: contain; border: 1px solid #ddd; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />
            `;
        }
        
        // Mejorar el campo de orden
        const orderInput = document.querySelector('input[name="order"]');
        if (orderInput) {
            orderInput.min = '0';
            orderInput.step = '1';
            orderInput.placeholder = 'Ej: 1, 2, 3...';
        }
        
        console.log('✅ Carousel Admin JS initialized successfully');
    }
    
})();