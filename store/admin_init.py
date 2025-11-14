from django.contrib import admin
from django.contrib.admin import AdminSite
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path
from .models import *
from .admin import *

# Personalizar completamente el admin site
class CustomAdminSite(AdminSite):
    site_header = 'ALM Refaccionaria - Panel de Administración'
    site_title = 'ALM Admin'
    index_title = 'Gestión de E-commerce'
    
    def each_context(self, request):
        """Agregar contexto personalizado a todas las páginas del admin"""
        context = super().each_context(request)
        
        # Estadísticas para el dashboard
        context.update({
            'total_orders': Order.objects.filter(complete=True).count(),
            'pending_orders': Order.objects.filter(status='Pendiente').count(),
            'total_customers': Customer.objects.count(),
            'total_products': Product.objects.count(),
        })
        return context

# Reemplazar el admin site por defecto
admin.site = CustomAdminSite()

# Re-registrar todos los modelos con nuestras clases personalizadas
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderHistory, OrderHistoryAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(ShippingAddress, ShippingAddressAdmin)