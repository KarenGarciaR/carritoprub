#!/usr/bin/env python
"""
Script para limpiar completamente las órdenes y empezar desde cero
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from store.models import *
from django.contrib.auth.models import User

def main():
    print("🧹 Limpieza completa de órdenes - EMPEZAR DESDE CERO")
    print("=" * 60)
    
    # Mostrar estado actual antes de limpiar
    print("📊 Estado antes de la limpieza:")
    print(f"   Total órdenes: {Order.objects.count()}")
    print(f"   OrderItems: {OrderItem.objects.count()}")
    print(f"   ShippingAddresses: {ShippingAddress.objects.count()}")
    print(f"   OrderHistory: {OrderHistory.objects.count()}")
    
    # Confirmar limpieza
    print("\n⚠️  ATENCIÓN: Esta operación eliminará TODAS las órdenes y datos relacionados")
    print("   - Todas las órdenes (completadas e incompletas)")
    print("   - Todos los items de órdenes")
    print("   - Todas las direcciones de envío de órdenes")
    print("   - Todo el historial de órdenes")
    print("   - Los clientes y sus direcciones se mantendrán")
    
    # Realizar limpieza
    print("\n🔄 Iniciando limpieza...")
    
    # 1. Eliminar OrderHistory
    history_count = OrderHistory.objects.count()
    OrderHistory.objects.all().delete()
    print(f"   ✅ Eliminados {history_count} registros de historial")
    
    # 2. Eliminar ShippingAddress
    shipping_count = ShippingAddress.objects.count()
    ShippingAddress.objects.all().delete()
    print(f"   ✅ Eliminadas {shipping_count} direcciones de envío")
    
    # 3. Eliminar OrderItem
    items_count = OrderItem.objects.count()
    OrderItem.objects.all().delete()
    print(f"   ✅ Eliminados {items_count} items de órdenes")
    
    # 4. Eliminar Order
    orders_count = Order.objects.count()
    Order.objects.all().delete()
    print(f"   ✅ Eliminadas {orders_count} órdenes")
    
    # Verificar limpieza
    print("\n🔍 Verificando limpieza:")
    print(f"   Órdenes restantes: {Order.objects.count()}")
    print(f"   OrderItems restantes: {OrderItem.objects.count()}")
    print(f"   ShippingAddresses restantes: {ShippingAddress.objects.count()}")
    print(f"   OrderHistory restantes: {OrderHistory.objects.count()}")
    
    # Mostrar lo que se mantiene
    print("\n📋 Datos que se mantienen:")
    print(f"   Clientes: {Customer.objects.count()}")
    print(f"   Usuarios: {User.objects.count()}")
    print(f"   Productos: {Product.objects.count()}")
    print(f"   Direcciones de clientes: {CustomerAddress.objects.count()}")
    
    # Mostrar clientes y sus direcciones
    print("\n👥 Clientes activos:")
    for customer in Customer.objects.all():
        addresses_count = customer.addresses.count()
        print(f"   • {customer.name} ({customer.email}) - {addresses_count} direcciones guardadas")
    
    print("\n✅ Limpieza completada!")
    print("🎯 El sistema está listo para recibir nuevos pedidos desde el #1")
    print("\n📝 Próximos pasos:")
    print("   1. Los clientes pueden hacer nuevos pedidos")
    print("   2. Las órdenes comenzarán desde #1")
    print("   3. Los estados se pueden cambiar desde el admin")
    print("   4. Los clientes verán el progreso de sus pedidos")

if __name__ == "__main__":
    main()