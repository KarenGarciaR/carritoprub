from django.contrib import admin
from .models import CarouselSlide

@admin.register(CarouselSlide)
class CarouselSlideAdmin(admin.ModelAdmin):
    list_display = ['title', 'slide_type', 'is_active', 'order', 'created_at']
    list_filter = ['slide_type', 'is_active', 'created_at']
    search_fields = ['title', 'subtitle']
    list_editable = ['is_active', 'order']
    ordering = ['order', '-created_at']
    
    fieldsets = (
        ('Contenido Principal', {
            'fields': ('title', 'subtitle', 'description', 'image')
        }),
        ('Configuración', {
            'fields': ('slide_type', 'is_active', 'order')
        }),
        ('Botón y Enlaces', {
            'fields': ('button_text', 'button_link', 'external_link'),
            'classes': ('collapse',)
        }),
        ('Programación', {
            'fields': ('start_date', 'end_date'),
            'classes': ('collapse',)
        }),
    )