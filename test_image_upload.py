#!/usr/bin/env python
"""
Script para probar la subida de imágenes al carrusel
"""
import os
import django
from PIL import Image, ImageDraw, ImageFont
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from store.models import CarouselSlide

def create_test_image():
    """Crear una imagen de prueba para el carrusel"""
    # Crear una imagen de 1200x600 píxeles (tamaño típico para carrusel)
    width, height = 1200, 600
    image = Image.new('RGB', (width, height), color='#4a90e2')
    
    # Obtener un objeto de dibujo
    draw = ImageDraw.Draw(image)
    
    # Intentar usar una fuente, si no está disponible usar la default
    try:
        font_title = ImageFont.truetype("arial.ttf", 60)
        font_text = ImageFont.truetype("arial.ttf", 30)
    except OSError:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()
    
    # Añadir texto
    title_text = "¡OFERTA ESPECIAL!"
    subtitle_text = "Refacciones ALM - Calidad Garantizada"
    
    # Calcular posición del texto para centrarlo
    bbox_title = draw.textbbox((0, 0), title_text, font=font_title)
    title_width = bbox_title[2] - bbox_title[0]
    title_x = (width - title_width) // 2
    
    bbox_subtitle = draw.textbbox((0, 0), subtitle_text, font=font_text)
    subtitle_width = bbox_subtitle[2] - bbox_subtitle[0]
    subtitle_x = (width - subtitle_width) // 2
    
    # Dibujar el texto
    draw.text((title_x, height//2 - 80), title_text, fill='white', font=font_title)
    draw.text((subtitle_x, height//2 + 20), subtitle_text, fill='white', font=font_text)
    
    # Agregar un borde decorativo
    draw.rectangle([20, 20, width-20, height-20], outline='white', width=3)
    
    # Guardar la imagen
    image_path = 'media/carousel/test_offer_image.jpg'
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    image.save(image_path, 'JPEG', quality=90)
    
    print(f"✅ Imagen de prueba creada en: {image_path}")
    return image_path

def create_test_carousel_slide():
    """Crear un slide de carrusel de prueba"""
    try:
        # Crear la imagen de prueba
        image_path = create_test_image()
        
        # Crear el slide de carrusel
        slide = CarouselSlide.objects.create(
            title="¡Oferta Especial de Refacciones!",
            subtitle="Hasta 30% de descuento en productos seleccionados",
            description="Aprovecha nuestras ofertas especiales en refacciones de calidad. Válido por tiempo limitado.",
            image=image_path.replace('media/', ''),  # Django maneja la ruta relativa
            button_text="Ver Ofertas",
            button_link="/store/",
            external_link=False,
            is_active=True,
            order=1,
            slide_type='promotion'
        )
        
        print(f"✅ Slide de carrusel creado exitosamente: {slide.title}")
        print(f"   - ID: {slide.id}")
        print(f"   - Imagen: {slide.image.url if slide.image else 'Sin imagen'}")
        print(f"   - Activo: {slide.is_active}")
        
        return slide
        
    except Exception as e:
        print(f"❌ Error creando slide de carrusel: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Iniciando prueba de subida de imágenes al carrusel...")
    
    # Verificar que la carpeta media/carousel existe
    carousel_dir = 'media/carousel'
    if not os.path.exists(carousel_dir):
        os.makedirs(carousel_dir)
        print(f"✅ Carpeta creada: {carousel_dir}")
    
    # Crear slide de prueba
    slide = create_test_carousel_slide()
    
    if slide:
        print("\n🎉 ¡Prueba completada exitosamente!")
        print("Ahora puedes:")
        print("1. Ir al admin de Django (http://127.0.0.1:8000/admin/)")
        print("2. Navegar a 'Slides del Carrusel'")
        print("3. Ver el slide de prueba creado")
        print("4. Intentar subir más imágenes manualmente")
    else:
        print("\n❌ La prueba falló. Revisa los errores arriba.")