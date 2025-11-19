#!/usr/bin/env python
"""
Script de diagnóstico para problemas de subida de imágenes en el admin
"""
import os
import django
import stat

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.conf import settings
from store.models import CarouselSlide

def check_directory_permissions():
    """Verificar permisos de directorios"""
    print("🔍 Verificando permisos de directorios...")
    
    directories = [
        settings.MEDIA_ROOT,
        os.path.join(settings.MEDIA_ROOT, 'carousel'),
        settings.STATIC_ROOT if hasattr(settings, 'STATIC_ROOT') else None,
    ]
    
    for directory in directories:
        if directory and os.path.exists(directory):
            # Obtener permisos
            permissions = oct(os.stat(directory).st_mode)[-3:]
            print(f"✅ {directory}: permisos {permissions}")
            
            # Verificar si se puede escribir
            if os.access(directory, os.W_OK):
                print(f"   ✅ Escritura permitida")
            else:
                print(f"   ❌ SIN permisos de escritura")
        else:
            print(f"❌ {directory}: NO EXISTE")

def check_django_settings():
    """Verificar configuración de Django"""
    print("\n🔍 Verificando configuración de Django...")
    
    print(f"MEDIA_URL: {settings.MEDIA_URL}")
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"DEBUG: {settings.DEBUG}")
    
    # Verificar que Pillow esté instalado
    try:
        from PIL import Image
        print("✅ Pillow está instalado correctamente")
    except ImportError:
        print("❌ Pillow NO está instalado")

def check_carousel_slides():
    """Verificar slides existentes"""
    print("\n🔍 Verificando slides de carrusel existentes...")
    
    slides = CarouselSlide.objects.all()
    print(f"Total de slides: {slides.count()}")
    
    for slide in slides:
        print(f"\n📄 Slide ID {slide.id}: {slide.title}")
        print(f"   - Imagen: {slide.image}")
        print(f"   - URL de imagen: {slide.image.url if slide.image else 'N/A'}")
        print(f"   - Activo: {slide.is_active}")
        
        if slide.image:
            image_path = os.path.join(settings.MEDIA_ROOT, str(slide.image))
            if os.path.exists(image_path):
                size = os.path.getsize(image_path)
                print(f"   - Archivo existe: ✅ ({size} bytes)")
            else:
                print(f"   - Archivo existe: ❌")

def test_image_creation():
    """Probar creación de imagen programáticamente"""
    print("\n🔍 Probando creación de imagen...")
    
    try:
        from PIL import Image, ImageDraw
        
        # Crear imagen simple
        img = Image.new('RGB', (400, 200), color='red')
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "Prueba de imagen", fill='white')
        
        # Guardar imagen
        test_path = os.path.join(settings.MEDIA_ROOT, 'carousel', 'diagnostic_test.jpg')
        img.save(test_path)
        
        if os.path.exists(test_path):
            print("✅ Imagen de prueba creada exitosamente")
            
            # Intentar crear slide
            slide = CarouselSlide(
                title="Prueba Diagnóstica",
                image=f'carousel/diagnostic_test.jpg'
            )
            slide.save()
            
            print(f"✅ Slide de prueba creado: ID {slide.id}")
            
            # Limpiar
            slide.delete()
            os.remove(test_path)
            print("✅ Prueba limpiada")
            
        else:
            print("❌ No se pudo crear la imagen de prueba")
            
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")

def check_admin_config():
    """Verificar configuración del admin"""
    print("\n🔍 Verificando configuración del admin...")
    
    try:
        from django.contrib import admin
        from store.models import CarouselSlide
        
        if CarouselSlide in admin.site._registry:
            print("✅ CarouselSlide está registrado en el admin")
            admin_class = admin.site._registry[CarouselSlide]
            print(f"   Clase admin: {admin_class.__class__.__name__}")
        else:
            print("❌ CarouselSlide NO está registrado en el admin")
            
    except Exception as e:
        print(f"❌ Error verificando admin: {e}")

def main():
    print("🚀 Iniciando diagnóstico de subida de imágenes...")
    print("=" * 60)
    
    check_directory_permissions()
    check_django_settings()
    check_carousel_slides()
    check_admin_config()
    test_image_creation()
    
    print("\n" + "=" * 60)
    print("🏁 Diagnóstico completado")
    
    print("\n💡 Si tienes problemas para subir imágenes en el admin:")
    print("1. Verifica que los permisos de carpetas sean correctos")
    print("2. Asegúrate de que el archivo sea una imagen válida")
    print("3. Verifica que el archivo no sea demasiado grande (< 5MB)")
    print("4. Intenta con diferentes formatos (JPG, PNG)")
    print("5. Revisa la consola del navegador para errores JavaScript")

if __name__ == "__main__":
    main()