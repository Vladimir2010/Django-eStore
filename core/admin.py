from django.contrib import admin
from .models import Customer, CustomUserModel, Firm, OwnerFirm


class CustomerAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user']

class OwnerFirmAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user', 'bulstat', 'owner_of_firm']

admin.site.register(Customer, CustomerAdmin)
admin.site.register(CustomUserModel)
admin.site.register(Firm)
admin.site.register(OwnerFirm, OwnerFirmAdmin)
