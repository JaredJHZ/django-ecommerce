from django import forms


from localflavor.mx.models import (MXZipCodeField)

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'Paypal')
)

FROM_GUADALAJARA = (
    ('S', 'Si'),
    ('N', 'No')
)

class CheckoutForm(forms.Form):

    shipping_address = forms.CharField(required = True )

    suburb_shipping =  forms.CharField( required = True )

    shipping_zip = forms.CharField(required = True)

    shipping_phone_number = forms.CharField(required = True)

    set_default_shipping = forms.BooleanField(required = False)

    from_guadalajara = forms.ChoiceField(choices = FROM_GUADALAJARA , required = True )

    shipping_state = forms.CharField(required = True)

    payment_option = forms.ChoiceField(choices=PAYMENT_CHOICES)

    city = forms.CharField( required = True )

    inside_guadalajara = forms.CharField( required = False )
