from django.contrib import admin
from .models import Customer


class CustomerAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user']

admin.site.register(Customer, CustomerAdmin)
