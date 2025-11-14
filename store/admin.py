from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Q
from .models import *
import datetime

# Configuración del sitio de administración
admin.site.site_header = "🚗 ALM Refaccionaria - Panel de Administración"
admin.site.site_title = "ALM Admin"
admin.site.index_title = "Gestión de E-commerce"

# Filtros personalizados
class OrderDateFilter(admin.SimpleListFilter):
    title = 'Fecha de pedido'
    parameter_name = 'date_range'

    def lookups(self, request, model_admin):
        return (
            ('today', 'Hoy'),
            ('week', 'Esta semana'),
            ('month', 'Este mes'),
            ('pending', 'Pendientes'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'today':
            return queryset.filter(date_ordered__date=datetime.date.today())
        elif self.value() == 'week':
            start_week = datetime.date.today() - datetime.timedelta(days=7)
            return queryset.filter(date_ordered__date__gte=start_week)
        elif self.value() == 'month':
            start_month = datetime.date.today() - datetime.timedelta(days=30)
            return queryset.filter(date_ordered__date__gte=start_month)
        elif self.value() == 'pending':
            return queryset.filter(complete=False)

# Admin para Customer
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'user', 'phone_number', 'total_orders', 'last_order']
    list_filter = ['user__date_joined']
    search_fields = ['name', 'email', 'user__username']
    readonly_fields = ['user']
    
    def total_orders(self, obj):
        return obj.order_set.filter(complete=True).count()
    total_orders.short_description = 'Total Pedidos'
    
    def last_order(self, obj):
        last = obj.order_set.filter(complete=True).order_by('-date_ordered').first()
        if last:
            return last.date_ordered.strftime('%d/%m/%Y')
        return 'Sin pedidos'
    last_order.short_description = 'Último Pedido'

# Admin para Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'quantity', 'stock_status', 'category', 'seller', 'product_image']
    list_filter = ['category', 'seller', 'date_of_delivery', 'material']
    search_fields = ['name', 'description']
    list_editable = ['price', 'quantity']
    ordering = ['-id']
    
    def stock_status(self, obj):
        if obj.quantity <= 0:
            return format_html('<span style="color: red; font-weight: bold;">Sin Stock</span>')
        elif obj.quantity <= 5:
            return format_html('<span style="color: orange; font-weight: bold;">Stock Bajo</span>')
        else:
            return format_html('<span style="color: green; font-weight: bold;">En Stock</span>')
    stock_status.short_description = 'Estado de Stock'
    
    def product_image(self, obj):
        if obj.imageURL:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 5px;" />',
                obj.imageURL
            )
        return "Sin imagen"
    product_image.short_description = 'Imagen'

# Inline para OrderItem
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['get_total']
    
    def get_total(self, obj):
        return f"${obj.get_total:.2f}"
    get_total.short_description = 'Total Item'

# Inline para ShippingAddress
class ShippingAddressInline(admin.StackedInline):
    model = ShippingAddress
    extra = 0

# Admin para Order
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_info', 'order_total', 'status_badge', 'payment_method_display', 'complete', 'date_ordered', 'order_actions']
    list_filter = [OrderDateFilter, 'complete', 'status']
    search_fields = ['customer__name', 'customer__email', 'transaction_id']
    list_per_page = 25
    inlines = [OrderItemInline, ShippingAddressInline]
    readonly_fields = ['transaction_id', 'date_ordered', 'get_cart_total', 'get_cart_items']
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('customer', 'complete', 'status', 'transaction_id', 'date_ordered')
        }),
        ('Resumen del Pedido', {
            'fields': ('get_cart_items', 'get_cart_total'),
            'classes': ('collapse',)
        }),
    )
    
    def customer_info(self, obj):
        if obj.customer:
            return format_html(
                '<strong>{}</strong><br><small>{}</small>',
                obj.customer.name or 'N/A',
                obj.customer.email or 'N/A'
            )
        return 'Invitado'
    customer_info.short_description = 'Cliente'
    
    def order_total(self, obj):
        return format_html('<strong>${:.2f}</strong>', obj.get_cart_total_with_iva)
    order_total.short_description = 'Total (IVA inc.)'
    
    def status_badge(self, obj):
        # Mapear estados de Order (español) a colores
        status_colors = {
            'Pendiente': '#ffc107',
            'Procesando': '#17a2b8', 
            'Enviado': '#007bff',
            'Entregado': '#28a745',
            'Cancelado': '#dc3545'
        }
        color = status_colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def payment_method_display(self, obj):
        # Buscar el método de pago en OrderHistory
        history = OrderHistory.objects.filter(order=obj).first()
        if history:
            methods = {
                'bank-transfer': '🏦 Transferencia',
                'card-payment': '💳 Tarjeta',
                'online-payment': '📱 En Línea',
                'bank-deposit': '💰 Depósito'
            }
            return methods.get(history.payment_method, history.payment_method)
        return 'N/A'
    payment_method_display.short_description = 'Método de Pago'
    
    def order_actions(self, obj):
        history_url = reverse('admin:store_orderhistory_changelist') + f'?order__id__exact={obj.id}'
        return format_html(
            '<a href="{}" class="button" style="background: #007bff; color: white; padding: 5px 10px; border-radius: 3px; text-decoration: none;">Ver Historial</a>',
            history_url
        )
    order_actions.short_description = 'Acciones'

# Admin para OrderHistory
@admin.register(OrderHistory)
class OrderHistoryAdmin(admin.ModelAdmin):
    list_display = ['order_info', 'customer_name', 'status', 'status_badge', 'payment_method_badge', 'created_at', 'quick_actions']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order__customer__name', 'order__customer__email', 'order__transaction_id']
    list_editable = ['status']
    ordering = ['-created_at']
    
    def order_info(self, obj):
        return format_html(
            '<strong>Pedido #{}</strong><br><small>ID Trans: {}</small>',
            obj.order.id,
            obj.order.transaction_id or 'N/A'
        )
    order_info.short_description = 'Pedido'
    
    def customer_name(self, obj):
        if obj.customer:
            return obj.customer.name
        elif obj.order.customer:
            return obj.order.customer.name
        return 'Invitado'
    customer_name.short_description = 'Cliente'
    
    def status_badge(self, obj):
        status_colors = {
            'pending': '#ffc107',
            'processing': '#17a2b8',
            'shipped': '#007bff', 
            'delivered': '#28a745',
            'cancelled': '#dc3545'
        }
        color = status_colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def payment_method_badge(self, obj):
        method_info = {
            'bank-transfer': ('🏦', 'Transferencia', '#2c3e50'),
            'card-payment': ('💳', 'Tarjeta', '#e74c3c'),
            'online-payment': ('📱', 'En Línea', '#3498db'),
            'bank-deposit': ('💰', 'Depósito', '#27ae60')
        }
        icon, name, color = method_info.get(obj.payment_method, ('❓', obj.payment_method, '#6c757d'))
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px;">{} {}</span>',
            color,
            icon,
            name
        )
    payment_method_badge.short_description = 'Método de Pago'
    
    def quick_actions(self, obj):
        actions = []
        if obj.status == 'pending':
            actions.append('<button onclick="updateStatus({}, \'processing\')" style="background: #17a2b8; color: white; border: none; padding: 3px 6px; border-radius: 3px; cursor: pointer;">Procesar</button>'.format(obj.id))
        elif obj.status == 'processing':
            actions.append('<button onclick="updateStatus({}, \'shipped\')" style="background: #007bff; color: white; border: none; padding: 3px 6px; border-radius: 3px; cursor: pointer;">Enviar</button>'.format(obj.id))
        elif obj.status == 'shipped':
            actions.append('<button onclick="updateStatus({}, \'delivered\')" style="background: #28a745; color: white; border: none; padding: 3px 6px; border-radius: 3px; cursor: pointer;">Entregar</button>'.format(obj.id))
        
        return format_html(' '.join(actions))
    quick_actions.short_description = 'Acciones Rápidas'
    
    class Media:
        js = ('admin/js/order_status_updater.js',)

# Admin para OrderItem
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'order', 'quantity', 'get_total', 'date_added']
    list_filter = ['date_added', 'product__category']
    search_fields = ['product__name', 'order__customer__name']

# Admin para ShippingAddress
@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'order', 'city', 'state', 'zipcode', 'date_added']
    list_filter = ['state', 'city', 'date_added']
    search_fields = ['customer__name', 'address', 'city']