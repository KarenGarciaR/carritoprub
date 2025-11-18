#!/usr/bin/env python
"""
Script para probar el sistema de órdenes desde cero
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from store.models import *
from django.contrib.auth.models import User

def main():
    print("🧪 Pruebas del Sistema de Órdenes Limpio")
    print("=" * 50)
    
    # Verificar estado inicial
    print("📊 Estado inicial:")
    print(f"   Órdenes: {Order.objects.count()}")
    print(f"   OrderHistory: {OrderHistory.objects.count()}")
    print(f"   Clientes: {Customer.objects.count()}")
    print(f"   Productos: {Product.objects.count()}")
    
    # Verificar que los clientes tienen direcciones
    print("\n🏠 Direcciones de clientes:")
    for customer in Customer.objects.all():
        addresses_count = customer.addresses.count()
        print(f"   {customer.name}: {addresses_count} direcciones")
        if addresses_count == 0:
            print(f"      ⚠️ {customer.name} necesita al menos una dirección para hacer pedidos")
    
    # Verificar que hay productos disponibles
    print(f"\n📦 Productos disponibles: {Product.objects.filter(quantity__gt=0).count()}")
    for product in Product.objects.filter(quantity__gt=0):
        print(f"   • {product.name} - Stock: {product.quantity} - ${product.price}")
    
    # Instrucciones para pruebas
    print(f"\n✅ Sistema listo para pruebas!")
    print(f"\n📋 Pasos para probar:")
    print(f"   1. Inicia sesión como cliente")
    print(f"   2. Agrega productos al carrito")
    print(f"   3. Ve al checkout")
    print(f"   4. Completa el pedido")
    print(f"   5. Verifica que aparece con #1")
    print(f"   6. Ve al admin para cambiar estados")
    print(f"   7. Verifica que el cliente ve los cambios")
    
    print(f"\n👨‍💼 Clientes disponibles para pruebas:")
    users = User.objects.filter(customer__isnull=False)
    for user in users:
        customer = user.customer
        addresses = customer.addresses.count()
        print(f"   • Usuario: {user.username} | Cliente: {customer.name} | Direcciones: {addresses}")
    
    print(f"\n🛠️ URLs importantes:")
    print(f"   Admin: http://127.0.0.1:8000/admin/")
    print(f"   Tienda: http://127.0.0.1:8000/tienda/")
    print(f"   Mis Pedidos: http://127.0.0.1:8000/order_history/")
    print(f"   Checkout: http://127.0.0.1:8000/checkout/")

if __name__ == "__main__":
    main()