from django.contrib import admin

# Register your models here.

from .models import Item, Order, OrderItem, Payment, BillingAddress, Coupon

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered']

admin.site.register(Item)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(BillingAddress)
admin.site.register(Coupon)