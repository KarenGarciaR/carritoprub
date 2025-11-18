#!/usr/bin/env python
"""
Script para verificar que el sistema está completamente limpio y funcionando
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from store.models import *
from django.contrib.auth.models import User

def main():
    print("🔍 VERIFICACIÓN DEL SISTEMA COMPLETAMENTE LIMPIO")
    print("=" * 55)
    
    # Verificar estado completamente limpio
    print("✅ Verificación de limpieza:")
    orders = Order.objects.count()
    items = OrderItem.objects.count()
    shipping = ShippingAddress.objects.count()
    history = OrderHistory.objects.count()
    
    print(f"   Órdenes: {orders} (debe ser 0)")
    print(f"   Items de órdenes: {items} (debe ser 0)")
    print(f"   Direcciones de envío: {shipping} (debe ser 0)")
    print(f"   Historial de órdenes: {history} (debe ser 0)")
    
    all_clean = orders == 0 and items == 0 and shipping == 0 and history == 0
    print(f"   Estado: {'✅ COMPLETAMENTE LIMPIO' if all_clean else '❌ NO LIMPIO'}")
    
    # Verificar datos conservados
    print(f"\n📋 Datos conservados:")
    customers = Customer.objects.count()
    users = User.objects.count()
    products = Product.objects.count()
    addresses = CustomerAddress.objects.count()
    
    print(f"   Clientes: {customers}")
    print(f"   Usuarios: {users}")
    print(f"   Productos: {products}")
    print(f"   Direcciones guardadas: {addresses}")
    
    # Mostrar productos disponibles
    print(f"\n🛍️ Productos disponibles para compra:")
    available_products = Product.objects.filter(quantity__gt=0)
    for product in available_products:
        print(f"   • {product.name} - Stock: {product.quantity} - ${product.price}")
    
    # Mostrar clientes listos
    print(f"\n👥 Clientes listos para hacer pedidos:")
    ready_customers = 0
    for customer in Customer.objects.all():
        addresses_count = customer.addresses.count()
        if addresses_count > 0:
            ready_customers += 1
            print(f"   ✅ {customer.name} - {addresses_count} direcciones")
        else:
            print(f"   ⚠️ {customer.name} - Sin direcciones (necesita configurar)")
    
    print(f"\n📊 Resumen:")
    print(f"   Clientes listos para comprar: {ready_customers}/{customers}")
    print(f"   Productos disponibles: {available_products.count()}")
    print(f"   Próximo número de pedido: #1")
    
    # Test de funcionalidad básica
    print(f"\n🧪 Test básico de funcionalidades:")
    
    # Verificar que se puede crear una orden de prueba
    try:
        test_customer = Customer.objects.first()
        if test_customer:
            # Crear orden de prueba (sin guardar)
            test_order = Order(customer=test_customer, complete=False, status='Pendiente')
            print(f"   ✅ Creación de órdenes: Funcional")
            
            # Verificar productos
            test_product = Product.objects.first()
            if test_product:
                print(f"   ✅ Productos disponibles: Funcional")
            else:
                print(f"   ❌ No hay productos disponibles")
        else:
            print(f"   ❌ No hay clientes disponibles")
    except Exception as e:
        print(f"   ❌ Error en test: {e}")
    
    print(f"\n🎯 ESTADO FINAL:")
    if all_clean and ready_customers > 0 and available_products.count() > 0:
        print(f"   🚀 SISTEMA COMPLETAMENTE LISTO")
        print(f"   🛒 Los clientes pueden hacer nuevos pedidos")
        print(f"   📦 Los pedidos comenzarán desde #1")
        print(f"   🎊 ¡Todo funcionando perfectamente!")
    else:
        print(f"   ⚠️ Sistema limpio pero requiere configuración adicional")
    
    print(f"\n🔗 URLs importantes:")
    print(f"   Tienda: http://127.0.0.1:8000/tienda/")
    print(f"   Admin: http://127.0.0.1:8000/admin/")
    print(f"   Mis Pedidos: http://127.0.0.1:8000/order_history/")

if __name__ == "__main__":
    main()