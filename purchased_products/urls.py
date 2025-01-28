from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_sale, name='create_sale'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
]