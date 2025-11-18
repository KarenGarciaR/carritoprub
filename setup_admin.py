
"""
Script de inicialización para el admin mejorado de ALM Refaccionaria
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_admin():
    """Configurar y inicializar el admin mejorado"""
    
    print("🚀 Iniciando configuración del Admin Mejorado de ALM Refaccionaria...")
    
    # Aplicar migraciones si es necesario
    print("📦 Aplicando migraciones...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migraciones aplicadas correctamente")
    except Exception as e:
        print(f"⚠️  Error en migraciones: {e}")
    
    # Recopilar archivos estáticos
    print("📁 Recopilando archivos estáticos...")
    try:
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Archivos estáticos recopilados")
    except Exception as e:
        print(f"⚠️  Error en collectstatic: {e}")
    
    print("\n🎉 ¡Configuración completada!")
    print("\n📋 Características del Admin Mejorado:")
    print("   • 🎨 Interfaz moderna y responsiva")
    print("   • 📊 Dashboard con estadísticas en tiempo real")
    print("   • 🔄 Actualizaciones de estado de pedidos con un clic")
    print("   • 📦 Gestión avanzada de productos e inventario")
    print("   • 👥 Administración completa de clientes")
    print("   • 📈 Filtros y búsquedas avanzadas")
    print("   • 🎯 Acciones rápidas y navegación optimizada")
    
    print("\n🔗 Para acceder al admin:")
    print("   1. Ejecuta: python manage.py runserver")
    print("   2. Ve a: http://127.0.0.1:8000/admin/")
    print("   3. Inicia sesión con tu cuenta de superusuario")
    
    print("\n💡 Funciones principales:")
    print("   • Gestión de pedidos con estados: Pendiente → Procesando → Enviado → Entregado")
    print("   • Seguimiento de inventario con alertas de stock bajo")
    print("   • Historial completo de órdenes con métodos de pago")
    print("   • Dashboard personalizado con métricas importantes")
    
    print("\n🔧 Admin personalizado creado por:")
    print("   ALM Refaccionaria - Sistema de E-commerce v2.0")

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
    django.setup()
    setup_admin()