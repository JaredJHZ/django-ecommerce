from django.contrib import admin

# Register your models here.

from .models import Item, Order, OrderItem, Payment, Address, Category

def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested = False , refund_granted = True)

make_refund_accepted.short_description = 'Actualizar ordenes a reembolso realizado'
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered','payment' ,'shipping_address']
    list_filter = ['user', 'ordered']
    list_display_links = ['user','shipping_address','payment']
    search_fields = ['user__username','ref_code']
    actions = [make_refund_accepted]
    filter_horizontal = ('items',)

class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'street_address', 'suburb', 'state','zip','address_type','default']
    list_filter = [ 'address_type','default','country']
    search_fields = ['user','street_address','suburb','zip']


admin.site.site_header = "Patyshop ";
admin.site.site_title = "Administrador de Patyshopth";
admin.site.register(Item)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(Address)
admin.site.register(Category)

