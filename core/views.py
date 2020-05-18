from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Refund, Address
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm, CouponForm, RefundForm
import stripe
import random
import string

stripe.api_key = "sk_test_En70VblPfMWFvxVyvh9Knszb00XdGJY9co"

def craete_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

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
                'order':order,
                'couponform': CouponForm(),
                'DISPLAY_COUPON_FORM': True
            }

            shipping_address_qs = Address.objects.filter(user = self.request.user, address_type = 'E', default = True)

            if shipping_address_qs.exists():
                context.update({'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(user = self.request.user, address_type = 'F', default = True)

            if billing_address_qs.exists():
                context.update({'default_billing_address': billing_address_qs[0]})

        except ObjectDoesNotExist:
            messages.info(self.request, "No tienes una orden activa")
            return redirect("core:checkout")

    
        return render(self.request, "checkout-page.html", context)
    
    def post(self , *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered = False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get('use_default_shipping')
                print(use_default_shipping)

                if use_default_shipping:
                    print("usando direccion default")
                    shipping_address_qs = Address.objects.filter(user = self.request.user, address_type = 'E', default = True)
                    if shipping_address_qs.exists():
                        shipping_address = shipping_address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(self.request, "No existe la direccion")
                        return redirect("core:checkout")
                else:
                    print("nueva direccion")
                    shipping_address = form.cleaned_data.get('shipping_address')
                    suburb_shipping = form.cleaned_data.get('suburb_shipping')
                    shipping_country = form.cleaned_data.get('shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')
                    shipping_phone_number = form.cleaned_data.get('shipping_phone_number')

                    if is_valid_form([shipping_address, suburb_shipping, shipping_country,shipping_zip, shipping_phone_number]):
                        print("ok shipping")
                        shipping_address = Address(
                            user = self.request.user,
                            street_address = shipping_address,
                            suburb = suburb_shipping,
                            country = shipping_country,
                            zip = shipping_zip,
                            phone_number = shipping_phone_number,
                            address_type = 'E'
                        )
                        print(shipping_address)
                        shipping_address.save()
                        order.shipping_address = shipping_address
                        order.save()
                        set_default_shipping = form.cleaned_data.get('set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()
                    else:
                        messages.info(self.request, "Agregue todos los valores")
                        return redirect("core:checkout")



                use_default_billing = form.cleaned_data.get('use_default_billing')

                same_billing_address = form.cleaned_data.get('same_billing_address')

                print(same_billing_address)

                if same_billing_address:
                    print("same")
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'F'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    print("Usando una direccion de facturacion default")
                    billing_address_qs = Address.objects.filter(user = self.request.user, address_type = 'F', default = True)

                    if billing_address_qs.exists():

                        billing_address = billing_address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(self.request, "No existe la direccion def facturacion")
                        return redirect("core:checkout")
                else:
                    billing_address = form.cleaned_data.get('billing_address')
                    suburb_billing = form.cleaned_data.get('suburb_billing')
                    billing_country = form.cleaned_data.get('billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')
                    billing_phone_number = form.cleaned_data.get('billing_phone_number')

                    if is_valid_form([billing_address, suburb_billing, billing_country,billing_zip, billing_phone_number]):
                        billing_address = Address(
                            user = self.request.user,
                            street_address = billing_address,
                            suburb = suburb_billing,
                            country = billing_country,
                            zip = billing_zip,
                            phone_number = billing_phone_number,
                            address_type = 'F'
                        )
   
                        set_default_billing = form.cleaned_data.get('set_default_billing')
       
                        if set_default_billing:
                         
                            billing_address.default = True
                        billing_address.save()
                        order.billing_address = billing_address
                        order.save()

                    else:
                        messages.info(self.request, "Agregue todos los valores")
                        return redirect("core:checkout")

                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'S':
                    return redirect('core:payment', payment_option="stripe")
                else:
                    return redirect('core:payment', payment_option="paypal")
            else:
                messages.info(self.request,"Hubo un problema con su formulario de pago")
                return redirect('core:order-summary')
        except:
            messages.warning(self.request, "No tienes una orden activa")
            return redirect('core:order-summary')


class PaymentView(View):
    def get(self, *args, **kwargs):
        # order
        order = Order.objects.get(user = self.request.user, ordered = False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False
            }

            return render(self.request, "payment.html"  , context = context)
        else:
            messages.warning(self.request , "No tienes una direccion activa")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user = self.request.user, ordered = False)
        token = self.request.POST.get('stripeToken')
        print("token")
        print(self.request.POST)
        amount = int(order.get_total()) 

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
            payment.amount = order.get_total()
            payment.save()

            order_items = order.items.all()
            order_items.update(ordered = True)
            for item in order_items:
                item.save()

            order.ordered = True
            order.payment = payment

            order.ref_code = create_ref_code()

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


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code = code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "El cupon no es valido")
        return redirect("core:checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get("code")
                order = Order.objects.get(user = self.request.user, ordered = False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success("Se ha agregado el cupon")
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(request, "No tienes una orden activa")
                return redirect("core:checkout")

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
                