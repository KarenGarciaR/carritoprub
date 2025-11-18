import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from store.models import CarouselSlide

def check_carousel_slides():
    print("=== VERIFICACIÓN DEL CARRUSEL ===\n")
    
    # Obtener todos los slides
    all_slides = CarouselSlide.objects.all()
    visible_slides = CarouselSlide.objects.filter(is_active=True)
    
    print(f"Total de slides en la base de datos: {all_slides.count()}")
    print(f"Slides activos: {visible_slides.count()}\n")
    
    if all_slides.exists():
        print("DETALLES DE LOS SLIDES:")
        print("-" * 60)
        
        for slide in all_slides:
            print(f"ID: {slide.id}")
            print(f"Título: {slide.title}")
            print(f"Tipo: {slide.get_slide_type_display()}")
            print(f"Activo: {'Sí' if slide.is_active else 'No'}")
            print(f"Visible: {'Sí' if slide.is_visible else 'No'}")
            print(f"Imagen URL: {slide.image_url}")
            print(f"Orden: {slide.order}")
            print(f"Enlace: {slide.button_link or 'Sin enlace'}")
            print("-" * 60)
    else:
        print("No hay slides en la base de datos.")
        print("\nEjecutar 'python create_carousel_slides.py' para crear slides de ejemplo.")
    
    print("\n=== ESTADÍSTICAS ===")
    types_count = {}
    for slide in visible_slides:
        slide_type = slide.get_slide_type_display()
        types_count[slide_type] = types_count.get(slide_type, 0) + 1
    
    if types_count:
        print("Distribución por tipo (slides activos):")
        for slide_type, count in types_count.items():
            print(f"  - {slide_type}: {count}")
    else:
        print("No hay slides activos para mostrar estadísticas.")

if __name__ == "__main__":
    check_carousel_slides()