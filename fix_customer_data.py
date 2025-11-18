#!/usr/bin/env python
"""
Script para corregir clientes con datos vacíos y limpiar la base de datos
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from store.models import *
from django.contrib.auth.models import User

def main():
    print("🔧 Corrigiendo clientes con datos vacíos...")
    
    # Encontrar clientes con datos problemáticos
    empty_name_customers = Customer.objects.filter(name__isnull=True)
    empty_email_customers = Customer.objects.filter(email="")
    
    print(f"   Clientes con nombre vacío: {empty_name_customers.count()}")
    print(f"   Clientes con email vacío: {empty_email_customers.count()}")
    
    # Mostrar todos los clientes para análisis
    print("\n📋 Todos los clientes:")
    customers = Customer.objects.all()
    for customer in customers:
        print(f"   ID: {customer.id}, Name: '{customer.name}', Email: '{customer.email}', User: {customer.user}")
        
        # Contar órdenes asociadas
        orders_count = Order.objects.filter(customer=customer).count()
        completed_orders = Order.objects.filter(customer=customer, complete=True).count()
        print(f"      Órdenes: {orders_count} total, {completed_orders} completadas")
    
    # Intentar corregir clientes problemáticos
    print("\n🔄 Intentando correcciones...")
    
    for customer in customers:
        needs_update = False
        
        # Si no tiene nombre pero tiene usuario, usar el username
        if not customer.name and customer.user:
            customer.name = customer.user.username
            needs_update = True
            print(f"   ✅ Asignado nombre '{customer.user.username}' al cliente ID {customer.id}")
        
        # Si no tiene email pero tiene usuario, usar el email del usuario
        if not customer.email and customer.user:
            customer.email = customer.user.email
            needs_update = True
            print(f"   ✅ Asignado email '{customer.user.email}' al cliente ID {customer.id}")
        
        # Si aún no tiene datos válidos
        if not customer.name:
            customer.name = f"Cliente #{customer.id}"
            needs_update = True
            print(f"   ⚠️ Asignado nombre genérico al cliente ID {customer.id}")
        
        if not customer.email:
            customer.email = f"cliente{customer.id}@temp.com"
            needs_update = True
            print(f"   ⚠️ Asignado email temporal al cliente ID {customer.id}")
        
        if needs_update:
            customer.save()
    
    # Verificar si hay clientes duplicados o que se puedan consolidar
    print("\n🔍 Verificando duplicados...")
    users_with_multiple_customers = User.objects.filter(customer__isnull=False).annotate(
        customer_count=models.Count('customer')
    ).filter(customer_count__gt=1)
    
    if users_with_multiple_customers.exists():
        print(f"   ⚠️ {users_with_multiple_customers.count()} usuarios con múltiples perfiles de cliente")
        for user in users_with_multiple_customers:
            print(f"      Usuario {user.username} tiene {user.customer_count} perfiles")
    else:
        print("   ✅ No hay usuarios con múltiples perfiles")
    
    # Estadísticas finales
    print("\n📊 Estadísticas finales:")
    print(f"   Total clientes: {Customer.objects.count()}")
    print(f"   Clientes con órdenes: {Customer.objects.filter(order__isnull=False).distinct().count()}")
    
    # Mostrar distribución de órdenes por cliente
    print("\n📦 Órdenes por cliente (después de corrección):")
    for customer in Customer.objects.all():
        completed_count = Order.objects.filter(customer=customer, complete=True).count()
        active_count = Order.objects.filter(customer=customer, complete=False).count()
        if completed_count > 0 or active_count > 0:
            print(f"   {customer.name}: {completed_count} completadas, {active_count} activas")

if __name__ == "__main__":
    main()