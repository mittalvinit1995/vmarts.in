from django.urls import path
from .views import index,product,Cartview,CheckoutView,add_to_cart,remove_from_cart,remove_single_item_from_cart,shop,showcategory,chat,ChatbotView
app_name='public'

urlpatterns = [
    path('', index, name='index'),
    path('category/<path:hierarchy>/',showcategory,name='category'),
    path('product/<slug>/', product, name='product'),
    path('cart/', Cartview.as_view(), name='cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('shop/', shop.as_view(),name='shop'),
    path('chat/',chat,name='chat'),
    path('chatbot/',ChatbotView.as_view(),name='chatbot'),
  ]
