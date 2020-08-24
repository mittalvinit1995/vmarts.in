from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.views.generic import ListView, DetailView, View
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Item, Slider,Order,OrderItem, Address,Category
from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm
from django.http import HttpResponse,JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .responce_df import *
from .richresponce import *
from django.utils.decorators import method_decorator

# Create your views here.
        
def index(request):
    content ={
         'items': Item.objects.all(),
         'sliders': Slider.objects.all(),
     }
    return render(request,'index.html',content)

def showcategory(request,hierarchy= None):
    pass
#     category_slug = hierarchy.split('/')
#     parent = None
#     for slug in category_slug[:-1]:
#         parent = root.get(parent=parent, slug = slug)

#     try:
#         instance = Category.objects.get(parent=parent,slug=category_slug[-1])
#     except:
#         instance = get_object_or_404(Item, slug = category_slug[-1])
#         return render(request, "index.html", {'contents':contents})
#     else:
#         contents=[content,instance]
#         return render(request, 'index.html', {'contents':contents})
   
    
    
def product(request,slug): 
    content ={
        'items': Item.objects.filter(product_slug=slug)
    }
    return render(request,'product.html', content)



@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, product_slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__product_slug=item.product_slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("public:cart")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("public:cart")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("public:cart")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, product_slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__product_slug=item.product_slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart.")
            return redirect("public:cart")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("public:cart", product_slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("public:cart", product_slug=slug)


class shop(DetailView):
    model = Item
    paginate_by = 4
    template_name = "shop.html"
         
class Cartview(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'cart.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, product_slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__product_slug=item.product_slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("public:cart")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("public:product", product_slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("public:product", product_slug=slug)

class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs[0]})

            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("public:checkout")


    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        print(self.request.POST)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Using the defualt shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('public:checkout')
                else:
                    print("User is entering a new shipping address")
                    first_name = form.cleaned_data.get('first_name')
                    last_name = form.cleaned_data.get('last_name')
                    country = form.cleaned_data.get('shipping_country')
                    city = form.cleaned_data.get('city')
                    streetaddress =  form.cleaned_data.get('streetaddress')
                    zipcode = form.cleaned_data.get('zipcode')
                    phone = form.cleaned_data.get('shipping_zip')
                    email = form.cleaned_data.get('email')
                    if is_valid_form([first_name,last_name,country,city,streetaddress,zipcode,phone,email]):
                        shipping_address = Address(
                            FirstName=first_name,
                            LastName=last_name,
                            Country=country,
                            City=city,
                            street_address=streetaddress,
                            zip=zipcode,
                            Phone=phone,
                            Email=email,
                            address_type='S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")

                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    print("Using the defualt billing address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default billing address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new billing address")
                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_country = form.cleaned_data.get(
                        'billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required billing address fields")

                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('core:payment', payment_option='paypal')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")
#pending (DataBase and Connect handlling Task Goes Here) 
@csrf_exempt
def chat(request):
    #Get Intent 
    intent=json.loads(request.body).get('queryResult').get('intent').get('displayName')
    #Get Parmeters
    parameter = json.loads(request.body).get('queryResult').get('parameters')
    if 'all_category' == intent:
        results =Category.objects.all()
        categoryNumber=len(list(results))
        categoryList = [i for i in results]
        return JsonResponse(
                      {"fulfillmentText":  "No of Categories :" +str(categoryNumber) + "  Category" + str(results)}   
                       )
    elif 'ProductPrice' ==intent:
        value=list(parameter.values())[1]
        results =Item.objects.raw("""SELECT *FROM vmart.public_item where product_title='{}' """.format(value))
        if len(list(results)) ==1:
            for i in results:
                product=i.product_price if i.product_offer is not True else i.product_discount_price
                productUrl=i.product_slug
                #url='<a href="~/add-to-cart/{}/" >Add to Cart</a>'.format(i.product_slug)
            return JsonResponse(
                            {"fulfillmentText": str(int(product))   + '<a href="http://10.0.1.86/add-to-cart/{}/" >Add to Cart</a>'.format(productUrl)
                            
                            })
        else:
            return JsonResponse(
                            {"fulfillmentText":'oops Product is not avaliable on this Site'})

    elif 'Other' == intent:
        print('good')
        pass
    else:
        pass

  
    
# @csrf_exempt
# def chatbot(request):
#     help='help'
#     return render(request,'chatbotclient.html')



class ChatbotView(TemplateView):
    template_name = 'chatbotclient.html'
    @method_decorator(csrf_exempt)
    def get_context_data(self, **kwargs):
        context = super(ChatbotView, self).get_context_data(**kwargs)
        context['Item'] = Item.objects.all()
        # context['modeltwo'] = ModelTwo.objects.get(*query logic*)
        return context
