from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django_countries.fields import CountryField

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

class Item(models.Model):
    title = models.CharField(max_length = 100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length = 2)
    label = models.CharField(choices=LABEL_CHOICES, max_length = 2)
    slug = models.SlugField()
    discount_price = models.FloatField(blank=True, null=True)
    description = models.TextField()
    image = models.ImageField(blank = True, null = True)
    

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
    item = models.ForeignKey(Item, on_delete= models.CASCADE)
    quantity = models.IntegerField(default= 1)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE, blank = True, null = True)
    ordered = models.BooleanField(default=False)

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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE)
    ref_code = models.CharField(max_length=30)
    ordered = models.BooleanField(default=False)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now= True)
    ordered_date = models.DateTimeField()
    billing_address = models.ForeignKey('Address',related_name="billing_address" , on_delete=models.CASCADE, blank = True, null = True)
    shipping_address = models.ForeignKey('Address', related_name="shipping_address" ,on_delete=models.CASCADE, blank = True, null = True)
    payment = models.ForeignKey('Payment', on_delete=models.CASCADE, blank = True, null = True)
    coupon = models.ForeignKey('Coupon', on_delete=models.CASCADE, blank = True, null = True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default = False)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        
        return total

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length = 100)
    suburb = models.CharField(max_length = 100)
    phone_number = models.CharField(max_length = 10)
    country = CountryField(multiple = False)
    zip = models.CharField(max_length = 6)
    address_type = models.CharField(max_length = 1, choices = ADRESS_CHOICES)
    default = models.BooleanField(default = False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = "Direcciones"

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length = 50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete = models.SET_NULL, blank = True, null = True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.user.username

class Coupon(models.Model):
    code = models.CharField(max_length = 15)
    amount = models.FloatField()

    def __str__(self):
        return self.code

class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete = models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.pk}"