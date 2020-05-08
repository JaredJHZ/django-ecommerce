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

class Item(models.Model):
    title = models.CharField(max_length = 100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length = 2)
    label = models.CharField(choices=LABEL_CHOICES, max_length = 2)
    slug = models.SlugField()
    discount_price = models.FloatField(blank=True, null=True)
    description = models.TextField()

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
    ordered = models.BooleanField(default=False)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now= True)
    ordered_date = models.DateTimeField()

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total