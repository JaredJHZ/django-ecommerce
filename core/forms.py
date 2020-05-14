from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from localflavor.mx.models import (MXZipCodeField)

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'Paypal')
)

class CheckoutForm(forms.Form):
    street_address = forms.CharField( widget = forms.TextInput(attrs = {
        'class': 'form-control'
    }) )

    suburb =  forms.CharField( widget = forms.TextInput(attrs = {
        'class': 'form-control'
    }) )

    country = CountryField(blank_label='(Elija un país)').formfield(
        widget = CountrySelectWidget(
            attrs = {
                'class': 'custom-select d-block w-100'
            }
        )
    )
    zip = forms.CharField(
        widget = forms.TextInput(
            attrs = {
                'class': 'form-control'
            }
        )
    )

    phone_number = forms.CharField(
        widget = forms.TextInput(
            attrs = {
                'type':'number',
                'class': 'form-control'
            }
        )
    )
    same_billing_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(choices=PAYMENT_CHOICES)

class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))
