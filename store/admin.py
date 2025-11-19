from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Q
from django.utils import timezone
from .models import *
from .models import CarouselSlide  # Importación explícita
import datetime

# Importar admin específico del carrusel
try:
    from . import carousel_admin
    print("✅ Admin de carrusel importado correctamente")
except ImportError as e:
    print(f"❌ Error importando admin de carrusel: {e}")

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
        total = float(obj.get_total)
        return "${:.2f}".format(total)
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
        total = float(obj.get_cart_total_with_iva)
        return format_html('<strong>${}</strong>', "{:.2f}".format(total))
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
                'bank-deposit': '💰 Depósito',
                'online-payment': '💳 Pago en Línea'
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

# Acciones masivas para OrderHistory
def mark_as_processing(modeladmin, request, queryset):
    updated = queryset.update(status='processing')
    for order_history in queryset:
        order_history.order.status = 'Procesando'
        order_history.order.save()
    modeladmin.message_user(request, f'{updated} pedidos marcados como "Procesando".')
mark_as_processing.short_description = '🔄 Marcar como Procesando'

def mark_as_shipped(modeladmin, request, queryset):
    updated = queryset.update(status='shipped')
    for order_history in queryset:
        order_history.order.status = 'Enviado'
        order_history.order.save()
    modeladmin.message_user(request, f'{updated} pedidos marcados como "Enviado".')
mark_as_shipped.short_description = '🚚 Marcar como Enviado'

def mark_as_delivered(modeladmin, request, queryset):
    updated = queryset.update(status='delivered')
    for order_history in queryset:
        order_history.order.status = 'Entregado'
        order_history.order.complete = True
        order_history.order.save()
    modeladmin.message_user(request, f'{updated} pedidos marcados como "Entregado".')
mark_as_delivered.short_description = '✅ Marcar como Entregado'

# Admin para OrderHistory
@admin.register(OrderHistory)
class OrderHistoryAdmin(admin.ModelAdmin):
    list_display = ['order_info', 'customer_name', 'status', 'status_badge', 'payment_method_badge', 'created_at', 'quick_actions']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order__customer__name', 'order__customer__email', 'order__transaction_id']
    list_editable = ['status']
    ordering = ['-created_at']
    actions = [mark_as_processing, mark_as_shipped, mark_as_delivered]
    
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
            'bank-deposit': ('💰', 'Depósito', '#27ae60'),
            'online-payment': ('💳', 'Pago en Línea', '#3498db')
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
    
    def save_model(self, request, obj, form, change):
        """Sincronizar el estado del OrderHistory con el Order"""
        super().save_model(request, obj, form, change)
        # Actualizar el estado de la orden principal
        if obj.status == 'delivered':
            obj.order.status = 'Entregado'
            obj.order.complete = True
        elif obj.status == 'shipped':
            obj.order.status = 'Enviado'
        elif obj.status == 'processing':
            obj.order.status = 'Procesando'
        elif obj.status == 'pending':
            obj.order.status = 'Pendiente'
        elif obj.status == 'cancelled':
            obj.order.status = 'Cancelado'
        obj.order.save()
    
    class Media:
        js = ('admin/js/order_status_updater.js',)

# Admin para OrderItem
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'order', 'quantity', 'get_total', 'date_added']
    list_filter = ['date_added', 'product__category']
    search_fields = ['product__name', 'order__customer__name']

# Admin para CustomerAddress
@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'nickname', 'full_name', 'city', 'state', 'is_default', 'created_at']
    list_filter = ['is_default', 'state', 'city', 'created_at']
    search_fields = ['customer__name', 'customer__email', 'nickname', 'full_name', 'address', 'city']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('customer', 'nickname', 'full_name', 'phone', 'is_default')
        }),
        ('Dirección', {
            'fields': ('address', 'neighborhood', 'city', 'state', 'zipcode', 'references')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer')

# Admin para ShippingAddress
@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'order', 'get_customer_address', 'city', 'state', 'zipcode', 'date_added']
    list_filter = ['state', 'city', 'date_added']
    search_fields = ['customer__name', 'address', 'city', 'name']
    readonly_fields = ['date_added']
    
    def get_customer_address(self, obj):
        if obj.customer_address:
            return format_html(
                '<span style="color: #28a745;"><i class="fas fa-link"></i> {}</span>',
                obj.customer_address.nickname
            )
        return format_html('<span style="color: #6c757d;">Sin vincular</span>')
    get_customer_address.short_description = 'Dirección Cliente'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer', 'order', 'customer_address')

# Admin para Refund
@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_info', 'customer_name', 'refund_type_badge', 'refund_amount', 'status_badge', 'reason_display', 'requested_at', 'refund_actions']
    list_filter = ['status', 'refund_type', 'reason', 'requested_at']
    search_fields = ['order__customer__name', 'order__customer__email', 'order__id', 'customer_notes', 'admin_notes']
    list_per_page = 25
    readonly_fields = ['order', 'refund_amount', 'requested_at', 'processed_at']
    
    fieldsets = (
        ('Información del Reembolso', {
            'fields': ('order', 'refund_type', 'refund_amount', 'status', 'reason')
        }),
        ('Notas y Comentarios', {
            'fields': ('customer_notes', 'admin_notes'),
            'classes': ('wide',)
        }),
        ('Fechas', {
            'fields': ('requested_at', 'processed_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def order_info(self, obj):
        total = float(obj.order.get_cart_total_with_iva)
        return format_html(
            '<strong>Pedido #{}</strong><br><small>${}</small>',
            obj.order.id,
            "{:.2f}".format(total)
        )
    order_info.short_description = 'Pedido'
    
    def customer_name(self, obj):
        if obj.order.customer:
            return format_html(
                '<strong>{}</strong><br><small>{}</small>',
                obj.order.customer.name,
                obj.order.customer.email
            )
        return 'N/A'
    customer_name.short_description = 'Cliente'
    
    def refund_type_badge(self, obj):
        type_info = {
            'cancellation': ('🚫', 'Cancelación', '#ffc107'),
            'return_refund': ('↩️', 'Devolución', '#17a2b8')
        }
        icon, name, color = type_info.get(obj.refund_type, ('❓', obj.refund_type, '#6c757d'))
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{} {}</span>',
            color, icon, name
        )
    refund_type_badge.short_description = 'Tipo'
    
    def status_badge(self, obj):
        status_colors = {
            'pending': '#ffc107',
            'approved': '#28a745',
            'processing': '#17a2b8',
            'waiting_return': '#fd7e14',
            'product_received': '#20c997',
            'quality_check': '#6f42c1',
            'completed': '#198754',
            'rejected': '#dc3545'
        }
        color = status_colors.get(obj.status, '#6c757d')
        status_names = {
            'pending': 'Pendiente',
            'approved': 'Aprobado',
            'processing': 'Procesando',
            'waiting_return': 'Esperando Retorno',
            'product_received': 'Producto Recibido',
            'quality_check': 'Verificación',
            'completed': 'Completado',
            'rejected': 'Rechazado'
        }
        name = status_names.get(obj.status, obj.status)
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color, name
        )
    status_badge.short_description = 'Estado'
    
    def reason_display(self, obj):
        reasons = {
            'changed_mind': '🤔 Cambié de opinión',
            'wrong_product': '❌ Producto incorrecto',
            'defective': '⚠️ Defectuoso',
            'not_as_described': '📝 No como se describía',
            'damaged_shipping': '📦 Dañado en envío',
            'other': '❓ Otro motivo'
        }
        return reasons.get(obj.reason, obj.get_reason_display())
    reason_display.short_description = 'Motivo'
    
    def refund_actions(self, obj):
        actions = []
        if obj.status == 'pending':
            actions.append(f'<a href="/admin/process-refund/{obj.id}/" style="background: #28a745; color: white; padding: 3px 8px; border-radius: 3px; text-decoration: none; font-size: 11px;">✅ Aprobar</a>')
            actions.append(f'<a href="/admin/process-refund/{obj.id}/" style="background: #dc3545; color: white; padding: 3px 8px; border-radius: 3px; text-decoration: none; font-size: 11px;">❌ Rechazar</a>')
        elif obj.status in ['approved', 'processing', 'waiting_return', 'product_received', 'quality_check']:
            actions.append(f'<a href="/admin/process-refund/{obj.id}/" style="background: #007bff; color: white; padding: 3px 8px; border-radius: 3px; text-decoration: none; font-size: 11px;">⚙️ Procesar</a>')
        
        order_link = f'<a href="/store/order/{obj.order.id}/detail/" style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 3px; text-decoration: none; font-size: 11px;">👁️ Ver Pedido</a>'
        actions.append(order_link)
        
        return format_html(' '.join(actions))
    refund_actions.short_description = 'Acciones'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'order__customer')

# Acciones masivas para Refund
def approve_refunds(modeladmin, request, queryset):
    updated = 0
    for refund in queryset.filter(status='pending'):
        refund.status = 'approved'
        refund.save()
        updated += 1
    modeladmin.message_user(request, f'{updated} reembolsos aprobados.')
approve_refunds.short_description = '✅ Aprobar reembolsos seleccionados'

def reject_refunds(modeladmin, request, queryset):
    updated = 0
    for refund in queryset.filter(status='pending'):
        refund.status = 'rejected'
        refund.processed_at = timezone.now()
        refund.save()
        updated += 1
    modeladmin.message_user(request, f'{updated} reembolsos rechazados.')
reject_refunds.short_description = '❌ Rechazar reembolsos seleccionados'

# Agregar las acciones al admin
RefundAdmin.actions = [approve_refunds, reject_refunds]

# Admin para CarouselSlide - COMENTADO (se usa carousel_admin.py)
# class CarouselSlideAdmin(admin.ModelAdmin):
#     list_display = ['title', 'slide_type', 'is_active', 'order', 'created_at']
#     list_filter = ['slide_type', 'is_active', 'created_at']
#     search_fields = ['title', 'subtitle']
#     list_editable = ['is_active', 'order']
#     ordering = ['order', '-created_at']

# # Registro manual del admin
# try:
#     admin.site.register(CarouselSlide, CarouselSlideAdmin)
#     print("✅ CarouselSlide registrado correctamente en admin")
# except Exception as e:
#     print(f"❌ Error registrando CarouselSlide: {e}")