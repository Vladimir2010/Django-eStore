from django.contrib import admin
from .models import Customer, CustomUserModel, Firm


class CustomerAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user']

admin.site.register(Customer, CustomerAdmin)
admin.site.register(CustomUserModel)
admin.site.register(Firm)
