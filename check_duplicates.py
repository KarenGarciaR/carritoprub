#!/usr/bin/env python
"""
Script para verificar órdenes duplicadas
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from store.models import *
from django.contrib.auth.models import User

def main():
    print("🔍 Verificando órdenes duplicadas...")
    
    print("\n=== ÓRDENES RECIENTES ===")
    orders = Order.objects.all().order_by('-id')[:10]
    for order in orders:
        customer_name = order.customer.name if order.customer else "None"
        print(f"Orden #{order.id} - Cliente: {customer_name} - Complete: {order.complete} - Status: {order.status}")
    
    print("\n=== HISTORIALES ===")
    histories = OrderHistory.objects.all().order_by('-id')[:5]
    for history in histories:
        print(f"History #{history.id} - Orden: #{history.order.id} - Status: {history.status} - Payment: {history.payment_method}")
    
    # Buscar duplicados por cliente
    print("\n=== POSIBLES DUPLICADOS ===")
    customers = Customer.objects.all()
    for customer in customers:
        recent_orders = Order.objects.filter(customer=customer).order_by('-id')[:3]
        if recent_orders.count() > 1:
            print(f"\nCliente {customer.name}:")
            for order in recent_orders:
                items_count = order.orderitem_set.count()
                print(f"  - Orden #{order.id}: {items_count} items, Complete: {order.complete}, Status: {order.status}")

if __name__ == "__main__":
    main()