#!/usr/bin/env python
"""
Script para corregir órdenes sin cliente asignado
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from store.models import *
from django.contrib.auth.models import User

def main():
    print("🔧 Corrigiendo órdenes sin cliente...")
    
    # Encontrar órdenes sin cliente
    orphan_orders = Order.objects.filter(customer__isnull=True)
    print(f"   Órdenes sin cliente: {orphan_orders.count()}")
    
    if orphan_orders.count() == 0:
        print("   ✅ No hay órdenes sin cliente")
        return
    
    # Intentar asociar órdenes a clientes basándose en historial
    for order in orphan_orders:
        try:
            # Buscar en OrderHistory si hay un registro asociado
            history = OrderHistory.objects.filter(order=order).first()
            if history and history.customer:
                order.customer = history.customer
                order.save()
                print(f"   ✅ Orden #{order.id} asociada a {history.customer.name}")
                continue
            
            # Buscar en ShippingAddress
            shipping = ShippingAddress.objects.filter(order=order).first()
            if shipping and shipping.customer:
                order.customer = shipping.customer
                order.save()
                print(f"   ✅ Orden #{order.id} asociada a {shipping.customer.name}")
                continue
                
            # Si no se puede asociar, marcar para revisión
            print(f"   ⚠️ Orden #{order.id} no se pudo asociar automáticamente")
            
        except Exception as e:
            print(f"   ❌ Error procesando orden #{order.id}: {e}")
    
    # Estadísticas después de la corrección
    print(f"\n📊 Estadísticas después de la corrección:")
    remaining_orphans = Order.objects.filter(customer__isnull=True).count()
    print(f"   Órdenes sin cliente restantes: {remaining_orphans}")
    
    # Mostrar órdenes por cliente actualizadas
    customers = Customer.objects.all()
    for customer in customers:
        completed_count = Order.objects.filter(customer=customer, complete=True).count()
        if completed_count > 0:
            print(f"   {customer.name}: {completed_count} pedidos completados")

if __name__ == "__main__":
    main()