import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.contrib import admin
from store.models import CarouselSlide

def check_admin_registration():
    print("=== VERIFICACIÓN DEL ADMIN ===\n")
    
    # Verificar que el modelo existe
    try:
        slides_count = CarouselSlide.objects.count()
        print(f"✅ Modelo CarouselSlide encontrado con {slides_count} slides")
    except Exception as e:
        print(f"❌ Error con el modelo CarouselSlide: {e}")
        return
    
    # Verificar registro en admin
    print("\nModelos registrados en admin:")
    registered_models = list(admin.site._registry.keys())
    
    for model in registered_models:
        model_name = f"{model._meta.app_label}.{model._meta.model_name}"
        verbose_name = getattr(model._meta, 'verbose_name_plural', model._meta.model_name)
        print(f"  - {model_name}: {verbose_name}")
    
    # Verificar específicamente CarouselSlide
    if CarouselSlide in registered_models:
        print(f"\n✅ CarouselSlide está registrado en admin")
        admin_class = admin.site._registry[CarouselSlide]
        print(f"   Clase admin: {admin_class.__class__.__name__}")
    else:
        print(f"\n❌ CarouselSlide NO está registrado en admin")
        print("   Modelos de la app 'store' registrados:")
        store_models = [m for m in registered_models if m._meta.app_label == 'store']
        for model in store_models:
            print(f"     - {model._meta.model_name}")
    
    # Verificar URLs disponibles
    print(f"\nURLs del admin disponibles para la app 'store':")
    from django.urls import reverse
    for model in registered_models:
        if model._meta.app_label == 'store':
            try:
                url = reverse(f'admin:{model._meta.app_label}_{model._meta.model_name}_changelist')
                print(f"  - {model._meta.model_name}: {url}")
            except Exception as e:
                print(f"  - {model._meta.model_name}: Error al generar URL - {e}")

if __name__ == "__main__":
    check_admin_registration()