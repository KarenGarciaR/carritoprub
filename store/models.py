from django.db import models
from django.contrib.auth.models import User

MEXICAN_STATES = [
    ('AGU', 'Aguascalientes'),
    ('BCN', 'Baja California'),
    ('BCS', 'Baja California Sur'),
    ('CAM', 'Campeche'),
    ('CHP', 'Chiapas'),
    ('CHH', 'Chihuahua'),
    ('COA', 'Coahuila'),
    ('COL', 'Colima'),
    ('DIF', 'Ciudad de México'),
    ('DUR', 'Durango'),
    ('GUA', 'Guanajuato'),
    ('GRO', 'Guerrero'),
    ('HGO', 'Hidalgo'),
    ('JAL', 'Jalisco'),
    ('MEX', 'Estado de México'),
    ('MIC', 'Michoacán'),
    ('MOR', 'Morelos'),
    ('NAY', 'Nayarit'),
    ('NLE', 'Nuevo León'),
    ('OAX', 'Oaxaca'),
    ('PUE', 'Puebla'),
    ('QRO', 'Querétaro'),
    ('QRO', 'Quintana Roo'),
    ('SLP', 'San Luis Potosí'),
    ('SIN', 'Sinaloa'),
    ('SON', 'Sonora'),
    ('TAB', 'Tabasco'),
    ('TAM', 'Tamaulipas'),
    ('TLX', 'Tlaxcala'),
    ('VER', 'Veracruz'),
    ('YUC', 'Yucatán'),
    ('ZAC', 'Zacatecas'),
]

class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(max_length=200)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    referencias = models.CharField(max_length=250, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    zip_code = models.CharField(max_length=10, null=True, blank=True)
    state = models.CharField(
        max_length=3,
        choices=MEXICAN_STATES,
        blank=True,
        null=True
    )
    municipality = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name if self.name else self.email

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Sujeción y Soporte', 'Sujeción y Soporte'),
        ('Motor y Transmisión', 'Motor y Transmisión'),
        ('Sistema hidraulico y Neumatico', 'Sistema hidraulico y Neumatico'),
        ('Bujes y Casquillos', 'Bujes y Casquillos'),
        ('Sistema de Frenos', 'Sistema de Frenos'),
        ('Accesorios y Misceláneos', 'Accesorios y Misceláneos'),
    ]
    MATERIAL_CHOICES = [
        ('Acero', 'Acero'),
        ('Hierro fundido', 'Hierro fundido'),
        ('Bronce / Latón', 'Bronce / Latón'),
        ('Aluminio', 'Aluminio'),
        ('Goma / Poliuretano', 'Goma / Poliuretano'),
        ('Otro', 'Otro'),
    ]
    


    PROVEEDOR_CHOICES = [
        ('Productos Almeyda', 'Productos Almeyda'),
    ]

    proveedor = models.CharField(max_length=100, choices=PROVEEDOR_CHOICES)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=1000, null=True, blank=True)
    price = models.FloatField()
    offer_price = models.FloatField(null=True, blank=True)
    offer = models.BooleanField(default=False)
    quantity = models.IntegerField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    height_cm = models.FloatField()
    width_cm = models.FloatField()
    material = models.CharField(max_length=50, choices=MATERIAL_CHOICES)
    likes = models.ManyToManyField(User, related_name='liked_products', blank=True)
    date_of_delivery = models.DateField(null=True, blank=True)

    image = models.ImageField(null=True, blank=False)
    imageuno = models.ImageField(null=True, blank=False)
    imagedos = models.ImageField(null=True, blank=False)
    imagetres = models.ImageField(null=True, blank=False)

    def __str__(self):
        return self.name
    
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    
    @property
    def imageunoURL(self):
        try:
            url = self.imageuno.url
        except:
            url = ''
        return url
    
    @property
    def imagedosURL(self):
        try:
            url = self.imagedos.url
        except:
            url = ''
        return url
    
    @property
    def imagetresURL(self):
        try:
            url = self.imagetres.url
        except:
            url = ''
        return url

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Procesando', 'Procesando'),
        ('Enviado', 'Enviado'),
        ('Entregado', 'Entregado'),
        ('Cancelado', 'Cancelado'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=200, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pendiente')
    estimated_delivery = models.DateField(null=True, blank=True)
    custom_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'Orden #{self.id} - {self.customer}'

    @property
    def get_cart_items(self):
        return sum(item.quantity for item in self.orderitem_set.all())

    @property
    def get_cart_total(self):
        return sum(item.get_total for item in self.orderitem_set.all())
    
    @property
    def get_cart_iva(self):
        return self.get_cart_total * 0.16
    
    @property
    def get_cart_total_with_iva(self):
        return self.get_cart_total * 1.16

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        if not self.product:  # Si no hay producto
            return 0
        
        if self.product.offer and self.product.offer_price is not None:
            return self.product.offer_price * self.quantity
        
        return self.product.price * self.quantity


class OrderHistory(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('shipped', 'Enviado'),
        ('delivered', 'Entregado'),
        ('cancelled', 'Cancelado'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('bank-transfer', 'Transferencia Bancaria'),
        ('bank-deposit', 'Depósito en Banco'),
        ('online-payment', 'Pago en Línea con Tarjetas'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='bank-transfer')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido #{self.order.id} - {self.get_status_display()}"
    
    class Meta:
        ordering = ['-created_at']

class CustomerAddress(models.Model):
    """Modelo para guardar múltiples direcciones de envío por cliente"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='addresses')
    nickname = models.CharField(max_length=50, help_text="Ej: Casa, Trabajo, Casa de mamá") 
    full_name = models.CharField(max_length=200, verbose_name="Nombre completo del destinatario")
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=300, verbose_name="Calle y número")
    neighborhood = models.CharField(max_length=100, verbose_name="Colonia", blank=True, null=True)
    city = models.CharField(max_length=100, verbose_name="Ciudad/Municipio")
    state = models.CharField(max_length=3, choices=MEXICAN_STATES, verbose_name="Estado")
    zipcode = models.CharField(max_length=10, verbose_name="Código postal")
    references = models.TextField(blank=True, null=True, verbose_name="Referencias adicionales")
    is_default = models.BooleanField(default=False, verbose_name="Dirección principal")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', '-updated_at']
        verbose_name = "Dirección del Cliente"
        verbose_name_plural = "Direcciones de Clientes"

    def __str__(self):
        return f"{self.nickname} - {self.full_name}"

    def save(self, *args, **kwargs):
        # Si esta dirección se marca como principal, quitar el principal de las otras
        if self.is_default:
            CustomerAddress.objects.filter(
                customer=self.customer, 
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    @property
    def full_address(self):
        """Devuelve la dirección completa formateada"""
        parts = [self.address]
        if self.neighborhood:
            parts.append(self.neighborhood)
        parts.extend([self.city, self.get_state_display(), f"CP {self.zipcode}"])
        return ", ".join(parts)

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    customer_address = models.ForeignKey(CustomerAddress, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    zipcode = models.CharField(max_length=20)
    name = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address

class Personalizacion(models.Model):
    STATUS_CHOICES = [
        ('PENDIENTE',    'Pendiente'),
        ('EN_PROGRESO',  'En progreso'),
        ('RESPONDIDA',   'Respondida'),
    ]

    cliente          = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    descripcion      = models.TextField()
    fecha_creacion   = models.DateTimeField(auto_now_add=True)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDIENTE')
    respuesta_admin  = models.TextField(null=True, blank=True)
    atendido_por     = models.ForeignKey(User, on_delete=models.SET_NULL,
                                        null=True, blank=True,
                                        related_name='personalizaciones_atendidas')

    def __str__(self):
        who = self.cliente.user.username if self.cliente and self.cliente.user else "Invitado"
        return f"#{self.pk} - {who}"

class Comment(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.message}"

class Refund(models.Model):
    """Modelo para manejar reembolsos y cancelaciones"""
    REFUND_STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('processing', 'Procesando'),
        ('completed', 'Completado'),
        ('rejected', 'Rechazado'),
        ('waiting_return', 'Esperando Devolución'),
        ('product_received', 'Producto Recibido'),
        ('quality_check', 'Verificando Calidad'),
    ]
    
    REFUND_TYPE_CHOICES = [
        ('cancellation', 'Cancelación Simple'),
        ('return_refund', 'Devolución con Retorno'),
    ]
    
    REFUND_REASON_CHOICES = [
        ('changed_mind', 'Cambié de opinión'),
        ('wrong_product', 'Producto incorrecto'),
        ('defective', 'Producto defectuoso'),
        ('not_as_described', 'No como se describía'),
        ('damaged_shipping', 'Dañado en envío'),
        ('other', 'Otro motivo'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='refund')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    refund_type = models.CharField(max_length=20, choices=REFUND_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=REFUND_STATUS_CHOICES, default='pending')
    reason = models.CharField(max_length=20, choices=REFUND_REASON_CHOICES)
    customer_notes = models.TextField(blank=True, null=True, verbose_name="Comentarios del cliente")
    admin_notes = models.TextField(blank=True, null=True, verbose_name="Notas del administrador")
    
    # Montos
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto a reembolsar")
    refund_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Com isión por reembolso")
    final_refund_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto final de reembolso")
    
    # Fechas importantes
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Para devoluciones con retorno
    return_deadline = models.DateTimeField(null=True, blank=True, verbose_name="Fecha límite para devolver")
    product_returned_at = models.DateTimeField(null=True, blank=True)
    quality_approved = models.BooleanField(null=True, blank=True)
    
    # Gestión
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_refunds')
    
    def __str__(self):
        return f"Reembolso #{self.id} - Orden #{self.order.id} - {self.get_status_display()}"
    
    @property
    def can_cancel(self):
        """Determina si la orden puede ser cancelada sin devolución física"""
        return self.order.status in ['Pendiente', 'Procesando']
    
    @property
    def requires_return(self):
        """Determina si requiere devolución física del producto"""
        return self.order.status in ['Enviado', 'Entregado']
    
    def calculate_refund_amount(self):
        """Calcula el monto de reembolso basado en el tipo y comisiones"""
        base_amount = self.order.get_cart_total_with_iva
        
        if self.refund_type == 'cancellation':
            # Cancelación simple - reembolso completo
            self.refund_fee = 0
            self.final_refund_amount = base_amount
        else:
            # Devolución con retorno - puede tener comisión
            fee_percentage = 0.05  # 5% comisión por devolución
            self.refund_fee = base_amount * fee_percentage
            self.final_refund_amount = base_amount - self.refund_fee
        
        self.refund_amount = base_amount
        self.save()
    
    class Meta:
        ordering = ['-requested_at']
        verbose_name = "Reembolso"
        verbose_name_plural = "Reembolsos"

class CarouselSlide(models.Model):
    """Modelo para slides del carrusel de la página principal"""
    
    title = models.CharField(max_length=200, verbose_name="Título")
    subtitle = models.CharField(max_length=300, blank=True, null=True, verbose_name="Subtítulo")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    image = models.ImageField(upload_to='carousel/', verbose_name="Imagen")
    
    # Enlaces y botones
    button_text = models.CharField(max_length=50, blank=True, null=True, verbose_name="Texto del botón")
    button_link = models.URLField(blank=True, null=True, verbose_name="Enlace del botón")
    external_link = models.BooleanField(default=False, verbose_name="¿Enlace externo?")
    
    # Control de visibilidad y orden
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden de aparición")
    
    # Estilos y configuración
    SLIDE_TYPES = [
        ('promotion', '🏷️ Promoción/Oferta'),
        ('business', '🏢 Negocio/Instalaciones'),
        ('product', '🔧 Producto Destacado'),
        ('service', '⚙️ Servicio'),
        ('announcement', '📢 Anuncio General'),
    ]
    slide_type = models.CharField(max_length=20, choices=SLIDE_TYPES, default='promotion', verbose_name="Tipo de slide")
    
    # Configuración de colores
    background_color = models.CharField(max_length=7, default='#ffffff', verbose_name="Color de fondo", 
                                      help_text="Formato hex: #ffffff")
    text_color = models.CharField(max_length=7, default='#000000', verbose_name="Color del texto",
                                help_text="Formato hex: #000000")
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Programación opcional
    start_date = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de inicio", 
                                    help_text="Dejar vacío para mostrar inmediatamente")
    end_date = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de fin",
                                  help_text="Dejar vacío para mostrar indefinidamente")
    
    def __str__(self):
        return f"{self.title} - {self.get_slide_type_display()}"
    
    @property
    def is_visible(self):
        """Determina si el slide debe mostrarse basado en fechas y estado activo"""
        if not self.is_active:
            return False
        
        from django.utils import timezone
        now = timezone.now()
        
        if self.start_date and now < self.start_date:
            return False
        
        if self.end_date and now > self.end_date:
            return False
        
        return True
    
    @property
    def image_url(self):
        """URL segura de la imagen"""
        if self.image:
            return self.image.url
        return '/static/images/carousel_placeholder.jpg'
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Slide del Carrusel"
        verbose_name_plural = "Slides del Carrusel"