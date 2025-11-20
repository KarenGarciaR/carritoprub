"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from store.views import custom_admin_index
from store import views 

# Personalizar el admin
admin.site.site_header = "🚗 ALM Refaccionaria - Panel de Administración"
admin.site.site_title = "ALM Admin"
admin.site.index_title = "Gestión de E-commerce"

# Sobrescribir la vista del índice del admin
admin.site.index_template = 'admin/index.html'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-custom/', custom_admin_index, name='custom_admin'),
    path('', include('store.urls')),
    path('branches/', views.branch_list, name='branch_list'),
    path('branches/<int:branch_id>/', views.branch_detail, name='branch_detail'),
    path('api/product/<int:product_id>/availability/', views.get_product_availability, name='product_availability'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)