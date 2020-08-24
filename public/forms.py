from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('E', 'Check Payment'),
    ('P', 'PayPal'),
    ('D', ' Direct Bank Tranfer'),
    ('C', ' Cash On Delivery')

)


class CheckoutForm(forms.Form):
    first_name =forms.CharField(max_length=50, widget=forms.TextInput(attrs={
        'Placeholder': 'First Name',
        'class': 'form-control'}))
    last_name =forms.CharField(max_length=30,widget=forms.TextInput(attrs={
        'Placeholder': 'Last Name',
        'class': 'form-control'}))
    country=CountryField(blank_label='Select Country').formfield(
        required=True,
        widget=CountrySelectWidget(attrs={
            'class' :'form-control'
        }))
    city=forms.CharField(required=True,max_length=70,widget=forms.TextInput(attrs={'Placeholder': 'City / Town','class' :'form-control'}))
    apartment=forms.CharField(required=False,max_length=70,widget=forms.TextInput(attrs={'Placeholder':'Apartment /House No. ','class' :'form-control'}))
    Streetaddress=forms.CharField(required=True,max_length=120,widget=forms.TextInput(attrs={'Placeholder': 'Street / Colony ','class' :'form-control'}))
    zipcode=forms.CharField(required=True,max_length=70,widget=forms.TextInput(attrs={'Placeholder': 'ZipCode','class': 'form-control'}))
    phone=forms.CharField(required=True,widget=forms.TextInput(attrs={'Placeholder': 'Contact Number','class': 'form-control'}))
    email=forms.EmailField(required=False,widget=forms.TextInput(attrs={'Placeholder': 'Email Address','class': 'form-control'}))
    same_billing_address = forms.BooleanField(required=False)
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)
    set_default_billing = forms.BooleanField(required=False)
    use_default_billing = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)



class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()


class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)
