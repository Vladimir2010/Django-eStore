from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('edit-profile/', views.edit_profile_view, name='edit-profile'),
    path('add-firm/', views.add_firm_view, name='add-firm'),
    path('view-firms/', views.view_firms, name='view-firms'),
    path('update-cart/<int:product_id>/', views.update_cart_view, name='update-cart'),
    path('remove-firm/<int:firm_id>/', views.remove_firm, name='remove-firm'),
]
