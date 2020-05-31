from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from .models import Item, OrderItem, Order, Address, Payment, Refund, Address
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm
import stripe
import random
import string

stripe.api_key = "sk_test_En70VblPfMWFvxVyvh9Knszb00XdGJY9co"


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid

class CheckoutView(View):
    def get(self, *args , **kwargs): 
        try:
            order = Order.objects.get(user = self.request.user, ordered = False)
            form = CheckoutForm()
            context  = {
                'form':form,
                'order':order
            }

            shipping_address_qs = Address.objects.filter(user = self.request.user, default = True)

            if shipping_address_qs.exists():
                context.update({'default_shipping_address': shipping_address_qs[0]})

        except ObjectDoesNotExist:
            messages.info(self.request, "No tienes una orden activa")
            return redirect("core:checkout")

    
        return render(self.request, "checkout-page.html", context)
    
    def post(self , *args, **kwargs):
        print(self.request.POST)
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered = False)
            if form.is_valid():
                if False:
                    pass
                else:
                    shipping_address = form.cleaned_data.get('shipping_address')
                    suburb_shipping = form.cleaned_data.get('suburb_shipping')
                    shipping_country = form.cleaned_data.get('shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')
                    shipping_phone_number = form.cleaned_data.get('shipping_phone_number')
                    shipping_state = form.cleaned_data.get('shipping_state')
                    inside_guadalajara = form.cleaned_data.get('inside_guadalajara')                  

                    if is_valid_form([shipping_address, suburb_shipping, shipping_country,shipping_zip, shipping_phone_number, shipping_state]):

                        punto_medio = False

                        print("okidoki")

                        if inside_guadalajara != '':
                            if inside_guadalajara != 'medio':
                                order.sent_price = 80
                            else:
                                order.sent_price = 0
                                punto_medio = True
                                point = form.cleaned_data.get('point')  
                                print(point)
                        else:
                            order.sent_price = 130

                        if punto_medio:
                            shipping_address = Address(
                            user = self.request.user,
                            street_address = shipping_address,
                            suburb = suburb_shipping,
                            zip = shipping_zip,
                            phone_number = shipping_phone_number,
                            state = shipping_state,
                            point = point
                            )
                        else:
                            shipping_address = Address(
                            user = self.request.user,
                            street_address = shipping_address,
                            suburb = suburb_shipping,
                            zip = shipping_zip,
                            phone_number = shipping_phone_number,
                            state = shipping_state
                            )


                        
                        shipping_address.save()
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(self.request, "Agregue todos los valores")
                        return redirect("core:checkout")


                payment_option = form.cleaned_data.get('payment_option')

                print(payment_option)

                if payment_option == 'S':
                    return redirect('core:payment', payment_option="stripe")
                else:
                    return redirect('/paypal', payment_option="paypal")
            else:
                messages.info(self.request,"Hubo un problema con su formulario de pago")
                return redirect('core:order-summary')
        except:
            messages.warning(self.request, "No tienes una orden activa")
            return redirect('core:order-summary')


class PaypalView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user = self.request.user, ordered = False)
        if order.shipping_address:
            context = {
                'order': order
            }
            return render(self.request, "paypal.html"  , context = context)

def paypal_response(request):

    order = Order.objects.get(user = request.user, ordered = False)
    amount = int(order.get_total() + order.sent_price) 
    payment = Payment()
    payment.stripe_charge_id = "PAYPAL"
    payment.user = request.user
    payment.amount = order.get_total() + order.sent_price
    payment.save()
    order_items = order.items.all()
    order_items.update(ordered = True)
    for item in order_items:
        item.save()
    order.ordered = True
    order.payment = payment
    order.ordered_date = timezone.now()

    for order_item in order.items.all():
        nueva_cantidad = order_item.item.stock - order_item.quantity
        Item.objects.filter(title = order_item.item.title).update(stock = nueva_cantidad)

    order.save()


    messages.info(request, "Se completo el pedido")

    
    return HttpResponse("hecho")

class PaymentView(View):
    def get(self, *args, **kwargs):
        # order
        order = Order.objects.get(user = self.request.user, ordered = False)
        if order.shipping_address:
            context = {
                'order': order
            }

            return render(self.request, "payment.html"  , context = context)
        else:
            messages.warning(self.request , "No tienes una direccion activa")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user = self.request.user, ordered = False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() + order.sent_price) 

        try:
            charge = stripe.Charge.create(
                amount = amount * 100,
                currency = "MXN",
                source = token,
                description = "cargo de patyshop"
            )

            
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total() + order.sent_price
            payment.save()

            order_items = order.items.all()
            order_items.update(ordered = True)
            for item in order_items:
                item.save()

            order.ordered = True
            order.payment = payment
            order.ordered_date = timezone.now()

            for order_item in order.items.all():
                nueva_cantidad = order_item.item.stock - order_item.quantity
                Item.objects.filter(title = order_item.item.title).update(stock = nueva_cantidad)

            order.save()
            messages.success(self.request,"Pedido confirmado")
            return redirect("/")
        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, f"{err.get('message')}")
            return redirect("/")

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request, "Rate limit error")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            print(e)
            messages.warning(self.request, "Invalid parameters")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(self.request, "Not authenticated")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
            messages.warning(self.request, "Network error")
            return redirect("/")

        except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
            messages.warning(
                self.request, "Something went wrong. You were not charged. Please try again.")
            return redirect("/")

        except Exception as e:
            # send an email to ourselves
            messages.warning(
                self.request, "A serious error occurred. We have been notifed.")
            return redirect("/")     

def product_page(request):
    return render(request, "product-page.html")

class HomeView(ListView):
    model = Item
    paginate_by = 4
    template_name = "home-page.html"

class MyOrders(LoginRequiredMixin, ListView):

    model = Order
    template_name = "my-orders.html"
    def get_queryset(self):
          return Order.objects.filter(user = self.request.user, ordered = True)

class HomeFilter(ListView):

    model = Item
    paginate_by = 4
    template_name = "home-page.html"

    def get_queryset(self):
        filter_val = self.request.GET.get('filter', 'give-default-value')
        if len(filter_val) > 0:
            new_context = Item.objects.filter(
                category=filter_val,
            )
        else:
            new_context = Item.objects.all()
        
        if len(new_context) < 1:
            new_context = []
        
        return new_context

    def get_context_data(self, **kwargs):
        context = super(HomeFilter, self).get_context_data(**kwargs)
        context['filter'] = self.request.GET.get('filter', 'give-default-value')
        return context
class SearchFilter(ListView):
    model = Item
    paginate_by = 10
    template_name = "search.html"

    def get_queryset(self):
        filter_val = self.request.GET.get('filter', 'give-default-value')
        new_context = Item.objects.filter(
            title__icontains=filter_val
        )
        print(len(new_context))
        return new_context
    
    def get_context_data(self, **kwargs):
        context = super(SearchFilter, self).get_context_data(**kwargs)
        context['filter'] = self.request.GET.get('filter','give-default-value')
        return context

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
    print(item)
    order_item, created = OrderItem.objects.get_or_create(
        item = item,
        user = request.user,
        ordered = False
        )
    print(order_item.quantity)
    order_qs = Order.objects.filter(user = request.user, ordered = False)

    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug= item.slug).exists():
            if order_item.item.stock >= order_item.quantity + 1:
                order_item.quantity += 1
                order_item.save()
                messages.info(request, "Se agrega otro articulo de este tipo a tu carrito")
            else:
                messages.info(request, "Ya no hay mas en Stock")
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


# def get_coupon(request, code):
#     try:
#         coupon = Coupon.objects.get(code = code)
#         return coupon
#     except ObjectDoesNotExist:
#         messages.info(request, "El cupon no es valido")
#         return redirect("core:checkout")


# class AddCouponView(View):
#     def post(self, *args, **kwargs):
#         form = CouponForm(self.request.POST or None)
#         if form.is_valid():
#             try:
#                 code = form.cleaned_data.get("code")
#                 order = Order.objects.get(user = self.request.user, ordered = False)
#                 order.coupon = get_coupon(self.request, code)
#                 order.save()
#                 messages.success("Se ha agregado el cupon")
#                 return redirect("core:checkout")
#             except ObjectDoesNotExist:
#                 messages.info(request, "No tienes una orden activa")
#                 return redirect("core:checkout")

class RequestRefundView(View):

    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self,*args, **kwargs):
        form = RefundForm(request.POST)
        if form.is_valid():
            ref_code =form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            try:
                order = Order.objects.get(ref_code = ref_code)
                order.refund_requested = True
                order.save()

                refund = Refund()
                refund.order = order
                refund.reason = message

                messages.info(self.request, "Tu solicitud ha sido enviada")

                refund.save()
                return redirect('/')
            except ObjectDoesNotExist:
                messages.info(self.request, "No existe la orden")
                return redirect("core:request-refund")
                