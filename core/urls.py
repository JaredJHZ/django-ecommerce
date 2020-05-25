from django.urls import path
from .views import (
    CheckoutView, HomeView, 
    ItemDetailView, add_to_cart, 
    remove_from_cart, OrderSummaryView, 
    remove_single_item_from_cart, PaymentView,
    RequestRefundView,
    HomeFilter,
    SearchFilter,
    MyOrders,
    PaypalView,
    paypal_response
)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view() , name="home"),
    path('items/', HomeFilter.as_view(), name="filter-home"),
    path('myorders/', MyOrders.as_view(), name="my-orders"),
    path('search/', SearchFilter.as_view(), name="search"),
    path('checkout/', CheckoutView.as_view(), name="checkout"),
    path('product/<slug>/', ItemDetailView.as_view(), name="product_page"),
    path('order-summary/', OrderSummaryView.as_view() ,name='order-summary'),
    path('add-to-cart/<slug>/', add_to_cart, name="add-to-cart"),
    path('remove-from-cart/<slug>/', remove_from_cart, name="remove-from-cart"),
    path('remove-item-from-cart/<slug>/',remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name = "payment"),
    path('paypal/', PaypalView.as_view() , name = "paypal"),
    path('request-refund/', RequestRefundView.as_view(), name="request-refund"),
    path('confirmpaypal/', paypal_response, name="paypal_response")
]