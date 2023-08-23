from django.contrib import admin
from .models import (Product, OrderItem, Order, Address, Payment, Category, BankAccount)


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'address_line_1',
        'address_line_2',
        'city',
        'zip_code',
        'address_type',
    ]

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'active', 'primary_category']

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['start_date', 'ordered', 'ordered_date']


class BankAccountDisplay(admin.ModelAdmin):
    list_display = [
        'first_name',
        'last_name',
        'IBAN',
        'BIC',
        'bank_name'
    ]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(BankAccount, BankAccountDisplay)
