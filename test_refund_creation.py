#!/usr/bin/env python
"""
Script para probar la creación de reembolsos directamente
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

from store.models import *

def test_refund_creation():
    """Probar crear un reembolso directamente"""
    
    print("🧪 Probando creación de reembolso...")
    
    # Obtener la primera orden
    try:
        order = Order.objects.first()
        if not order:
            print("❌ No hay órdenes en la base de datos")
            return
        
        print(f"✅ Orden encontrada: #{order.id}")
        print(f"   Cliente: {order.customer.name if order.customer else 'N/A'}")
        print(f"   Total: ${order.get_cart_total_with_iva}")
        
        # Verificar si ya tiene reembolso
        if hasattr(order, 'refund') and order.refund:
            print(f"⚠️  La orden ya tiene un reembolso: #{order.refund.id}")
            return
        
        # Calcular montos
        base_amount = Decimal(str(order.get_cart_total_with_iva))
        refund_fee = Decimal('0.00')  # Cancelación simple
        final_refund_amount = base_amount
        
        print(f"💰 Montos calculados:")
        print(f"   Base: ${base_amount}")
        print(f"   Comisión: ${refund_fee}")
        print(f"   Final: ${final_refund_amount}")
        
        # Intentar crear el reembolso
        refund = Refund.objects.create(
            order=order,
            customer=order.customer,
            refund_type='cancellation',
            reason='changed_mind',
            customer_notes='Prueba desde script',
            status='pending',
            refund_amount=base_amount,
            refund_fee=refund_fee,
            final_refund_amount=final_refund_amount
        )
        
        print(f"✅ Reembolso creado exitosamente: #{refund.id}")
        print(f"   Tipo: {refund.get_refund_type_display()}")
        print(f"   Estado: {refund.get_status_display()}")
        print(f"   Monto: ${refund.refund_amount}")
        
    except Exception as e:
        print(f"❌ Error creando reembolso: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_refund_creation()