#!/usr/bin/env python
"""
Script para limpiar órdenes duplicadas y vacías
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from store.models import *
from django.contrib.auth.models import User

def main():
    print("🧹 Limpiando órdenes duplicadas y vacías...")
    
    # 1. Eliminar órdenes vacías (sin items)
    empty_orders = Order.objects.filter(orderitem__isnull=True)
    empty_count = empty_orders.count()
    if empty_count > 0:
        print(f"   Eliminando {empty_count} órdenes vacías...")
        for order in empty_orders:
            print(f"      - Orden #{order.id} (Cliente: {order.customer.name if order.customer else 'None'})")
        empty_orders.delete()
    else:
        print("   ✅ No hay órdenes vacías")
    
    # 2. Verificar órdenes por cliente
    print("\n🔍 Verificando órdenes por cliente...")
    customers = Customer.objects.all()
    for customer in customers:
        incomplete_orders = Order.objects.filter(customer=customer, complete=False)
        if incomplete_orders.count() > 1:
            print(f"   ⚠️ Cliente {customer.name} tiene {incomplete_orders.count()} carritos activos")
            # Consolidar en una sola orden
            main_order = incomplete_orders.first()
            other_orders = incomplete_orders[1:]
            
            for order in other_orders:
                # Mover items a la orden principal
                for item in order.orderitem_set.all():
                    existing_item = OrderItem.objects.filter(order=main_order, product=item.product).first()
                    if existing_item:
                        existing_item.quantity += item.quantity
                        existing_item.save()
                    else:
                        item.order = main_order
                        item.save()
                order.delete()
            print(f"      ✅ Consolidado en orden #{main_order.id}")
    
    # 3. Arreglar estados incorrectos
    print("\n🔧 Corrigiendo estados...")
    # Órdenes completadas deben tener status diferente a 'Pendiente'
    completed_pending = Order.objects.filter(complete=True, status='Pendiente')
    for order in completed_pending:
        order.status = 'Procesando'
        order.save()
        print(f"   ✅ Orden #{order.id} corregida: Complete=True, Status=Procesando")
    
    # 4. Verificar historial sin duplicados
    print(f"\n📋 Estado final:")
    print(f"   Total órdenes: {Order.objects.count()}")
    print(f"   Órdenes completadas: {Order.objects.filter(complete=True).count()}")
    print(f"   Órdenes activas: {Order.objects.filter(complete=False).count()}")
    print(f"   Historiales: {OrderHistory.objects.count()}")
    
    print(f"\n📦 Órdenes por cliente:")
    for customer in Customer.objects.all():
        completed = Order.objects.filter(customer=customer, complete=True).count()
        active = Order.objects.filter(customer=customer, complete=False).count()
        if completed > 0 or active > 0:
            print(f"   {customer.name}: {completed} completadas, {active} activas")

if __name__ == "__main__":
    main()