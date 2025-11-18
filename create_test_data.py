#!/usr/bin/env python
"""
Script para crear datos de prueba para el sistema de reembolsos
"""
import os
import sys
import django
from decimal import Decimal

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.contrib.auth.models import User
from store.models import *
from django.utils import timezone
import random

def create_test_data():
    """Crear datos de prueba para el sistema de reembolsos"""
    
    print("🚀 Creando datos de prueba para el sistema de reembolsos...")
    
    # 1. Crear usuario de prueba si no existe
    try:
        user = User.objects.get(username='cliente_test')
        print("✅ Usuario de prueba ya existe")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='cliente_test',
            email='cliente@test.com',
            password='test123',
            first_name='Cliente',
            last_name='Prueba'
        )
        print("✅ Usuario de prueba creado")
    
    # Crear usuario seller si no existe
    try:
        seller_user = User.objects.get(username='alm_seller')
        print("✅ Usuario vendedor ya existe")
    except User.DoesNotExist:
        seller_user = User.objects.create_user(
            username='alm_seller',
            email='seller@alm.com',
            password='seller123',
            first_name='ALM',
            last_name='Refaccionaria',
            is_staff=True
        )
        print("✅ Usuario vendedor creado")
    
    # 2. Crear customer si no existe
    try:
        customer = Customer.objects.get(user=user)
        print("✅ Customer ya existe")
    except Customer.DoesNotExist:
        customer = Customer.objects.create(
            user=user,
            name=f"{user.first_name} {user.last_name}",
            email=user.email,
            phone_number="+52 33 1234 5678"
        )
        print("✅ Customer creado")
    
    # 3. Usar productos existentes o crear si es necesario
    products = list(Product.objects.all()[:3])
    
    if not products:
        print("⚠️  No hay productos existentes. Creando productos simples...")
        # Si no hay productos, crear algunos básicos con todos los campos requeridos
        try:
            product1 = Product.objects.create(
                name='Filtro de Aceite Test',
                price=250.00,
                quantity=50,
                category='Filtros',
                description='Producto de prueba para sistema de reembolsos',
                seller=seller_user,
                height_cm=10.0,
                width_cm=10.0,
                weight_kg=0.5,
                length_cm=15.0,
                material='Metal',
                brand='Test Brand',
                compatibility='Universal',
                section='Motor'
            )
            products.append(product1)
            print(f"✅ Producto creado: {product1.name}")
        except Exception as e:
            print(f"⚠️  Error creando producto: {e}")
            print("ℹ️  Continuando sin productos...")
    else:
        print(f"✅ Usando {len(products)} productos existentes")
    
    # 4. Crear órdenes de prueba
    orders_created = 0
    for i in range(3):
        # Crear orden
        order = Order.objects.create(
            customer=customer,
            complete=True if i > 0 else False,  # La primera será pendiente
            transaction_id=f'TEST{1000 + i}',
            status='Entregado' if i > 1 else ('Enviado' if i > 0 else 'Pendiente')
        )
        
        # Agregar productos a la orden
        selected_products = random.sample(products, random.randint(1, 2))
        for product in selected_products:
            quantity = random.randint(1, 3)
            OrderItem.objects.create(
                product=product,
                order=order,
                quantity=quantity
            )
        
        # Crear historial de orden
        OrderHistory.objects.create(
            order=order,
            customer=customer,
            user=user,
            status='delivered' if i > 1 else ('shipped' if i > 0 else 'pending'),
            payment_method='bank-transfer'
        )
        
        orders_created += 1
        print(f"✅ Orden #{order.id} creada - Estado: {order.status}")
    
    print(f"\n📊 Resumen de datos creados:")
    print(f"   • Órdenes: {orders_created}")
    print(f"   • Productos: {len(products)}")
    print(f"   • Customer: {customer.name}")
    
    # 5. Mostrar instrucciones para pruebas
    print(f"\n🧪 Para probar el sistema de reembolsos:")
    print(f"   1. Inicia sesión como: cliente_test / test123")
    print(f"   2. Ve a 'Mi Historial de Pedidos'")
    print(f"   3. Haz clic en 'Ver Detalles' de cualquier pedido")
    print(f"   4. Prueba solicitar un reembolso")
    print(f"\n🔧 Para administradores:")
    print(f"   1. Ve a /store/admin/refunds/ para gestionar reembolsos")
    print(f"   2. O accede al admin de Django en /admin/")
    
    return True

if __name__ == '__main__':
    try:
        create_test_data()
        print("\n🎉 ¡Datos de prueba creados exitosamente!")
    except Exception as e:
        print(f"\n❌ Error al crear datos de prueba: {e}")
        import traceback
        traceback.print_exc()