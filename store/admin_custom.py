from django.contrib.admin import AdminSite
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.utils.safestring import mark_safe
from .models import *
from .views import admin_dashboard

class CustomAdminSite(AdminSite):
    """
    Panel de administración personalizado para ALM Refaccionaria
    """
    site_header = 'ALM Refaccionaria - Administración'
    site_title = 'ALM Admin'
    index_title = 'Panel de Control'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(admin_dashboard), name='dashboard'),
        ]
        return custom_urls + urls
    
    @method_decorator(never_cache)
    @method_decorator(csrf_protect)
    @method_decorator(staff_member_required)
    def admin_view(self, view):
        """
        Wrapper para las vistas del admin personalizado
        """
        def wrapper(request, *args, **kwargs):
            return view(request, *args, **kwargs)
        wrapper.admin_site = self
        return wrapper
    
    def index(self, request, extra_context=None):
        """
        Página principal del admin con dashboard personalizado
        """
        return admin_dashboard(request)

# Crear instancia del admin personalizado
custom_admin_site = CustomAdminSite(name='custom_admin')