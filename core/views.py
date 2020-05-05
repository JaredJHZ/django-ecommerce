from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Item, OrderItem, Order
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages


def checkout(request):
    return render(request, "checkout-page.html")

def product_page(request):
    return render(request, "product-page.html")

class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = "home-page.html"

class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"

def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug = slug)
    order_item, created = OrderItem.objects.get_or_create(
        item = item,
        user = request.user,
        ordered = False
        )
    order_qs = Order.objects.filter(user = request.user, ordered = False)

    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug= item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Se agrega otro articulo de este tipo a tu carrito")
        else:
            messages.info(request, "Este articulo fue agregado a tu carrito")
            order.items.add(order_item)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Este articulo fue agregado a tu carrito")
    return redirect("core:product_page", slug = slug)

def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug = slug)
    order_qs = Order.objects.filter(user = request.user, ordered = False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug= item.slug).exists():
            order_item = OrderItem.objects.filter(
                item = item,
                user = request.user,
                ordered = False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "Este articulo fue eliminado de tu carrito")
        else:
            messages.info(request, "Este articulo no se encontraba en tu carrito")
            return redirect("core:product_page", slug = slug)
    else:
        messages.info(request, "No tienes una orden activa!")
        return redirect("core:product_page", slug = slug)
    return redirect("core:product_page", slug = slug)

