#!/usr/bin/env python
"""
Script para optimizar el checkout eliminando duplicación de datos
y mejorar la numeración de órdenes
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from store.models import *
from django.contrib.auth.models import User
from django.db import transaction

def main():
    print("🔧 Optimizando sistema de checkout...")
    
    # 1. Limpiar órdenes huérfanas (sin cliente)
    print("\n1️⃣ Limpiando órdenes sin cliente...")
    orphan_orders = Order.objects.filter(customer__isnull=True)
    orphan_count = orphan_orders.count()
    
    if orphan_count > 0:
        print(f"   Encontradas {orphan_count} órdenes sin cliente")
        # Eliminar órdenes vacías huérfanas
        empty_orphans = orphan_orders.filter(orderitem__isnull=True)
        deleted_count = empty_orphans.count()
        empty_orphans.delete()
        print(f"   Eliminadas {deleted_count} órdenes vacías huérfanas")
        
        # Para órdenes con productos pero sin cliente, necesitamos decidir qué hacer
        remaining_orphans = Order.objects.filter(customer__isnull=True)
        if remaining_orphans.exists():
            print(f"   ⚠️ Quedan {remaining_orphans.count()} órdenes con productos pero sin cliente")
            print("   Estas necesitan revisión manual")
    else:
        print("   ✅ No hay órdenes huérfanas")
    
    # 2. Crear direcciones por defecto para clientes que no las tienen
    print("\n2️⃣ Creando direcciones por defecto...")
    customers_without_addresses = Customer.objects.filter(addresses__isnull=True).distinct()
    created_addresses = 0
    
    for customer in customers_without_addresses:
        if customer.address:  # Si tiene dirección en su perfil
            try:
                CustomerAddress.objects.create(
                    customer=customer,
                    nickname="Mi Dirección Principal",
                    full_name=customer.name or customer.user.get_full_name() or customer.user.username,
                    phone=customer.phone_number or "",
                    address=customer.address,
                    neighborhood="",
                    city=customer.municipality or "",
                    state=customer.state or "NLE",
                    zipcode=customer.zip_code or "",
                    references=customer.referencias or "",
                    is_default=True
                )
                created_addresses += 1
                print(f"   Creada dirección para {customer.name}")
            except Exception as e:
                print(f"   ❌ Error creando dirección para {customer.name}: {e}")
    
    print(f"   ✅ Creadas {created_addresses} direcciones por defecto")
    
    # 3. Verificar integridad de órdenes activas
    print("\n3️⃣ Verificando integridad de órdenes...")
    active_orders = Order.objects.filter(complete=False)
    print(f"   Órdenes activas (carritos): {active_orders.count()}")
    
    completed_orders = Order.objects.filter(complete=True)
    print(f"   Órdenes completadas: {completed_orders.count()}")
    
    # 4. Verificar que cada cliente tenga solo una orden activa
    print("\n4️⃣ Verificando órdenes activas por cliente...")
    customers_with_multiple_active = []
    
    for customer in Customer.objects.all():
        active_orders_count = Order.objects.filter(customer=customer, complete=False).count()
        if active_orders_count > 1:
            customers_with_multiple_active.append((customer, active_orders_count))
    
    if customers_with_multiple_active:
        print(f"   ⚠️ {len(customers_with_multiple_active)} clientes con múltiples carritos activos:")
        for customer, count in customers_with_multiple_active:
            print(f"     - {customer.name}: {count} carritos")
            
            # Consolidar en una sola orden
            active_orders = Order.objects.filter(customer=customer, complete=False).order_by('id')
            main_order = active_orders.first()
            other_orders = active_orders[1:]
            
            # Mover todos los items a la orden principal
            for order in other_orders:
                OrderItem.objects.filter(order=order).update(order=main_order)
                order.delete()
            
            print(f"     ✅ Consolidado en orden #{main_order.id}")
    else:
        print("   ✅ Todos los clientes tienen máximo un carrito activo")
    
    # 5. Estadísticas finales
    print("\n📊 Estadísticas finales:")
    print(f"   Total clientes: {Customer.objects.count()}")
    print(f"   Clientes con direcciones: {Customer.objects.filter(addresses__isnull=False).distinct().count()}")
    print(f"   Total órdenes: {Order.objects.count()}")
    print(f"   Órdenes completadas: {Order.objects.filter(complete=True).count()}")
    print(f"   Órdenes activas: {Order.objects.filter(complete=False).count()}")
    
    print("\n✅ Optimización completada!")

if __name__ == "__main__":
    main()