#!/usr/bin/env python
"""
Script para probar la preservación de imágenes en el admin
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from store.models import CarouselSlide

def test_image_preservation():
    """Probar que las imágenes se preservan al actualizar"""
    print("🧪 Probando preservación de imágenes...")
    
    # Buscar el slide con imagen que creamos antes
    slide_with_image = CarouselSlide.objects.filter(image__isnull=False).first()
    
    if not slide_with_image:
        print("❌ No hay slides con imagen para probar")
        return
    
    print(f"📄 Probando con slide: {slide_with_image.title}")
    print(f"   Imagen actual: {slide_with_image.image}")
    
    # Guardar la imagen original
    original_image = slide_with_image.image
    
    # Actualizar solo el título (sin tocar la imagen)
    slide_with_image.title = f"{slide_with_image.title} - ACTUALIZADO"
    slide_with_image.save()
    
    # Recargar desde la base de datos
    slide_with_image.refresh_from_db()
    
    # Verificar que la imagen se preservó
    if slide_with_image.image == original_image:
        print("✅ ¡Imagen preservada correctamente!")
        print(f"   Imagen después: {slide_with_image.image}")
    else:
        print("❌ La imagen se perdió")
        print(f"   Imagen después: {slide_with_image.image}")
    
    return slide_with_image

def create_slide_with_image_for_testing():
    """Crear un slide con imagen para testing"""
    print("🎨 Creando slide de prueba con imagen...")
    
    from PIL import Image, ImageDraw, ImageFont
    
    # Crear imagen de prueba
    img = Image.new('RGB', (800, 400), color='#28a745')
    draw = ImageDraw.Draw(img)
    
    # Agregar texto
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except OSError:
        font = ImageFont.load_default()
    
    draw.text((50, 150), "IMAGEN DE PRUEBA", fill='white', font=font)
    draw.text((50, 200), "No se debe borrar al actualizar", fill='white', font=font)
    
    # Guardar imagen
    image_path = 'media/carousel/preservation_test.jpg'
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    img.save(image_path, 'JPEG', quality=90)
    
    # Crear slide
    slide = CarouselSlide.objects.create(
        title="PRUEBA: Preservación de Imagen",
        subtitle="Este slide prueba que la imagen NO se borre",
        description="Al actualizar este slide, la imagen debe mantenerse intacta.",
        image=image_path.replace('media/', ''),
        button_text="Probar Admin",
        button_link="/admin/",
        is_active=True,
        order=0,
        slide_type='promotion'
    )
    
    print(f"✅ Slide creado: ID {slide.id}")
    print(f"   Título: {slide.title}")
    print(f"   Imagen: {slide.image}")
    
    return slide

def main():
    print("🚀 Iniciando prueba de preservación de imágenes...")
    print("=" * 60)
    
    # Crear un slide con imagen si no existe
    slides_with_images = CarouselSlide.objects.filter(image__isnull=False).count()
    if slides_with_images == 0:
        create_slide_with_image_for_testing()
    
    # Probar preservación
    test_slide = test_image_preservation()
    
    print("\n" + "=" * 60)
    print("✅ Prueba completada")
    
    if test_slide:
        print(f"\n💡 Ahora puedes probar en el admin:")
        print(f"1. Ve a: http://127.0.0.1:8000/admin/store/carouselslide/{test_slide.id}/change/")
        print(f"2. Cambia solo el título o subtítulo")
        print(f"3. NO toques el campo de imagen")
        print(f"4. Guarda el formulario")
        print(f"5. Verifica que la imagen sigue ahí")

if __name__ == "__main__":
    main()