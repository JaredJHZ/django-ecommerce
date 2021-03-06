from django.db import models
from django.conf import settings
from django.shortcuts import reverse


CATEGORY_CHOICES = (
    ('P', 'Bikini primaveral'),
    ('I', 'Bikini invernal')
)

LABEL_CHOICES = (
    ('N', 'Nuevo'),
    ('O', 'En oferta')
)

ADRESS_CHOICES = (
    ('F', 'Factura'),
    ('E', 'Envio')
)


class Category(models.Model):
    name = models.CharField(max_length = 100, verbose_name = "Nombre")

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categorias"

class Item(models.Model):
    title = models.CharField(max_length = 100, verbose_name = "Nombre del articulo")
    price = models.FloatField(verbose_name = "Precio")
    discount_price = models.FloatField(blank=True, null=True, verbose_name = "Precio de descuento")
    category = models.ForeignKey(Category, on_delete= models.CASCADE, blank = True, null = True)
    label = models.CharField(choices=LABEL_CHOICES, max_length = 2, verbose_name = "Nuevo o en oferta?")
    slug = models.SlugField(verbose_name = "Link")
    description = models.TextField(verbose_name = "Descripcion")
    image = models.ImageField()
    image2 = models.ImageField(blank = True, null = True)
    image3 = models.ImageField(blank = True, null = True)
    stock = models.IntegerField(default = 1, verbose_name = "Stock")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
    

    def get_absolute_url(self):
        return reverse("core:product_page", kwargs={
            'slug':self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug':self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug':self.slug
        })

    def get_title_upper(self):
        return self.title[0].upper() + self.title[1:]

    def __str__(self):
        return self.title



class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete= models.CASCADE , verbose_name = "Producto")
    quantity = models.IntegerField(default= 1 , verbose_name = "Cantidad")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE, blank = True, null = True, verbose_name = "Usuario")
    ordered = models.BooleanField(default=False, verbose_name="¿Ordenado?")
    class Meta:
        verbose_name = "Producto de orden"
        verbose_name_plural = "Productos de orden"

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"
    
    def get_total_item_price(self):
        return self.quantity * self.item.price
    
    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE, verbose_name = "Usuario")
    sent = models.BooleanField(default=False, verbose_name = "¿Ha sido enviado?")
    ref_code = models.CharField(max_length=30 , verbose_name = "Número de rastreo")
    ordered = models.BooleanField(default=False , verbose_name = "¿Ordenado?")
    items = models.ManyToManyField(OrderItem , verbose_name = "Productos")
    start_date = models.DateTimeField(auto_now= True)
    ordered_date = models.DateTimeField(verbose_name = "Fecha de orden")
    shipping_address = models.ForeignKey('Address', related_name="shipping_address" ,on_delete=models.CASCADE, blank = True, null = True, verbose_name = "Dirección")
    payment = models.ForeignKey('Payment', on_delete=models.CASCADE, blank = True, null = True, verbose_name = "Pago")
    sent_price = models.IntegerField(blank = True, null = True, verbose_name = "Precio de envío")

    class Meta:
        verbose_name = "Orden"
        verbose_name_plural = "Ordenes"

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        
        return total

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name = "Cliente")
    street_address = models.CharField(max_length = 100, verbose_name = "Calle")
    suburb = models.CharField(max_length = 100 , verbose_name ="Colonia")
    phone_number = models.CharField(max_length = 10, verbose_name = "Telefono")
    state = models.CharField( max_length = 30, verbose_name = "estado")
    zip = models.CharField(max_length = 6, verbose_name = "Codigo Postal")
    default = models.BooleanField(default = False)
    point = models.CharField(max_length = 200, verbose_name = "Punto medio")

    class Meta:
        verbose_name = "Dirección"
        verbose_name_plural = "Direcciones"

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = "Direcciones"

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length = 50, verbose_name ="ID de pago")
    user = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete = models.SET_NULL, blank = True, null = True, verbose_name = "Usuario")
    amount = models.FloatField(verbose_name="Cantidad (MXN)")
    timestamp = models.DateTimeField(auto_now_add = True, verbose_name = "Fecha")
    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
    def __str__(self):
        return self.user.username

# class Coupon(models.Model):
#     code = models.CharField(max_length = 15)
#     amount = models.FloatField()

#     def __str__(self):
#         return self.code

class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete = models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.pk}"