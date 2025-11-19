// JavaScript para mejorar el admin del carrusel
(function($) {
    'use strict';
    
    // Verificar que jQuery está disponible
    if (typeof $ === 'undefined') {
        console.warn('🎠 jQuery no está disponible, usando django.jQuery');
        $ = django.jQuery;
    }
    
    $(document).ready(function() {
        console.log('🎠 Carousel Admin JS loaded');
        
        // Mejorar el selector de color
        $('input[name="background_color"], input[name="text_color"]').each(function() {
            var $input = $(this);
            var $wrapper = $('<div class="color-picker-wrapper"></div>');
            $input.wrap($wrapper);
            
            // Crear input de tipo color
            var $colorPicker = $('<input type="color" class="color-picker">');
            $colorPicker.val($input.val());
            $input.after($colorPicker);
            
            // Sincronizar valores
            $colorPicker.on('change', function() {
                $input.val($(this).val());
                updateColorPreview($input, $(this).val());
            });
            
            $input.on('change', function() {
                $colorPicker.val($(this).val());
                updateColorPreview($input, $(this).val());
            });
            
            // Vista previa inicial
            updateColorPreview($input, $input.val());
        });
        
        // Función para actualizar vista previa de color
        function updateColorPreview($input, color) {
            var $preview = $input.siblings('.color-preview');
            if ($preview.length === 0) {
                $preview = $('<div class="color-preview"></div>');
                $input.after($preview);
            }
            
            $preview.css({
                'width': '30px',
                'height': '30px',
                'background-color': color,
                'border': '2px solid #ddd',
                'border-radius': '50%',
                'display': 'inline-block',
                'margin-left': '10px',
                'vertical-align': 'middle'
            });
        }
        
        // Validación de imagen
        $('input[name="image"]').on('change', function() {
            var file = this.files[0];
            if (file) {
                // Validar tipo de archivo
                var validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
                if (!validTypes.includes(file.type)) {
                    alert('⚠️ Por favor selecciona un archivo de imagen válido (JPG, PNG, GIF, WebP)');
                    $(this).val('');
                    return;
                }
                
                // Validar tamaño (máximo 5MB)
                var maxSize = 5 * 1024 * 1024; // 5MB
                if (file.size > maxSize) {
                    alert('⚠️ La imagen es demasiado grande. Por favor selecciona una imagen menor a 5MB.');
                    $(this).val('');
                    return;
                }
                
                // Mostrar vista previa
                var reader = new FileReader();
                reader.onload = function(e) {
                    showImagePreview(e.target.result);
                };
                reader.readAsDataURL(file);
                
                console.log('✅ Imagen seleccionada:', file.name, 'Tamaño:', (file.size / 1024 / 1024).toFixed(2) + 'MB');
            }
        });
        
        // Función para mostrar vista previa de imagen
        function showImagePreview(src) {
            var $preview = $('#image-upload-preview');
            if ($preview.length === 0) {
                $preview = $('<div id="image-upload-preview"></div>');
                $('input[name="image"]').after($preview);
            }
            
            $preview.html(`
                <div style="margin-top: 15px; padding: 10px; background: #f8f9fa; border-radius: 5px; border: 1px solid #dee2e6;">
                    <p style="margin: 0 0 10px 0; font-weight: bold; color: #007bff;">📷 Vista previa de la imagen:</p>
                    <img src="${src}" style="max-width: 300px; max-height: 200px; object-fit: contain; border: 1px solid #ddd; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />
                </div>
            `);
        }
        
        // Mejorar el mensaje de ayuda para imágenes
        var $imageField = $('.field-image');
        if ($imageField.length) {
            var helpText = `
                <div class="carousel-help-text">
                    <strong>💡 Consejos para subir imágenes:</strong><br>
                    • Tamaño recomendado: 1200x600 píxeles (ratio 2:1)<br>
                    • Formatos soportados: JPG, PNG, GIF, WebP<br>
                    • Tamaño máximo: 5MB<br>
                    • Para mejores resultados, usa imágenes de alta calidad
                </div>
            `;
            $imageField.append(helpText);
        }
        
        // Mejorar la interfaz de orden
        $('input[name="order"]').attr('min', '0').attr('step', '1').attr('placeholder', 'Ej: 1, 2, 3...');
        
        // Agregar tooltips informativos
        var tooltips = {
            'title': 'Título principal que aparecerá en el slide',
            'subtitle': 'Subtítulo opcional para información adicional',
            'description': 'Descripción detallada (opcional)',
            'button_text': 'Texto que aparecerá en el botón de acción',
            'button_link': 'URL a la que dirigirá el botón',
            'order': 'Orden de aparición (menor número = aparece primero)'
        };
        
        $.each(tooltips, function(fieldName, tooltip) {
            $(`input[name="${fieldName}"], textarea[name="${fieldName}"]`)
                .attr('title', tooltip)
                .attr('placeholder', tooltip);
        });
        
        console.log('✅ Carousel Admin JS initialized successfully');
    });
    
})(django.jQuery);