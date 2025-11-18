#!/usr/bin/env python
"""
Script para borrar todas las órdenes y reiniciar el conteo completamente
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from store.models import *
from django.contrib.auth.models import User
from django.db import connection

def main():
    print("🗑️ BORRANDO TODAS LAS ÓRDENES Y REINICIANDO CONTEO")
    print("=" * 60)
    
    # Mostrar estado antes del borrado
    print("📊 Estado antes del borrado:")
    print(f"   Total órdenes: {Order.objects.count()}")
    print(f"   OrderItems: {OrderItem.objects.count()}")
    print(f"   ShippingAddresses: {ShippingAddress.objects.count()}")
    print(f"   OrderHistory: {OrderHistory.objects.count()}")
    
    # Confirmar acción
    print("\n⚠️  ATENCIÓN: Esta operación:")
    print("   ✗ Eliminará TODAS las órdenes")
    print("   ✗ Eliminará TODOS los items de órdenes")
    print("   ✗ Eliminará TODAS las direcciones de envío")
    print("   ✗ Eliminará TODO el historial de órdenes")
    print("   ✗ Reiniciará el contador de IDs de órdenes a 1")
    print("   ✓ Mantendrá clientes, productos y direcciones guardadas")
    
    # Realizar limpieza completa
    print("\n🔄 Iniciando borrado completo...")
    
    try:
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
        
        # 5. Reiniciar el contador de auto-incremento
        print("\n🔄 Reiniciando contador de IDs...")
        with connection.cursor() as cursor:
            # Para SQLite
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='store_order';")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='store_orderitem';")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='store_orderhistory';")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='store_shippingaddress';")
        print("   ✅ Contadores de ID reiniciados")
        
        # Verificar limpieza
        print("\n🔍 Verificando limpieza completa:")
        print(f"   Órdenes restantes: {Order.objects.count()}")
        print(f"   OrderItems restantes: {OrderItem.objects.count()}")
        print(f"   ShippingAddresses restantes: {ShippingAddress.objects.count()}")
        print(f"   OrderHistory restantes: {OrderHistory.objects.count()}")
        
        # Mostrar lo que se mantiene
        print("\n📋 Datos que se conservan:")
        print(f"   Clientes: {Customer.objects.count()}")
        print(f"   Usuarios: {User.objects.count()}")
        print(f"   Productos: {Product.objects.count()}")
        print(f"   Direcciones de clientes: {CustomerAddress.objects.count()}")
        
        # Mostrar clientes activos
        print("\n👥 Clientes disponibles para nuevos pedidos:")
        for customer in Customer.objects.all():
            addresses_count = customer.addresses.count()
            status = "✅ Listo" if addresses_count > 0 else "⚠️ Necesita dirección"
            print(f"   • {customer.name} ({customer.email}) - {addresses_count} direcciones - {status}")
        
        print("\n✅ BORRADO COMPLETO EXITOSO!")
        print("🎯 El próximo pedido será #1")
        print("🛒 El sistema está listo para recibir nuevos pedidos")
        
    except Exception as e:
        print(f"\n❌ Error durante el borrado: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()