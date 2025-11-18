#!/usr/bin/env python
"""
Script para verificar y mostrar los números de pedido desde la perspectiva del cliente
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from store.models import *
from django.contrib.auth.models import User

def main():
    print("🔍 Verificando números de pedido por cliente...")
    
    # Verificar órdenes por cliente
    customers = Customer.objects.all()
    
    for customer in customers:
        print(f"\n👤 Cliente: {customer.name} ({customer.email})")
        
        # Órdenes completadas (pedidos reales)
        completed_orders = Order.objects.filter(customer=customer, complete=True).order_by('-id')
        active_orders = Order.objects.filter(customer=customer, complete=False).order_by('-id')
        
        print(f"   📦 Pedidos completados: {completed_orders.count()}")
        for order in completed_orders:
            items_count = order.orderitem_set.count()
            total = order.get_cart_total
            status = order.status
            print(f"      • Pedido #{order.id} - {items_count} items - ${total:.2f} - {status}")
        
        print(f"   🛒 Carritos activos: {active_orders.count()}")
        for order in active_orders:
            items_count = order.orderitem_set.count() 
            total = order.get_cart_total
            print(f"      • Carrito #{order.id} - {items_count} items - ${total:.2f}")
    
    # Verificar numeración general
    print(f"\n📊 Estadísticas de numeración:")
    last_order = Order.objects.all().order_by('-id').first()
    if last_order:
        print(f"   Último número de orden: #{last_order.id}")
    
    completed_orders = Order.objects.filter(complete=True).order_by('-id')[:5]
    print(f"   Últimos 5 pedidos completados:")
    for order in completed_orders:
        customer_name = order.customer.name if order.customer else "Sin cliente"
        print(f"      • #{order.id} - {customer_name} - {order.status}")

if __name__ == "__main__":
    main()