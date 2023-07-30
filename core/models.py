from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser


class CustomUserModel(AbstractUser):
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class OwnerFirm(models.Model):
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)
    name_of_firm = models.CharField(max_length=100)
    bulstat = models.CharField(max_length=9, unique=True)
    VAT_number = models.CharField(max_length=11, unique=True, null=True, blank=True)
    address_by_registration = models.CharField(max_length=300)
    address_of_shop = models.CharField(max_length=300, null=True, blank=True)
    activity = models.CharField(max_length=150)
    owner_of_firm = models.CharField(max_length=100)
    mobile_number_of_firm = models.CharField(max_length=13)
    static_number_of_firm = models.CharField(max_length=15, null=True, blank=True)

    @property
    def is_vat(self):
        if not self.VAT_number is None:
            return True
        return False

    @property
    def is_have_address_shop(self):
        if not self.address_of_shop is None:
            return True
        return False

    @property
    def is_static_number_of_firm(self):
        if not self.static_number_of_firm is None:
            return True
        return False


    def __str__(self):
        return self.name_of_firm


class Firm(models.Model):
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)
    name_of_firm = models.CharField(max_length=100)
    bulstat = models.CharField(max_length=9, unique=True)
    VAT_number = models.CharField(max_length=11, unique=True, null=True, blank=True)
    address_by_registration = models.CharField(max_length=200)
    owner_of_firm = models.CharField(max_length=100)

    @property
    def is_vat(self):
        if not self.VAT_number is None:
            return True
        return False

    def __str__(self):
        return self.name_of_firm

class Customer(models.Model):
    user = models.OneToOneField(CustomUserModel, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.email


def post_save_user_receiver(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance)


post_save.connect(post_save_user_receiver, sender=CustomUserModel)
