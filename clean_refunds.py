#!/usr/bin/env python
"""
Script para limpiar reembolsos de prueba
"""
import os
import sys
import django

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from store.models import *

def clean_refunds():
    """Limpiar todos los reembolsos de prueba"""
    
    print("🧹 Limpiando reembolsos existentes...")
    
    refunds = Refund.objects.all()
    count = refunds.count()
    
    if count > 0:
        refunds.delete()
        print(f"✅ {count} reembolsos eliminados")
    else:
        print("✅ No hay reembolsos para limpiar")

if __name__ == '__main__':
    clean_refunds()