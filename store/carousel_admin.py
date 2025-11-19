from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import CarouselSlide

class CarouselSlideForm(forms.ModelForm):
    """Formulario personalizado para CarouselSlide que preserva las imágenes"""
    
    class Meta:
        model = CarouselSlide
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'cols': 60}),
            'title': forms.TextInput(attrs={'size': 60}),
            'subtitle': forms.TextInput(attrs={'size': 60}),
            'button_text': forms.TextInput(attrs={'size': 30}),
            'button_link': forms.URLInput(attrs={'size': 60}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si estamos editando y hay una imagen, modificar el label
        if self.instance and self.instance.pk and self.instance.image:
            self.fields['image'].help_text = format_html(
                '<br><strong>✅ Imagen actual:</strong><br>'
                '<img src="{}" style="max-width: 200px; max-height: 150px; '
                'object-fit: contain; border: 2px solid #28a745; border-radius: 5px; margin: 5px 0;"/><br>'
                '<div style="background: #d4edda; border: 1px solid #c3e6cb; border-radius: 3px; padding: 8px; margin: 5px 0;">'
                '<small style="color: #155724;"><strong>💡 Importante:</strong><br>'
                '• <strong>Dejar vacío</strong> = conservar imagen actual<br>'
                '• <strong>Seleccionar archivo</strong> = reemplazar con nueva imagen</small></div>',
                self.instance.image.url
            )
            self.fields['image'].required = False
            self.fields['image'].label = "🖼️ Cambiar imagen (opcional)"
        else:
            self.fields['image'].help_text = format_html(
                '<div style="background: #cce5ff; border: 1px solid #007bff; border-radius: 3px; padding: 8px;">'
                '<small style="color: #004085;"><strong>📷 Requerido:</strong> Selecciona una imagen para el slide del carrusel.<br>'
                'Formatos: JPG, PNG, GIF, WebP | Tamaño recomendado: 1200x600px</small></div>'
            )
            self.fields['image'].label = "🖼️ Imagen del slide"

@admin.register(CarouselSlide)
class CarouselSlideAdmin(admin.ModelAdmin):
    form = CarouselSlideForm  # Usar el formulario personalizado
    list_display = ['title', 'slide_type', 'is_active', 'order', 'image_preview', 'created_at']
    list_filter = ['slide_type', 'is_active', 'created_at']
    search_fields = ['title', 'subtitle']
    list_editable = ['is_active', 'order']
    ordering = ['order', '-created_at']
    
    def save_model(self, request, obj, form, change):
        """Personalizar el guardado para preservar la imagen existente"""
        if change:  # Si estamos editando (no creando)
            try:
                # Obtener el objeto original de la base de datos
                original = CarouselSlide.objects.get(pk=obj.pk)
                
                # Verificar si se está intentando subir una nueva imagen
                new_image = form.cleaned_data.get('image')
                
                # Si hay una nueva imagen, usarla
                if new_image:
                    # Verificar que la nueva imagen sea válida
                    if hasattr(new_image, 'name') and new_image.name:
                        obj.image = new_image
                        print(f"✅ Nueva imagen guardada: {new_image.name}")
                    else:
                        # Si la nueva imagen no es válida, conservar la original
                        obj.image = original.image
                        print(f"⚠️ Imagen no válida, conservando original: {original.image}")
                elif original.image:
                    # Si no hay nueva imagen, conservar la original
                    obj.image = original.image
                    print(f"📸 Conservando imagen original: {original.image}")
                    
            except CarouselSlide.DoesNotExist:
                print("❌ Error: No se encontró el slide original")
                pass
                
        else:
            # Si estamos creando un nuevo slide
            new_image = form.cleaned_data.get('image')
            if new_image and hasattr(new_image, 'name') and new_image.name:
                print(f"✅ Nuevo slide con imagen: {new_image.name}")
            
        super().save_model(request, obj, form, change)
    
    fieldsets = (
        ('Contenido Principal', {
            'fields': ('title', 'subtitle', 'description', 'image', 'image_preview_large'),
            'description': 'Información principal del slide del carrusel'
        }),
        ('Configuración', {
            'fields': ('slide_type', 'is_active', 'order'),
            'description': 'Configuración de visualización y orden'
        }),
        ('Botón y Enlaces', {
            'fields': ('button_text', 'button_link', 'external_link'),
            'classes': ('collapse',),
            'description': 'Configuración del botón de acción (opcional)'
        }),
        ('Programación', {
            'fields': ('start_date', 'end_date'),
            'classes': ('collapse',),
            'description': 'Fechas de inicio y fin para mostrar el slide (opcional)'
        }),
        ('Colores Personalizados', {
            'fields': ('background_color', 'text_color'),
            'classes': ('collapse',),
            'description': 'Personalización de colores del slide'
        }),
    )
    
    readonly_fields = ['image_preview_large']
    
    def image_preview(self, obj):
        """Mostrar vista previa pequeña de la imagen en la lista"""
        if obj.image:
            from django.utils.html import format_html
            return format_html(
                '<img src="{}" style="width: 50px; height: 30px; object-fit: cover; border-radius: 3px;" />',
                obj.image.url
            )
        return "Sin imagen"
    image_preview.short_description = 'Vista Previa'
    
    def image_preview_large(self, obj):
        """Mostrar vista previa grande de la imagen en el formulario de edición"""
        if obj.image:
            from django.utils.html import format_html
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px; object-fit: contain; border: 1px solid #ddd; border-radius: 5px;" />',
                obj.image.url
            )
        return "No hay imagen cargada"
    image_preview_large.short_description = 'Vista Previa Actual'
    
    class Media:
        css = {
            'all': ('admin/css/carousel_admin.css',)
        }
        js = ('admin/js/carousel_admin.js',)