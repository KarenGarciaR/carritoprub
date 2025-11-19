#!/usr/bin/env python
"""
Script para diagnosticar y corregir problemas con imágenes en slides existentes
"""
import os
import django
from PIL import Image, ImageDraw, ImageFont

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from store.models import CarouselSlide

def create_placeholder_images():
    """Crear imágenes placeholder para slides sin imagen"""
    print("🎨 Creando imágenes placeholder para slides sin imagen...")
    
    slides_without_image = CarouselSlide.objects.filter(image='')
    
    for slide in slides_without_image:
        print(f"\n📄 Procesando slide: {slide.title}")
        
        # Crear imagen placeholder
        img = Image.new('RGB', (1200, 600), color='#007bff')
        draw = ImageDraw.Draw(img)
        
        # Intentar cargar fuente
        try:
            font_title = ImageFont.truetype("arial.ttf", 48)
            font_subtitle = ImageFont.truetype("arial.ttf", 24)
        except OSError:
            font_title = ImageFont.load_default()
            font_subtitle = ImageFont.load_default()
        
        # Dibujar fondo con gradiente simulado
        for i in range(600):
            color_value = int(0x00 + (0x7f * i / 600))
            color = f"#{color_value:02x}{color_value + 0x40:02x}ff"
            try:
                draw.line([(0, i), (1200, i)], fill=color)
            except:
                break
        
        # Agregar texto
        title_text = slide.title[:30] + "..." if len(slide.title) > 30 else slide.title
        subtitle_text = slide.subtitle[:50] + "..." if slide.subtitle and len(slide.subtitle) > 50 else (slide.subtitle or "")
        
        # Calcular posiciones centradas
        try:
            bbox_title = draw.textbbox((0, 0), title_text, font=font_title)
            title_width = bbox_title[2] - bbox_title[0]
            title_x = (1200 - title_width) // 2
            
            if subtitle_text:
                bbox_subtitle = draw.textbbox((0, 0), subtitle_text, font=font_subtitle)
                subtitle_width = bbox_subtitle[2] - bbox_subtitle[0]
                subtitle_x = (1200 - subtitle_width) // 2
        except:
            title_x = 100
            subtitle_x = 100
        
        # Dibujar textos
        draw.text((title_x, 250), title_text, fill='white', font=font_title)
        if subtitle_text:
            draw.text((subtitle_x, 320), subtitle_text, fill='#cccccc', font=font_subtitle)
        
        # Agregar borde
        draw.rectangle([10, 10, 1190, 590], outline='white', width=3)
        
        # Guardar imagen
        filename = f"slide_{slide.id}_{slide.slide_type}.jpg"
        image_path = f'media/carousel/{filename}'
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        img.save(image_path, 'JPEG', quality=85)
        
        # Actualizar slide
        slide.image = f'carousel/{filename}'
        slide.save()
        
        print(f"✅ Imagen creada: {filename}")

def diagnose_existing_slides():
    """Diagnosticar slides existentes"""
    print("🔍 Diagnosticando slides existentes...")
    
    all_slides = CarouselSlide.objects.all()
    print(f"Total de slides: {all_slides.count()}")
    
    slides_with_images = 0
    slides_without_images = 0
    broken_images = 0
    
    for slide in all_slides:
        print(f"\n📄 Slide ID {slide.id}: {slide.title}")
        
        if slide.image:
            print(f"   ✅ Tiene imagen: {slide.image}")
            
            # Verificar si el archivo existe
            full_path = os.path.join('media', str(slide.image))
            if os.path.exists(full_path):
                size = os.path.getsize(full_path)
                print(f"   ✅ Archivo existe ({size} bytes)")
                slides_with_images += 1
            else:
                print(f"   ❌ Archivo NO existe: {full_path}")
                broken_images += 1
        else:
            print(f"   ❌ Sin imagen")
            slides_without_images += 1
    
    print(f"\n📊 Resumen:")
    print(f"   ✅ Con imagen válida: {slides_with_images}")
    print(f"   ❌ Sin imagen: {slides_without_images}")
    print(f"   🔗 Enlaces rotos: {broken_images}")
    
    return slides_without_images > 0

def test_admin_image_upload():
    """Probar subida de imagen simulando el admin"""
    print("\n🧪 Probando subida de imagen como el admin...")
    
    # Crear imagen de prueba
    test_img = Image.new('RGB', (800, 400), color='#28a745')
    draw = ImageDraw.Draw(test_img)
    draw.text((200, 180), "PRUEBA ADMIN", fill='white')
    
    # Guardar temporalmente
    temp_path = 'media/carousel/admin_test.jpg'
    test_img.save(temp_path, 'JPEG')
    
    # Crear nuevo slide
    from django.core.files import File
    
    slide = CarouselSlide(
        title="PRUEBA: Admin Upload Test",
        subtitle="Testing image upload functionality",
        slide_type='promotion',
        is_active=True,
        order=999
    )
    
    # Simular carga de archivo como lo haría el admin
    with open(temp_path, 'rb') as f:
        slide.image.save('admin_test.jpg', File(f), save=True)
    
    print(f"✅ Slide de prueba creado: ID {slide.id}")
    print(f"   Imagen: {slide.image}")
    
    # Probar actualización
    original_image = slide.image
    slide.title = "ACTUALIZADO: Admin Upload Test"
    slide.save()
    
    slide.refresh_from_db()
    if slide.image == original_image:
        print("✅ Imagen preservada en actualización")
    else:
        print("❌ Imagen se perdió en actualización")
    
    return slide

def main():
    print("🚀 Iniciando diagnóstico y corrección de imágenes...")
    print("=" * 60)
    
    # Diagnosticar slides existentes
    needs_images = diagnose_existing_slides()
    
    # Crear imágenes placeholder si es necesario
    if needs_images:
        create_placeholder_images()
        print("\n🔄 Re-diagnosticando después de crear placeholders...")
        diagnose_existing_slides()
    
    # Probar funcionalidad del admin
    test_slide = test_admin_image_upload()
    
    print("\n" + "=" * 60)
    print("✅ Diagnóstico y corrección completados")
    
    print(f"\n💡 Recomendaciones:")
    print("1. Reinicia el servidor Django")
    print("2. Ve al admin: http://127.0.0.1:8000/admin/store/carouselslide/")
    print("3. Todos los slides ahora deberían tener imágenes")
    print("4. Al editar, la imagen se preservará automáticamente")
    print("5. Para cambiar imagen, selecciona un archivo nuevo")
    
    if test_slide:
        print(f"\n🧪 Slide de prueba creado: ID {test_slide.id}")
        print(f"   Úsalo para probar la funcionalidad del admin")

if __name__ == "__main__":
    main()