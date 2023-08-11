from django.urls import path
from . import views
from django.conf import settings
from django.core.mail import send_mail


app_name = 'cart'

urlpatterns = [
    path('', views.CartView.as_view(), name='summary'),
    path('shop/', views.ProductListView.as_view(), name='product-list'),
    path('shop/<slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('increase-quantity/<pk>/',
         views.IncreaseQuantityView.as_view(), name='increase-quantity'),
    path('decrease-quantity/<pk>/',
         views.DecreaseQuantityView.as_view(), name='decrease-quantity'),
    path('remove-from-cart/<pk>/',
         views.RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/', views.PaymentView.as_view(), name='payment'),
    path('thank-you/', views.ThankYouView.as_view(), name='thank-you'),
    path('confirm-order/', views.ConfirmOrderView.as_view(), name='confirm-order'),
    path('orders/<pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('bank-payment/', views.BankPayment.as_view(), name='bank-payment'),
    path('delivery-payment/', views.DeliveryPayment.as_view(), name='delivery-payment'),
    path('searh_products', views.search_view, name='search_products'),
    path('invoice/<int:facture_id>/', views.FactureView.as_view(), name='facture'),
    # path('pdf/', views.pdf_invoice, name='pdf-invoice'),

]
