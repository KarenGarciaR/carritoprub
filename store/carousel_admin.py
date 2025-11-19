from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import CarouselSlide

@admin.register(CarouselSlide)
class CarouselSlideAdmin(admin.ModelAdmin):
    list_display = ['title', 'slide_type', 'image_preview', 'is_active', 'order', 'created_at']
    list_filter = ['slide_type', 'is_active', 'created_at']
    search_fields = ['title', 'subtitle', 'description']
    list_editable = ['is_active', 'order']
    ordering = ['order', '-created_at']
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('title', 'subtitle', 'description', 'slide_type', 'is_active', 'order')
        }),
        ('Imagen del Slide', {
            'fields': ('image', 'image_preview_large'),
            'description': 'Sube una imagen para el slide del carrusel'
        }),
        ('Botón de Acción', {
            'fields': ('button_text', 'button_link'),
            'classes': ('collapse',),
        }),
        ('Personalización', {
            'fields': ('background_color', 'text_color'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['image_preview_large']
    
    def image_preview(self, obj):
        """Miniatura de la imagen en la lista"""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 80px; height: 40px; object-fit: cover; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">Sin imagen</span>')
    image_preview.short_description = 'Vista Previa'
    
    def image_preview_large(self, obj):
        """Vista previa grande en el formulario de edición"""
        if obj.image:
            return format_html(
                '''
                <div style="margin-top: 10px; padding: 15px; background: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6;">
                    <p style="margin: 0 0 10px 0; font-weight: bold; color: #495057;">📷 Imagen actual del slide:</p>
                    <img src="{}" style="max-width: 500px; max-height: 300px; object-fit: contain; border: 2px solid #dee2e6; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" />
                    <p style="margin: 10px 0 0 0; font-size: 12px; color: #6c757d;">
                        <strong>URL:</strong> <a href="{}" target="_blank">{}</a>
                    </p>
                </div>
                ''',
                obj.image.url,
                obj.image.url,
                obj.image.url
            )
        return format_html('<p style="color: #999; font-style: italic;">No hay imagen cargada aún</p>')
    image_preview_large.short_description = 'Vista Previa Actual'
    
    def save_model(self, request, obj, form, change):
        """Override para debugging al guardar"""
        print(f"\n{'='*50}")
        print(f"🔄 Guardando CarouselSlide: {obj.title}")
        print(f"{'='*50}")
        
        # Verificar si hay imagen
        if 'image' in form.cleaned_data and form.cleaned_data['image']:
            print(f"✅ Imagen detectada: {form.cleaned_data['image']}")
        else:
            print(f"⚠️ No se detectó imagen nueva")
        
        # Guardar el objeto
        super().save_model(request, obj, form, change)
        
        # Verificar que se guardó
        if obj.image:
            print(f"✅ Imagen guardada exitosamente: {obj.image.url}")
        else:
            print(f"❌ No se guardó ninguna imagen")
        print(f"{'='*50}\n")
    
    class Media:
        css = {
            'all': ('admin/css/carousel_admin.css',)
        }
        js = ('admin/js/carousel_admin.js',)

print("✅ CarouselSlideAdmin registrado correctamente")