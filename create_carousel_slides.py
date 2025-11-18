#!/usr/bin/env python
"""
Script para crear slides de ejemplo para el carrusel
"""
import os
import sys
import django

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from store.models import *
from django.utils import timezone
from datetime import timedelta

def create_sample_slides():
    """Crear slides de ejemplo para el carrusel"""
    
    print("🎠 Creando slides de ejemplo para el carrusel...")
    
    # Limpiar slides existentes
    CarouselSlide.objects.all().delete()
    print("🧹 Slides existentes eliminados")
    
    # Slides de ejemplo
    slides_data = [
        {
            'title': '¡Ofertas Especiales!',
            'subtitle': 'Hasta 30% de descuento',
            'description': 'Aprovecha nuestras ofertas en suspensiones y componentes automotrices de la más alta calidad.',
            'slide_type': 'promotion',
            'button_text': 'Ver Ofertas',
            'button_link': '/tienda/',
            'order': 1,
            'background_color': '#e74c3c',
            'text_color': '#ffffff'
        },
        {
            'title': 'ALM Refaccionaria',
            'subtitle': 'Más de 20 años de experiencia',
            'description': 'Conoce nuestras instalaciones y el equipo profesional que te brinda el mejor servicio.',
            'slide_type': 'business',
            'button_text': 'Conocer Más',
            'button_link': '/nosotros/',
            'order': 2,
            'background_color': '#3498db',
            'text_color': '#ffffff'
        },
        {
            'title': 'Amortiguadores Premium',
            'subtitle': 'Calidad garantizada',
            'description': 'Descubre nuestra línea premium de amortiguadores para todo tipo de vehículos.',
            'slide_type': 'product',
            'button_text': 'Ver Productos',
            'button_link': '/tienda/',
            'order': 3,
            'background_color': '#f39c12',
            'text_color': '#ffffff'
        },
        {
            'title': 'Servicio de Instalación',
            'subtitle': 'Instalación profesional',
            'description': 'Nuestro equipo técnico especializado instala tus componentes con la máxima precisión.',
            'slide_type': 'service',
            'button_text': 'Contactar',
            'button_link': '/contacto/',
            'order': 4,
            'background_color': '#27ae60',
            'text_color': '#ffffff'
        }
    ]
    
    created_count = 0
    for slide_data in slides_data:
        slide = CarouselSlide.objects.create(**slide_data)
        created_count += 1
        print(f"✅ Slide creado: {slide.title} ({slide.get_slide_type_display()})")
    
    print(f"\n📊 Resumen:")
    print(f"   • {created_count} slides creados")
    print(f"   • Todos están activos y visibles")
    print(f"   • Configurados en orden ascendente")
    
    print(f"\n🎯 Para gestionar los slides:")
    print(f"   1. Ve a /admin/ e inicia sesión como administrador")
    print(f"   2. Busca la sección 'Slides del Carrusel'")
    print(f"   3. Puedes editar, activar/desactivar y reordenar slides")
    print(f"   4. Agrega imágenes reales para mejores resultados")
    
    print(f"\n📝 Notas importantes:")
    print(f"   • Los slides sin imagen mostrarán un placeholder")
    print(f"   • Puedes programar fechas de inicio y fin")
    print(f"   • Los colores se pueden personalizar")
    print(f"   • El orden determina la secuencia de aparición")

if __name__ == '__main__':
    try:
        create_sample_slides()
        print("\n🎉 ¡Slides de ejemplo creados exitosamente!")
    except Exception as e:
        print(f"\n❌ Error creando slides: {e}")
        import traceback
        traceback.print_exc()