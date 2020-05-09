from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from .models import Item, OrderItem, Order, BillingAddress
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm

class CheckoutView(View):
    def get(self, *args , **kwargs): 
        form = CheckoutForm()
        context  = {
            'form':form
        }
        return render(self.request, "checkout-page.html", context)
    
    def post(self , *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered = False)
            print(order)
            if form.is_valid():
                print("form valid")
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # same_billing_address = form.cleaned_data.get('same_billing_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                
                print(street_address)
                print(apartment_address)
                print(country)
                print(zip)
                print(payment_option)

                billing_address = BillingAddress(
                    user = self.request.user,
                    street_address = street_address,
                    apartment_address = apartment_address,
                    country = country,
                    zip = zip
                )

                print(billing_address)
                billing_address.save()
                order_billing_address = billing_address
                order.save()
                return redirect('core:checkout')
            messages.warning(self.request, "Algo fallo")
            return redirect('core:checkout')
        except:
            messages.warning(self.request, "No tienes una orden activa")
            return redirect('core:order-summary')





def product_page(request):
    return render(request, "product-page.html")

class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = "home-page.html"

class OrderSummaryView(LoginRequiredMixin,View):
    def get(self, *args , **kwargs):
        try:
            order = Order.objects.get(user = self.request.user, ordered = False)
            context = {
                'object': order
            }
            return render(self.request,'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(request, "No tienes una orden activa")
            return redirect("/")

class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"

@login_required
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
    return redirect("core:order-summary")

@login_required
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
            return redirect("core:order-summary")
    else:
        messages.info(request, "No tienes una orden activa!")
        return redirect("core:product_page", slug = slug)
    return redirect("core:product_page", slug = slug)

@login_required
def remove_single_item_from_cart(request, slug):
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
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
                order_item.delete()
            messages.info(request, "Se ha eliminado un articulo fue eliminado de tu carrito")
            return redirect('core:order-summary')
        else:
            messages.info(request, "Este articulo no se encontraba en tu carrito")
            return redirect("core:product_page", slug = slug)
    else:
        messages.info(request, "No tienes una orden activa!")
        return redirect("core:product_page", slug = slug)
    return redirect("core:product_page", slug = slug)

