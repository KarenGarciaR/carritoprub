from django.dispatch import receiver
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseForbidden, JsonResponse
import json
import datetime
from django.utils import timezone
from .models import * 
from .utils import cookieCart, cartData, guestOrder
from .forms import ProductEditForm, SignupForm, LoginForm
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ProductForm, CustomerForm, OrderUpdateForm
from django.db.models.signals import post_save
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
import urllib.request
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST


# Create your views here.
# Home page
def index(request):
    """Página principal con productos destacados"""
    data = cartData(request)
    cartItems = data['cartItems']
    
    # Obtener productos destacados (puedes filtrar por ofertas, más vendidos, etc.)
    products_destacados = Product.objects.filter(
        quantity__gt=0  # Solo productos con stock
    ).order_by('-id')[:8]  # Los 8 productos más recientes
    
    context = {
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

    if request.method == 'POST':
        try:
            # Debug: Verificar qué datos llegan
            print(f"DEBUG - Procesando pago para orden {order.id}")
            print(f"DEBUG - Estado actual: {order.status}")
            print(f"DEBUG - Complete actual: {order.complete}")
            
            # Guardar método de pago
            payment_method = request.POST.get('payment_method')
            if payment_method:
                order.payment_method = payment_method
                print(f"DEBUG - Método de pago: {payment_method}")
            
            # Actualizar orden actual - SIMULAR PAGO EFECTUADO
            order.complete = True
            order.status = "Procesando"  # PAGO CONFIRMADO - PREPARANDO ENVÍO
            order.save()
            
            print(f"DEBUG - Nuevo estado: {order.status}")
            print(f"DEBUG - Nuevo complete: {order.complete}")
            
            # Crear historial
            OrderHistory.objects.create(user=request.user, order=order)
            
            # IMPORTANTE: Crear una nueva orden vacía para el siguiente carrito
            # Esto asegura que cada compra sea independiente
            new_order = Order.objects.create(
                customer=customer,
                complete=False,
                status="Pendiente"
            )
            
            messages.success(request, f'¡Pago realizado con éxito! Tu pedido #{order.id} está siendo preparado para envío.')
            return redirect('order_history')
            
        except Exception as e:
            messages.error(request, f'Ocurrió un error al procesar el pago: {e}')
            return redirect('checkout')
        
    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'customer': customer,
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
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

        if action == 'add':
            orderItem.quantity = (orderItem.quantity + 1)
        elif action == 'remove':
            orderItem.quantity = (orderItem.quantity - 1)

        orderItem.save()

        if orderItem.quantity <= 0:
            orderItem.delete()

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
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    data = cartData(request)
    cartItems = data['cartItems']

    # Permitir solo al administrador o al dueño del pedido ver los detalles
    if not request.user.is_staff and order.customer.user != request.user:
        return HttpResponseForbidden("No tienes permiso para ver este pedido.")

    return render(request, 'store/order_detail.html', {'order': order, 'cartItems': cartItems})

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