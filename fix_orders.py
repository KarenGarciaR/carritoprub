#!/usr/bin/env python
"""
Script para limpiar y corregir datos de órdenes
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from store.models import Order, Customer, OrderHistory

def fix_orders():
    print("🔧 Iniciando limpieza de órdenes...")
    
    # 1. Corregir estados inválidos
    print("\n1️⃣ Corrigiendo estados inválidos...")
    invalid_orders = Order.objects.exclude(
        status__in=['Pendiente', 'Procesando', 'Enviado', 'Entregado', 'Cancelado']
    )
    
    for order in invalid_orders:
        old_status = order.status
        if 'Reembolso' in order.status:
            order.status = 'Cancelado'
        else:
            order.status = 'Pendiente'
        order.save()
        print(f"   Orden #{order.id}: {old_status} → {order.status}")
    
    # 2. Verificar órdenes sin cliente
    print("\n2️⃣ Verificando órdenes sin cliente...")
    orders_without_customer = Order.objects.filter(customer__isnull=True)
    print(f"   Órdenes sin cliente: {orders_without_customer.count()}")
    
    # 3. Mostrar estadísticas finales
    print("\n📊 Estadísticas finales:")
    total_orders = Order.objects.count()
    complete_orders = Order.objects.filter(complete=True).count()
    orders_with_items = Order.objects.filter(orderitem__isnull=False).distinct().count()
    
    print(f"   Total de órdenes: {total_orders}")
    print(f"   Órdenes completadas: {complete_orders}")
    print(f"   Órdenes con productos: {orders_with_items}")
    
    # 4. Mostrar órdenes por estado
    print("\n📈 Órdenes por estado:")
    for status_code, status_name in Order.STATUS_CHOICES:
        count = Order.objects.filter(status=status_code).count()
        print(f"   {status_name}: {count}")

if __name__ == "__main__":
    fix_orders()
    print("\n✅ Limpieza completada!")