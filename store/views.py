from django.dispatch import receiver
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseForbidden, JsonResponse
import json
import datetime
from django.utils import timezone
from decimal import Decimal
from .models import * 
from .models import Branch, ProductBranch
from django.db.models import Sum, Count
from .utils import cookieCart, cartData, guestOrder
from .forms import ProductEditForm, SignupForm, LoginForm, CustomerAddressForm
from django.contrib.auth import logout as auth_logout
import openai
import os
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ProductForm, CustomerForm, OrderUpdateForm
from django.db.models.signals import post_save
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
import urllib.request
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST


# Create your views here.
# Home page
def index(request):
    """Página principal con carrusel y productos destacados"""
    data = cartData(request)
    cartItems = data['cartItems']
    
    # Obtener slides activos del carrusel
    carousel_slides = CarouselSlide.objects.filter(
        is_active=True
    ).order_by('order', '-created_at')
    
    # Filtrar slides visibles basado en fechas programadas
    visible_slides = [slide for slide in carousel_slides if slide.is_visible]
    
    # Obtener productos destacados (puedes filtrar por ofertas, más vendidos, etc.)
    products_destacados = Product.objects.filter(
        quantity__gt=0  # Solo productos con stock
    ).order_by('-id')[:8]  # Los 8 productos más recientes
    
    context = {
        'carousel_slides': visible_slides,
        'products_destacados': products_destacados,
        'cartItems': cartItems
    }
    return render(request, 'store/index.html', context)

def nosotros(request):
    """Página Nosotros/Acerca de"""
    data = cartData(request)
    cartItems = data['cartItems']
    
    context = {
        'cartItems': cartItems
    }
    return render(request, 'store/nosotros.html', context)

def contacto(request):
    """Página de Contacto"""
    data = cartData(request)
    cartItems = data['cartItems']
    
    if request.method == 'POST':
        # Procesar formulario de contacto
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        mensaje = request.POST.get('mensaje')
        
        # Aquí puedes agregar la lógica para enviar el mensaje
        # Por ejemplo, guardar en base de datos o enviar email
        
        messages.success(request, 'Tu mensaje ha sido enviado correctamente. Nos pondremos en contacto contigo pronto.')
        return redirect('contacto')
    
    context = {
        'cartItems': cartItems
    }
    return render(request, 'store/contacto.html', context)

# Peticiones personalizadas de los usuarios
@staff_member_required
def lista_personalizaciones(request):
    pedidos = Personalizacion.objects.all().order_by('-fecha_creacion')
    return render(request, 'store/admin_personalizacion.html', {'pedidos': pedidos})

@staff_member_required
def atender_personalizacion(request, pk):
    pedido = get_object_or_404(Personalizacion, pk=pk)
    # Marcar en progreso
    pedido.status = 'EN_PROGRESO'
    pedido.atendido_por = request.user
    pedido.save()
    messages.success(request, f'Solicitud #{pedido.pk} marcada como "En progreso".')
    return redirect('personalizacion')

@login_required
def personalizacion(request):
    # 1) Admin responde / cambia estado
    data = cartData(request)
    cartItems = data['cartItems']

    if request.method == 'POST' and 'pedido_id' in request.POST and request.user.is_staff:
        pid = request.POST['pedido_id']
        p = get_object_or_404(Personalizacion, pk=pid)
        p.status          = request.POST['status']
        p.respuesta_admin = request.POST['respuesta_admin']
        p.atendido_por    = request.user
        p.save()
        messages.success(request, f'Solicitud #{p.pk} actualizada.')
        return redirect('personalizacion')

    # 2) Cliente crea nueva solicitud
    if request.method == 'POST' and 'descripcion' in request.POST and not request.user.is_staff:
        descripcion = request.POST['descripcion']
        cliente     = getattr(request.user, 'customer', None)
        Personalizacion.objects.create(cliente=cliente,
                                       descripcion=descripcion)
        messages.success(request, 'Solicitud enviada.')
        return redirect('personalizacion')

    # 3) Cargar todas las solicitudes
    if request.user.is_staff:
        pedidos = Personalizacion.objects.all().order_by('-fecha_creacion')
    else:
        pedidos = Personalizacion.objects.filter(
            cliente__user=request.user
        ).order_by('-fecha_creacion')

    return render(request, 'store/personalizacion.html', {
        'pedidos': pedidos, 'cartItems': cartItems
    })

# Vistas de login y registro de usuarios
def user_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            customer = Customer.objects.create(user=user)
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'store/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_superuser:  # Si es admin
                    messages.success(request, "Bienvenido Administrador.")
                    return redirect('store')  # Lo rediriges a un panel de administrador
                else:
                    try:
                        customer = user.customer  # Solo si no es admin
                        messages.success(request, "Inicio de sesión exitoso.")
                        return redirect('store')
                    except Customer.DoesNotExist:
                        logout(request)
                        messages.error(request, "Tu cuenta no tiene perfil de cliente asociado.")
                        return redirect('login')
    else:
        form = LoginForm()
    return render(request, 'store/login.html', {'form': form})

def user_logout(request):
    auth_logout(request)
    messages.info(request, 'Session Deleted')
    return redirect('store')

@login_required
def profile(request):
    data = cartData(request)
    user = request.user
    cartItems = data['cartItems']
    
    try:
        customer = user.customer  # Usa la relación OneToOne
    except Customer.DoesNotExist:
        customer = None  # Por si el usuario es admin u otro sin Customer asociado

    return render(request, 'store/perfil.html', {
        'user': user,
        'customer': customer,
        'cartItems': cartItems
    })

@login_required
def edit_profile(request):
    user = request.user
    try:
        customer = user.customer
    except Customer.DoesNotExist:
        # Si el usuario no tiene Customer aún, lo creamos en blanco
        customer = Customer(user=user)

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Asegúrate de que 'profile' es el nombre de tu URL de perfil
    else:
        form = CustomerForm(instance=customer)

    return render(request, 'store/edit_profile.html', {'form': form})

# Vistas de logica de agregar, visualizar productos y pagar
@login_required
def order_history(request):
    data = cartData(request)
    cartItems = data['cartItems']

    if request.user.is_staff:
        # Admin ve todo el historial de órdenes
        order_histories = OrderHistory.objects.all().select_related('order', 'customer', 'user')
    else:
        # Cliente solo ve su historial de órdenes
        customer = None
        if request.user.is_authenticated:
            try:
                customer = Customer.objects.get(user=request.user)
            except Customer.DoesNotExist:
                pass
                
        if customer:
            order_histories = OrderHistory.objects.filter(customer=customer).select_related('order', 'customer')
        else:
            order_histories = OrderHistory.objects.none()
    
    return render(request, 'store/order_history.html', {
        'order_histories': order_histories, 
        'cartItems': cartItems
    })

@login_required
def add_product(request):
    data = cartData(request)
    cartItems = data['cartItems']
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user  # Asigna al usuario actual como el vendedor
            
            # Si el producto está en oferta, aseguramos que el precio de la oferta esté presente
            if product.offer:
                if not product.offer_price:
                    form.add_error('offer_price', 'Debe ingresar un precio de oferta si el producto está en oferta.')
                    return render(request, 'store/addProduct.html', {'form': form, 'cartItems': cartItems})
            
            product.save()
            return redirect('store')  # Redirige al perfil del usuario después de agregar el producto
    else:
        form = ProductForm(initial={'seller': request.user})  # Inicializa el formulario con el usuario actual

    return render(request, 'store/addProduct.html', {'form': form, 'cartItems': cartItems})
# Vistas de de historial de productos
@login_required
def product_history(request):
    data = cartData(request)
    cartItems = data['cartItems']
    user = request.user
    products = Product.objects.filter(seller=request.user)
    
    return render(request, 'store/productHistory.html', {'products': products, 'cartItems': cartItems})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer__user=request.user)

    # Estados que permiten cancelación
    cancelable_statuses = ["Pendiente", "Procesando"]
    
    if order.status in cancelable_statuses:
        # Solo permitir cancelación si el pedido está completo (fue pagado)
        if not order.complete:
            messages.error(request, "Este pedido aún no ha sido finalizado y no puede ser cancelado.")
            return redirect("order_history")
            
        # Si el pedido ya fue pagado (complete=True), requiere reembolso
        if order.complete:
            order.status = "Reembolso_Pendiente"
            order.refund_requested_date = timezone.now()
            
            # Obtener motivo de cancelación del POST
            order.refund_reason = request.POST.get('cancel_reason', 'Cliente solicitó cancelación')
            
            order.save()
            
            # Crear notificación para el usuario
            Notification.objects.create(
                user=request.user,
                message=f"Tu solicitud de reembolso para el pedido #{order.id} ha sido enviada. Los artículos deben ser devueltos para evaluación."
            )
            
            messages.success(request, 
                "Tu solicitud de reembolso ha sido enviada. "
                "Deberás devolver los artículos para que sean evaluados. "
                "El reembolso se procesará una vez confirmado el buen estado de los productos."
            )
            
    else:
        if order.status == "Cancelado":
            messages.info(request, "Este pedido ya está cancelado.")
        elif order.status == "Reembolso_Pendiente":
            messages.info(request, "Este pedido ya tiene un reembolso pendiente.")
        elif order.status == "Reembolsado":
            messages.info(request, "Este pedido ya fue reembolsado.")
        elif order.status in ["Enviado", "Entregado"]:
            messages.error(request, "No puedes cancelar un pedido que ya ha sido enviado o entregado.")
        else:
            messages.error(request, "Este pedido no se puede cancelar en su estado actual.")

    return redirect("order_history")

@staff_member_required
def process_refund(request, order_id):
    """Procesar reembolso - solo para administradores"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve' and order.status == 'Reembolso_Pendiente':
            # Restaurar stock
            for item in order.orderitem_set.all():
                if item.product:
                    item.product.quantity += item.quantity
                    item.product.save()
            
            # Actualizar orden
            order.status = 'Reembolsado'
            order.refund_processed_date = timezone.now()
            order.save()
            
            # Notificar al cliente
            Notification.objects.create(
                user=order.customer.user,
                message=f"Tu reembolso del pedido #{order.id} ha sido procesado exitosamente."
            )
            
            messages.success(request, f"Reembolso del pedido #{order.id} procesado exitosamente.")
            
        elif action == 'reject' and order.status == 'Reembolso_Pendiente':
            # Rechazar reembolso - volver a estado anterior
            reject_reason = request.POST.get('reject_reason', 'No especificado')
            order.status = 'Entregado'  # Asumir que ya fue entregado
            order.refund_reason += f"\n\nReembolso rechazado: {reject_reason}"
            order.save()
            
            # Notificar al cliente
            Notification.objects.create(
                user=order.customer.user,
                message=f"Tu solicitud de reembolso del pedido #{order.id} fue rechazada. Motivo: {reject_reason}"
            )
            
            messages.info(request, f"Solicitud de reembolso del pedido #{order.id} rechazada.")
    
    return redirect('admin_refunds')

@staff_member_required
def admin_refunds(request):
    """Lista de reembolsos pendientes para administradores"""
    data = cartData(request)
    cartItems = data['cartItems']
    
    pending_refunds = Order.objects.filter(status='Reembolso_Pendiente').order_by('-refund_requested_date')
    processed_refunds = Order.objects.filter(status='Reembolsado').order_by('-refund_processed_date')[:10]
    
    context = {
        'pending_refunds': pending_refunds,
        'processed_refunds': processed_refunds,
        'cartItems': cartItems
    }
    
    return render(request, 'store/admin_refunds.html', context)

@login_required
def clear_cart(request):
    """Vaciar carrito actual (cancelar pedido pendiente)"""
    try:
        customer = request.user.customer
        order = Order.objects.filter(customer=customer, complete=False).first()
        
        if order:
            # Restaurar stock
            for item in order.orderitem_set.all():
                if item.product:
                    item.product.quantity += item.quantity
                    item.product.save()
            
            # Eliminar items del carrito
            order.orderitem_set.all().delete()
            order.delete()
            
            messages.success(request, "Tu carrito ha sido vaciado y el stock restaurado.")
        else:
            messages.info(request, "No tienes un carrito activo.")
            
    except Customer.DoesNotExist:
        messages.error(request, "Error: No tienes un perfil de cliente asociado.")
    
    return redirect("cart")


# Vista de la tienda
def store(request):
    data = cartData(request)
    cartItems = data['cartItems']

    # Captura los filtros de la URL (GET)
    section = request.GET.get('section')  # p.ej: 'Animales'
    offer_only = request.GET.get('offer') == '1'  # '1' activa filtro de ofertas

    # Productos base
    products = Product.objects.all()

    # Aplicar filtros si existen
    if section:
        products = products.filter(category=section)

    if offer_only:
        products = products.filter(offer=True)

    context = {
        'products': products,
        'cartItems': cartItems,
        'current_section': section,
        'offer_only': offer_only,
        'sections': [choice[0] for choice in Product.CATEGORY_CHOICES],
    }
    return render(request, 'store/store.html', context)

def main(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/main.html', context)


def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    # Verifica si hay productos sin stock o si el stock es menor a la cantidad en el carrito
    has_out_of_stock = False
    insufficient_stock_items = []

    for item in items:
        if item.product.quantity == 0 or item.quantity > item.product.quantity:
            has_out_of_stock = True
            insufficient_stock_items.append({
                'product': item.product,
                'available': item.product.quantity,
                'requested': item.quantity,
            })

    notifications = []
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user, is_read=False)

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'has_out_of_stock': has_out_of_stock,
        'insufficient_stock_items': insufficient_stock_items,
        'notifications': notifications
    }
    return render(request, 'store/cart.html', context)

@receiver(post_save, sender=Product)
def notify_out_of_stock(sender, instance, **kwargs):
    if instance.quantity == 0:
        order_items = OrderItem.objects.filter(product=instance, order__complete=False)
        for item in order_items:
            user = item.order.customer.user
            # Solo crea la notificación si no existe aún para este usuario y producto agotado
            Notification.objects.create(
                user=user,
                message=f'El producto "{instance.name}" que tienes en tu carrito está agotado.'
            )


@login_required 
def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    customer = request.user.customer

    # Verificar que hay items en el carrito
    if not items:
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('cart')

    # Obtener direcciones del cliente
    customer_addresses = customer.addresses.all()
    address_form = CustomerAddressForm(customer=customer)
    
    # Si no tiene direcciones, crear una dirección temporal basada en su perfil
    if not customer_addresses.exists() and customer.address:
        # Crear una dirección por defecto desde los datos del cliente
        default_address = CustomerAddress.objects.create(
            customer=customer,
            nickname="Mi Casa",
            full_name=customer.name or customer.user.get_full_name() or customer.user.username,
            phone=customer.phone_number or "",
            address=customer.address,
            city=customer.municipality or "",
            state=customer.state or "NLE",
            zipcode=customer.zip_code or "",
            references=customer.referencias or "",
            is_default=True
        )
        customer_addresses = customer.addresses.all()

    if request.method == 'POST':
        try:
            # Check if it's an AJAX request with JSON data
            if request.content_type == 'application/json':
                import json
                data = json.loads(request.body)
                form_data = data.get('form', {})
                shipping_data = data.get('shipping', {})
                
                # Debug: Verificar qué datos llegan
                print(f"DEBUG - Procesando pago AJAX para orden {order.id}")
                print(f"DEBUG - Form data: {form_data}")
                print(f"DEBUG - Shipping data: {shipping_data}")
                
                # Obtener dirección seleccionada o crear nueva
                selected_address_id = shipping_data.get('selected_address')
                use_new_address = shipping_data.get('use_new_address', False)
                shipping_address = None
                
                if use_new_address:
                    # Crear nueva dirección desde datos AJAX
                    address_data = {
                        'nickname': shipping_data.get('nickname', ''),
                        'full_name': shipping_data.get('full_name', ''),
                        'phone': shipping_data.get('phone', ''),
                        'address': shipping_data.get('address', ''),
                        'neighborhood': shipping_data.get('neighborhood', ''),
                        'city': shipping_data.get('city', ''),
                        'state': shipping_data.get('state', ''),
                        'zipcode': shipping_data.get('zipcode', ''),
                        'references': shipping_data.get('references', ''),
                        'is_default': shipping_data.get('is_default', False),
                    }
                    address_form = CustomerAddressForm(address_data, customer=customer)
                    if address_form.is_valid():
                        new_address = address_form.save()
                        shipping_address = new_address
                    else:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Error en los datos de la nueva dirección.',
                            'errors': address_form.errors
                        })
                elif selected_address_id:
                    # Usar dirección existente
                    try:
                        shipping_address = customer.addresses.get(id=selected_address_id)
                    except CustomerAddress.DoesNotExist:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Dirección seleccionada no válida.'
                        })
                
                if not shipping_address:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Debes seleccionar una dirección de envío.'
                    })
                
                # Guardar método de pago
                payment_method = form_data.get('payment_method', 'bank-transfer')
            else:
                # Traditional form submission (fallback)
                print(f"DEBUG - Procesando pago tradicional para orden {order.id}")
                
                # Obtener dirección seleccionada o crear nueva
                selected_address_id = request.POST.get('selected_address')
                use_new_address = request.POST.get('use_new_address')
                shipping_address = None
                
                if use_new_address == 'on':
                    # Crear nueva dirección
                    address_form = CustomerAddressForm(request.POST, customer=customer)
                    if address_form.is_valid():
                        new_address = address_form.save()
                        shipping_address = new_address
                    else:
                        messages.error(request, 'Error en los datos de la nueva dirección.')
                        context = {
                            'items': items,
                            'order': order,
                            'cartItems': cartItems,
                            'customer': customer,
                            'customer_addresses': customer_addresses,
                            'address_form': address_form,
                        }
                        return render(request, 'store/checkout.html', context)
                elif selected_address_id:
                    # Usar dirección existente
                    shipping_address = customer.addresses.get(id=selected_address_id)
                
                if not shipping_address:
                    messages.error(request, 'Debes seleccionar una dirección de envío.')
                    context = {
                        'items': items,
                        'order': order,
                        'cartItems': cartItems,
                        'customer': customer,
                        'customer_addresses': customer_addresses,
                        'address_form': address_form,
                    }
                    return render(request, 'store/checkout.html', context)
                
                # Guardar método de pago
                payment_method = request.POST.get('payment_method', 'bank-transfer')
            
            # Actualizar orden actual - SIMULAR PAGO EFECTUADO
            order.complete = True
            order.status = "Procesando"  # PAGO CONFIRMADO - PREPARANDO ENVÍO
            
            # Generar ID de transacción si no existe
            if not order.transaction_id:
                import uuid
                order.transaction_id = str(uuid.uuid4())[:8].upper()
            
            order.save()
            
            # Crear shipping address para este pedido
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                customer_address=shipping_address,
                name=shipping_address.full_name,
                phone=shipping_address.phone,
                address=shipping_address.address,
                city=shipping_address.city,
                state=shipping_address.get_state_display(),
                zipcode=shipping_address.zipcode,
            )
            
            # Crear historial - PAGO SIMULADO SIEMPRE EXITOSO
            OrderHistory.objects.create(
                user=request.user, 
                customer=customer,
                order=order,
                status='processing',  # PAGO CONFIRMADO - No pendiente
                payment_method=payment_method
            )
            
            # NOTA: No crear nueva orden aquí - se creará automáticamente cuando
            # el usuario agregue el primer item al carrito en la próxima sesión
            
            # Return appropriate response based on request type
            if request.content_type == 'application/json':
                return JsonResponse({
                    'status': 'success',
                    'message': f'¡Pago realizado con éxito! Tu pedido #{order.id} será enviado a {shipping_address.nickname}.',
                    'order_id': order.id,
                    'payment_method': payment_method,
                    'shipping_address': shipping_address.nickname
                })
            else:
                messages.success(request, f'¡Pago realizado con éxito! Tu pedido #{order.id} será enviado a {shipping_address.nickname}.')
                return redirect('order_history')
            
        except Exception as e:
            if request.content_type == 'application/json':
                return JsonResponse({
                    'status': 'error',
                    'message': f'Ocurrió un error al procesar el pago: {e}'
                })
            else:
                messages.error(request, f'Ocurrió un error al procesar el pago: {e}')
                return redirect('checkout')
        
    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'customer': customer,
        'customer_addresses': customer_addresses,
        'address_form': address_form,
    }
    return render(request, 'store/checkout.html', context)

# Vista de pedidos comprados
def updateItem(request):
    try:
        data = json.loads(request.body)
        productId = data['productId']
        action = data['action']
        print('Action:', action)
        print('Product:', productId)
        
        try:
            customer = request.user.customer
        except Customer.DoesNotExist:
            return JsonResponse({'error': 'No customer associated with this user.'}, status=400)

        product = Product.objects.get(id=productId)
        
        # Buscar orden activa existente
        order = Order.objects.filter(customer=customer, complete=False).first()
        
        # Solo crear nueva orden si se está agregando un item y no hay orden activa
        if not order and action == 'add':
            order = Order.objects.create(customer=customer, complete=False, status='Pendiente')
        elif not order and action == 'remove':
            # No hay orden activa y se intenta remover, no hacer nada
            return JsonResponse({'message': 'No active order to remove from', 'quantity': 0}, status=200)
        
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

        if action == 'add':
            orderItem.quantity = (orderItem.quantity + 1)
        elif action == 'remove':
            orderItem.quantity = (orderItem.quantity - 1)

        orderItem.save()

        if orderItem.quantity <= 0:
            orderItem.delete()
            # Si no quedan items en la orden, eliminar la orden vacía
            if not order.orderitem_set.exists():
                order.delete()
                return JsonResponse({'message': 'Order deleted as it became empty', 'quantity': 0}, status=200)

        # Devuelve una respuesta JSON indicando que la actualización se realizó correctamente
        return JsonResponse({'message': 'Item was updated', 'quantity': orderItem.quantity}, status=200)
    except ObjectDoesNotExist as e:
        return JsonResponse({'error': str(e)}, status=400)
    except KeyError as e:
        return JsonResponse({'error': 'Missing key in request data: ' + str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'An error occurred: ' + str(e)}, status=500)

# Logica del manejo de pedidos del lado del usuario
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(user=request.user)

        # Verificamos si ya existe un pedido pendiente
        order = Order.objects.filter(customer=customer, complete=False).first()

        if order is None:  # Si no existe un pedido pendiente, no se crea nada
            return JsonResponse({'error': 'No hay pedido pendiente para este usuario.'}, status=400)

    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    payment_method = data['form'].get('payment_method', 'bank-transfer')
    order.transaction_id = transaction_id

    if total == order.get_cart_total_with_iva:
        order.complete = True
    order.save()

    # Restar la cantidad de productos comprados del stock
    for item in order.orderitem_set.all():
        product = item.product
        product.quantity -= item.quantity
        product.save()

    # Verificación de la dirección de envío
    print("Datos de envío recibidos:", data['shipping'])

    try:
        if order.shipping:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )
        else:
            print("No se requiere dirección de envío.")
    except Exception as e:
        print(f"Error al guardar la dirección de envío: {e}")

    # Crear historial de pedido para el cliente
    from .models import OrderHistory
    OrderHistory.objects.create(
        customer=customer,
        order=order,
        status='pending',
        payment_method=payment_method
    )

    return JsonResponse({
        'status': 'success',
        'message': 'Payment submitted successfully',
        'payment_method': payment_method,
        'order_id': order.id,
        'transaction_id': transaction_id
    }, safe=False)

# Vista para editar productos del lado del administrador
@login_required
def edit_product(request, product_id):
    data = cartData(request)
    cartItems = data['cartItems']
    
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    if request.method == 'POST':
        form = ProductEditForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user  # Asegura que el vendedor sea el usuario actual
            
            # Validación de oferta
            if product.offer and not product.offer_price:
                form.add_error('offer_price', 'Debe ingresar un precio de oferta si el producto está en oferta.')
                return render(request, 'store/editProduct.html', {'form': form, 'cartItems': cartItems})
            
            product.save()
            return redirect('productHistory')  # Redirige a la lista de productos
    else:
        form = ProductEditForm(instance=product)

    return render(request, 'store/editProduct.html', {'form': form, 'cartItems': cartItems})

# Vista para eliminar el producto
@login_required
def delete_product(request, product_id):
    # Verifica si el producto existe y pertenece al usuario actual (vendedor)
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    if request.method == 'POST':
        # Elimina el producto
        product.delete()
        messages.success(request, 'Producto eliminado con éxito.')
        return redirect('productHistory')  # Redirige a la lista de productos del vendedor

    return render(request, 'store/confirm_delete.html', {'product': product})


# Vista de detalles del pedido
# Vista de detalles del producto
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    data = cartData(request)
    cartItems = data['cartItems']
    comments = product.comments.order_by('-created_at')
    # Prepara una lista de miniaturas (URLs) hasta 4 imágenes
    thumbnails = [
        product.image.url if product.image else None,
        product.imageuno.url if product.imageuno else None,
        product.imagedos.url if product.imagedos else None,
        product.imagetres.url if product.imagetres else None,
    ]
    thumbnails = [t for t in thumbnails if t][:4]
    return render(request, 'store/product_detail.html', {
        'product': product,
        'thumbnails': thumbnails,
        'cartItems': cartItems,
        'comments': comments,
    })

# Vista de comentarios de producto
@login_required  # Si solo quieres que comenten usuarios logueados
def add_comment(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        text = request.POST.get('comment')
        if text:
            Comment.objects.create(
                product=product,
                user=request.user,
                text=text
            )
    return redirect('product_detail', pk=product.pk)

# Vista de likes para productos por usuarios clientes e incluso administradores
@require_POST
@login_required
def like_product(request, pk):
    product = Product.objects.get(pk=pk)
    user = request.user

    if user in product.likes.all():
        product.likes.remove(user)
        liked = False
    else:
        product.likes.add(user)
        liked = True

    return JsonResponse({
        'liked': liked,
        'likes_count': product.likes.count(),
    })

# Vista para los like de comentarios de usuarios acerca de los productos
@login_required
def like_comment(request, pk):
    if request.method == 'POST':
        comment = Comment.objects.get(pk=pk)
        user = request.user

        if user in comment.likes.all():
            comment.likes.remove(user)
            liked = False
        else:
            comment.likes.add(user)
            liked = True

        return JsonResponse({'liked': liked, 'likes_count': comment.likes.count()})

# Vista de lista de los pedidos que hacen los usuarios para que sean atendidos
@staff_member_required
def admin_order_list(request):
    orders = Order.objects.all().order_by('-date_ordered')
    return render(request, 'store/admin_order_list.html', {'orders': orders})

# Vista para editen el status y fecha de entrega de los productos
@staff_member_required
def update_order_status(request, order_id):
    data = cartData(request)
    cartItems = data['cartItems']
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        form = OrderUpdateForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'El pedido ha sido actualizado correctamente.')
            return redirect('admin_order_list')
    else:
        form = OrderUpdateForm(instance=order)

    return render(request, 'store/update_order.html', {'form': form, 'order': order, 'cartItems':cartItems})

@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            print(f"Chatbot recibió mensaje: {user_message}")  # Debug log
            
            if not user_message:
                return JsonResponse({'error': 'No se proporcionó mensaje'}, status=400)
            
            # Verificar si existe la clave de OpenAI
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                print("No se encontró OPENAI_API_KEY en el .env")
                bot_response = get_automated_response(user_message)
                print(f"✅ Respuesta automática generada: {bot_response[:100]}...")
                return JsonResponse({
                    'response': bot_response,
                    'success': True
    })
            
            print(f"Usando OpenAI API Key: {api_key[:10]}...")  # Debug log (solo primeros caracteres)
            
            # Configurar cliente OpenAI
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            # Crear el contexto del chatbot para ALM Refaccionaria
            system_prompt = """
            Eres un asistente virtual de ALM Refaccionaria, una tienda especializada en autopartes y refacciones automotrices.
            
            Tu función es ayudar a los clientes con:
            - Información sobre productos y refacciones automotrices
            - Consultas sobre pedidos, envíos y entregas
            - Recomendaciones de productos según el tipo de vehículo
            - Soporte general de la tienda
            - Preguntas sobre garantías, devoluciones y políticas
            - Información sobre métodos de pago disponibles
            
            Responde de manera amigable, profesional y útil. Usa un tono cercano pero profesional.
            Si no sabes algo específico sobre un producto, recomienda que contacten al equipo de ventas.
            Mantén las respuestas concisas pero informativas (máximo 3-4 líneas).
            """
            
            # Llamada a la API de OpenAI (nueva sintaxis)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            bot_response = response.choices[0].message.content.strip()
            print(f"OpenAI respondió: {bot_response}")  # Debug log
            
            return JsonResponse({
                'response': bot_response,
                'success': True
            })
            
        except Exception as e:
            print(f"Error con OpenAI: {str(e)}")
            # Usar sistema de respuestas automáticas como fallback
            bot_response = get_automated_response(user_message)
            return JsonResponse({
                'response': bot_response,
                'success': True
            })
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def get_automated_response(user_message):
    """Sistema de respuestas automáticas"""
    
    message_lower = user_message.lower().strip()
    
    # Saludos
    if any(word in message_lower for word in ['hola', 'buenos', 'buenas', 'hey', 'hi']):
        return "¡Hola! 👋 Bienvenido a ALM Refaccionaria..."
    
    # Productos
    elif any(word in message_lower for word in ['producto', 'productos', 'refaccion']):
        return "🔧 En ALM Refaccionaria manejamos..."
    
    # Envíos
    elif any(word in message_lower for word in ['envio', 'envío', 'entrega']):
        return "📦 Ofrecemos envío gratuito..."
    
    # Pagos
    elif any(word in message_lower for word in ['pago', 'pagar', 'precio']):
        return "💳 Aceptamos múltiples métodos..."
    
    # Garantías
    elif any(word in message_lower for word in ['garantia', 'garantía', 'devolucion']):
        return "🛡️ Todos nuestros productos..."
    
    # Pedidos
    elif any(word in message_lower for word in ['pedido', 'orden', 'compra']):
        return "📋 Puedes revisar el estado..."
    
    # Contacto
    elif any(word in message_lower for word in ['contacto', 'telefono', 'teléfono']):
        return "📞 Puedes contactarnos..."
    
    # ===== HORARIOS (VERSIÓN CORRECTA) =====
    elif any(word in message_lower for word in ['horario', 'hora', 'abierto', 'cerrado', 'atencion', 'atención', 'cierran', 'abren', 'atienden', 'trabajan', 'laboran']):
        return """🕒 Horario de Atención - ALM Refaccionaria

📅 Lunes a Viernes: 8:00 AM - 4:00 PM
📅 Sábado: 8:30 AM - 1:00 PM
📅 Domingo: Cerrado

⚠️ El horario puede variar en días festivos

📞 WhatsApp: +52 981 160 22 76
💬 Este asistente está disponible 24/7"""
    
    # Ubicación
    elif any(word in message_lower for word in ['ubicacion', 'ubicación', 'direccion']):
        return "📍 Puedes encontrar..."
    
    # ... resto de respuestas ...
    
    # Respuesta por defecto
    else:
        return "🤖 Recibí tu mensaje..."



# Vista para actualizar estado de pedidos desde el admin
@staff_member_required
@require_POST
@csrf_exempt
def admin_update_order_status(request):
    """Actualiza el estado de un pedido desde el panel de administración"""
    try:
        data = json.loads(request.body)
        order_history_id = data.get('order_history_id')
        new_status = data.get('status')
        
        # Validar que el estado es válido (códigos del modelo OrderHistory)
        valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        if new_status not in valid_statuses:
            return JsonResponse({'success': False, 'error': 'Estado no válido'})
        
        # Buscar el OrderHistory
        order_history = get_object_or_404(OrderHistory, id=order_history_id)
        
        # Actualizar el estado
        order_history.status = new_status
        order_history.save()
        
        # También actualizar el estado de la orden (usando los estados del modelo Order)
        status_mapping = {
            'pending': 'Pendiente',
            'processing': 'Procesando', 
            'shipped': 'Enviado',
            'delivered': 'Entregado',
            'cancelled': 'Cancelado'
        }
        
        order_history.order.status = status_mapping[new_status]
        if new_status == 'delivered':
            order_history.order.complete = True
        elif new_status == 'cancelled':
            order_history.order.complete = False
        order_history.order.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'Estado actualizado a {new_status}',
            'new_status': new_status
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# Vista para dashboard del admin
@staff_member_required
def admin_dashboard(request):
    """Dashboard personalizado para administradores"""
    # Estadísticas generales
    total_orders = Order.objects.count()  # Todos los pedidos
    completed_orders = Order.objects.filter(complete=True).count()
    pending_orders = Order.objects.filter(complete=False).count()
    total_customers = Customer.objects.count()
    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(quantity__lte=5).count()
    
    # Pedidos recientes (últimos 10)
    recent_orders = Order.objects.select_related('customer').order_by('-date_ordered')[:10]
    
    # Productos con stock bajo
    low_stock = Product.objects.filter(quantity__lte=5).order_by('quantity')[:10]
    
    # Ventas del mes actual
    current_month = timezone.now().replace(day=1)
    monthly_orders = Order.objects.filter(
        complete=True,
        date_ordered__gte=current_month
    )
    
    monthly_revenue = sum(order.get_cart_total_with_iva for order in monthly_orders)
    
    context = {
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
        'total_customers': total_customers,
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'recent_orders': recent_orders,
        'low_stock': low_stock,
        'monthly_revenue': monthly_revenue,
        'monthly_orders_count': monthly_orders.count(),
    }
    
    return render(request, 'admin/dashboard.html', context)


# Vista personalizada para el índice del admin
@staff_member_required
def custom_admin_index(request):
    """Índice personalizado del admin con estadísticas reales"""
    # Obtener estadísticas reales
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(complete=False).count()
    total_customers = Customer.objects.count()
    total_products = Product.objects.count()
    
    context = {
        'title': 'Panel de Control',
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_customers': total_customers,
        'total_products': total_products,
        'has_permission': True,
        'is_nav_sidebar_enabled': True,
        'available_apps': admin.site.get_app_list(request),
    }
    
    return render(request, 'admin/index.html', context)


# Vistas para gestión de direcciones del cliente
@login_required
def customer_addresses(request):
    """Vista para mostrar todas las direcciones del cliente"""
    data = cartData(request)
    customer = request.user.customer
    addresses = customer.addresses.all()
    
    context = {
        'cartItems': data['cartItems'],
        'addresses': addresses,
        'customer': customer,
    }
    return render(request, 'store/customer_addresses.html', context)

@login_required
def add_address(request):
    """Vista para agregar una nueva dirección"""
    data = cartData(request)
    customer = request.user.customer
    
    if request.method == 'POST':
        form = CustomerAddressForm(request.POST, customer=customer)
        if form.is_valid():
            address = form.save()
            messages.success(request, f'Dirección "{address.nickname}" agregada correctamente.')
            return redirect('customer_addresses')
    else:
        form = CustomerAddressForm(customer=customer)
    
    context = {
        'cartItems': data['cartItems'],
        'form': form,
        'title': 'Agregar Dirección',
    }
    return render(request, 'store/address_form.html', context)

@login_required
def edit_address(request, address_id):
    """Vista para editar una dirección existente"""
    data = cartData(request)
    customer = request.user.customer
    address = get_object_or_404(CustomerAddress, id=address_id, customer=customer)
    
    if request.method == 'POST':
        form = CustomerAddressForm(request.POST, instance=address, customer=customer)
        if form.is_valid():
            address = form.save()
            messages.success(request, f'Dirección "{address.nickname}" actualizada correctamente.')
            return redirect('customer_addresses')
    else:
        form = CustomerAddressForm(instance=address, customer=customer)
    
    context = {
        'cartItems': data['cartItems'],
        'form': form,
        'address': address,
        'title': 'Editar Dirección',
    }
    return render(request, 'store/address_form.html', context)

@login_required
def delete_address(request, address_id):
    """Vista para eliminar una dirección"""
    customer = request.user.customer
    address = get_object_or_404(CustomerAddress, id=address_id, customer=customer)
    
    # No permitir eliminar si es la única dirección
    if customer.addresses.count() <= 1:
        messages.error(request, 'No puedes eliminar tu única dirección registrada.')
        return redirect('customer_addresses')
    
    if request.method == 'POST':
        nickname = address.nickname
        address.delete()
        messages.success(request, f'Dirección "{nickname}" eliminada correctamente.')
        return redirect('customer_addresses')
    
    data = cartData(request)
    context = {
        'cartItems': data['cartItems'],
        'address': address,
    }
    return render(request, 'store/confirm_delete_address.html', context)

@login_required
def set_default_address(request, address_id):
    """Vista para establecer una dirección como principal"""
    customer = request.user.customer
    address = get_object_or_404(CustomerAddress, id=address_id, customer=customer)
    
    # Quitar el default de todas las direcciones del cliente
    customer.addresses.update(is_default=False)
    # Establecer esta como default
    address.is_default = True
    address.save()
    
    messages.success(request, f'"{address.nickname}" establecida como dirección principal.')
    return redirect('customer_addresses')

# ===== VISTAS PARA DETALLES DE PEDIDO Y REEMBOLSOS =====

@login_required
def order_detail(request, order_id):
    """Vista detallada de un pedido específico"""
    try:
        customer = request.user.customer
        order = get_object_or_404(Order, id=order_id, customer=customer)
        order_history = OrderHistory.objects.filter(order=order).first()
        shipping_address = ShippingAddress.objects.filter(order=order).first()
        refund = getattr(order, 'refund', None)  # Verificar si existe reembolso
        
        # Determinar si se puede cancelar/reembolsar
        can_request_refund = order.complete and not refund
        can_cancel = order.status in ['Pendiente', 'Procesando'] and not refund
        requires_return = order.status in ['Enviado', 'Entregado']
        
        data = cartData(request)
        context = {
            'cartItems': data['cartItems'],
            'order': order,
            'order_history': order_history,
            'shipping_address': shipping_address,
            'refund': refund,
            'can_request_refund': can_request_refund,
            'can_cancel': can_cancel,
            'requires_return': requires_return,
        }
        return render(request, 'store/order_detail.html', context)
        
    except Customer.DoesNotExist:
        messages.error(request, 'No tienes permisos para ver este pedido.')
        return redirect('order_history')

@login_required
def request_refund(request, order_id):
    """Vista para solicitar reembolso/cancelación"""
    try:
        customer = request.user.customer
        order = get_object_or_404(Order, id=order_id, customer=customer)
        
        # Verificar que no tenga ya un reembolso
        if hasattr(order, 'refund'):
            messages.error(request, 'Este pedido ya tiene una solicitud de reembolso.')
            return redirect('order_detail', order_id=order_id)
        
        if request.method == 'POST':
            reason = request.POST.get('reason')
            customer_notes = request.POST.get('customer_notes', '')
            
            # Determinar tipo de reembolso basado en el estado del pedido
            if order.status in ['Pendiente', 'Procesando']:
                refund_type = 'cancellation'
            else:
                refund_type = 'return_refund'
            
            # Calcular montos antes de crear el reembolso
            base_amount = Decimal(str(order.get_cart_total_with_iva))
            
            if refund_type == 'cancellation':
                # Cancelación simple - reembolso completo
                refund_fee = Decimal('0.00')
                final_refund_amount = base_amount
            else:
                # Devolución con retorno - comisión del 5%
                fee_percentage = Decimal('0.05')
                refund_fee = base_amount * fee_percentage
                final_refund_amount = base_amount - refund_fee
            
            # Crear solicitud de reembolso
            refund = Refund.objects.create(
                order=order,
                customer=customer,
                refund_type=refund_type,
                reason=reason,
                customer_notes=customer_notes,
                status='pending',
                refund_amount=base_amount,
                refund_fee=refund_fee,
                final_refund_amount=final_refund_amount
            )
            
            # Establecer fecha límite para devolución si es necesario
            if refund_type == 'return_refund':
                from django.utils import timezone
                from datetime import timedelta
                refund.return_deadline = timezone.now() + timedelta(days=15)
                refund.save()
            
            # Cambiar estado de la orden
            order.status = 'Cancelado' if refund_type == 'cancellation' else order.status
            order.save()
            
            # Actualizar OrderHistory
            order_history = OrderHistory.objects.filter(order=order).first()
            if order_history:
                order_history.status = 'cancelled' if refund_type == 'cancellation' else order_history.status
                order_history.save()
            
            # Crear notificación
            Notification.objects.create(
                user=request.user,
                message=f'Solicitud de reembolso creada para el pedido #{order.id}'
            )
            
            messages.success(request, 'Solicitud de reembolso enviada correctamente. Te contactaremos pronto.')
            return redirect('order_detail', order_id=order_id)
        
        # GET request - mostrar formulario
        data = cartData(request)
        context = {
            'cartItems': data['cartItems'],
            'order': order,
            'can_cancel': order.status in ['Pendiente', 'Procesando'],
            'requires_return': order.status in ['Enviado', 'Entregado'],
        }
        return render(request, 'store/request_refund.html', context)
        
    except Customer.DoesNotExist:
        messages.error(request, 'No tienes permisos para hacer esta solicitud.')
        return redirect('order_history')

@staff_member_required  
def admin_refunds_list(request):
    """Vista administrativa para gestionar reembolsos"""
    refunds = Refund.objects.all().select_related('order', 'order__customer').order_by('-created_at')
    
    # Calcular estadísticas
    stats = {
        'pending': refunds.filter(status='pending').count(),
        'approved': refunds.filter(status='approved').count(),
        'processing': refunds.filter(status__in=['processing', 'waiting_return', 'product_received', 'quality_check']).count(),
        'waiting_return': refunds.filter(status='waiting_return').count(),
    }
    
    # Filtros
    status_filter = request.GET.get('status')
    refund_type_filter = request.GET.get('refund_type')
    sort_by = request.GET.get('sort', '-created_at')
    
    if status_filter:
        refunds = refunds.filter(status=status_filter)
    
    if refund_type_filter:
        refunds = refunds.filter(refund_type=refund_type_filter)
    
    if sort_by:
        refunds = refunds.order_by(sort_by)
    
    # Paginación
    from django.core.paginator import Paginator
    paginator = Paginator(refunds, 20)
    page_number = request.GET.get('page')
    refunds = paginator.get_page(page_number)
    
    context = {
        'refunds': refunds,
        'stats': stats,
        'status_choices': Refund.REFUND_STATUS_CHOICES,
    }
    return render(request, 'store/admin_refunds.html', context)

@staff_member_required
def process_refund(request, refund_id):
    """Vista para procesar un reembolso desde el admin"""
    refund = get_object_or_404(Refund, id=refund_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        admin_notes = request.POST.get('admin_notes', '')
        
        if action == 'approve':
            refund.status = 'approved'
            refund.admin_notes = admin_notes
            refund.processed_by = request.user
            refund.processed_at = timezone.now()
            
            # Si es cancelación simple, marcar como completado inmediatamente
            if refund.refund_type == 'cancellation':
                refund.status = 'completed'
                refund.completed_at = timezone.now()
        
        elif action == 'reject':
            refund.status = 'rejected'
            refund.admin_notes = admin_notes
            refund.processed_by = request.user
            refund.processed_at = timezone.now()
            
            # Restaurar estado de la orden si fue cancelada
            if refund.order.status == 'Cancelado':
                refund.order.status = 'Procesando'
                refund.order.save()
        
        elif action == 'mark_received':
            if refund.refund_type == 'return_refund':
                refund.status = 'product_received'
                refund.product_returned_at = timezone.now()
        
        elif action == 'quality_ok':
            refund.quality_approved = True
            refund.status = 'completed'
            refund.completed_at = timezone.now()
            
        elif action == 'quality_fail':
            refund.quality_approved = False
            refund.status = 'rejected'
            refund.admin_notes += f" | Producto no aprobó control de calidad: {admin_notes}"
        
        refund.save()
        
        # Crear notificación para el cliente
        Notification.objects.create(
            user=refund.customer.user,
            message=f'Actualización en tu solicitud de reembolso para el pedido #{refund.order.id}'
        )
        
        messages.success(request, f'Reembolso #{refund.id} actualizado correctamente.')
        return redirect('admin_refunds_list')
    
    context = {
        'refund': refund,
    }
    return render(request, 'store/process_refund.html', context)


def contacto(request):
    """Vista de contacto con sucursales dinámicas"""
    if request.method == 'POST':
        # Tu código existente para procesar el formulario
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        mensaje = request.POST.get('mensaje')
        
        # Aquí podrías enviar un email o guardar en base de datos
        messages.success(request, '¡Mensaje enviado exitosamente! Nos pondremos en contacto pronto.')
        return redirect('contacto')
    
    # Obtener todas las sucursales activas
    branches = Branch.objects.filter(is_active=True).order_by('-is_main', 'name')
    
    context = {
        'branches': branches,
        'cartItems': 0  # Ajusta según tu lógica de carrito
    }
    
    return render(request, 'store/contacto.html', context)


def get_product_availability(request, product_id):
    """API endpoint para obtener disponibilidad de un producto por sucursal"""
    try:
        product = Product.objects.get(id=product_id)
        
        # Obtener inventario por sucursal
        availability = ProductBranch.objects.filter(
            product=product,
            branch__is_active=True
        ).select_related('branch').values(
            'branch__name',
            'branch__code',
            'branch__city',
            'branch__phone',
            'stock_quantity',
            'location_code'
        )
        
        data = {
            'product': product.name,
            'total_stock': sum(item['stock_quantity'] for item in availability),
            'availability': list(availability)
        }
        
        return JsonResponse(data)
    
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)


def branch_list(request):
    """Vista para listar todas las sucursales (API o página)"""
    branches = Branch.objects.filter(is_active=True).annotate(
        total_products=Count('product_branches'),
        total_stock=Sum('product_branches__stock_quantity')
    ).order_by('-is_main', 'name')
    
    # Si es una petición AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = [{
            'id': branch.id,
            'name': branch.name,
            'code': branch.code,
            'address': branch.full_address,
            'phone': branch.phone,
            'whatsapp': branch.whatsapp,
            'email': branch.email,
            'schedule': branch.schedule,
            'is_main': branch.is_main,
            'total_products': branch.total_products,
            'total_stock': branch.total_stock,
            'latitude': float(branch.latitude) if branch.latitude else None,
            'longitude': float(branch.longitude) if branch.longitude else None,
        } for branch in branches]
        
        return JsonResponse({'branches': data})
    
    # Si no, renderizar template
    context = {
        'branches': branches,
        'cartItems': 0
    }
    return render(request, 'store/branches.html', context)


def branch_detail(request, branch_id):
    """Vista detallada de una sucursal con su inventario"""
    branch = get_object_or_404(Branch, id=branch_id, is_active=True)
    
    # Obtener productos disponibles en esta sucursal
    products_in_branch = ProductBranch.objects.filter(
        branch=branch,
        stock_quantity__gt=0
    ).select_related('product').order_by('-stock_quantity')
    
    context = {
        'branch': branch,
        'products': products_in_branch,
        'cartItems': 0
    }
    
    return render(request, 'store/branch_detail.html', context)