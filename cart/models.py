from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_save
from django.shortcuts import reverse
from django.utils.text import slugify
from .validators import check_bank_account
from core.models import CustomUserModel, Firm, OwnerFirm

User = CustomUserModel


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Address(models.Model):
    ADDRESS_CHOICES = (
        ('S', 'Shipping'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address_line_1 = models.CharField(max_length=150)
    address_line_2 = models.CharField(max_length=150, null=True, blank=True)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.address_line_1}, {self.address_line_2}, {self.city}, {self.zip_code}"

    class Meta:
        verbose_name_plural = 'Addresses'


class Product(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='product_images')
    description = models.TextField()
    price = models.FloatField(default=0.00)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    primary_category = models.ForeignKey(Category, related_name='primary_products', blank=True, null=True,
                                         on_delete=models.CASCADE)
    secondary_categories = models.ManyToManyField(Category, blank=True)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("cart:product-detail", kwargs={'slug': self.slug})

    def get_update_url(self):
        return reverse("staff:product-update", kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse("staff:product-delete", kwargs={'pk': self.pk})

    def get_price(self):
        return "{:.2f}".format(self.price)

    @property
    def in_stock(self):
        if self.stock > 0:
            return True
        else:
            return False


class OrderItem(models.Model):
    order = models.ForeignKey(
        "Order", related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"

    def get_raw_total_item_price(self):
        return self.quantity * self.product.price

    def get_total_item_price(self):
        price = self.get_raw_total_item_price()
        return "{:.2f}".format(price)


class Order(models.Model):
    user = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(blank=True, null=True)
    ordered = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=15,
                                      choices=(
                                          ('Наложен платеж', 'Наложен платеж'),
                                          ('Банков път', 'Банков път')),
                                      null=True,
                                      blank=True)

    shipping_address = models.ForeignKey(
        Address, related_name='shipping_address', blank=True, null=True, on_delete=models.SET_NULL)
    firm = models.ForeignKey(
        Firm, related_name='firm', blank=True, null=True, on_delete=models.SET_NULL)
    facture_need = models.BooleanField(default=False)

    def __str__(self):
        return self.reference_number

    def is_delivery_payment(self):
        if self.payment_method == 'Наложен платеж':
            return True
        return False

    @property
    def get_payment_method(self):
        return self.payment_method

    @property
    def order_number(self):
        return self.pk

    @property
    def reference_number(self):
        return f"Поръчка-{self.pk}"

    def get_raw_subtotal(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_raw_total_item_price()
        return total

    def get_subtotal(self):
        subtotal = self.get_raw_subtotal()
        return "{:.2f}".format(subtotal)

    def get_raw_total(self):
        subtotal = self.get_raw_subtotal()
        return subtotal

    def get_total(self):
        total = self.get_raw_total()
        return "{:.2f}".format(total)

    @property
    def get_full_user_name(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Payment(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=20, choices=(
        ('Наложен платеж', 'Наложен платеж'),
        ('Банков път', 'Банков път'),
    ))
    date_of_payment = models.DateTimeField(auto_now_add=True)
    successful = models.BooleanField(default=False)
    amount = models.FloatField()

    def __str__(self):
        return self.reference_number

    @property
    def reference_number(self):
        return f"Плащане-{self.order}-{self.pk}"


def pre_save_product_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)


pre_save.connect(pre_save_product_receiver, sender=Product)


class BankAccount(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    IBAN = models.CharField(max_length=22, unique=True, validators=[check_bank_account])
    BIC = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100)
    name_of_firm = models.BooleanField(default=False)

    @property
    def get_full_name(self):
        if self.get_is_firm:
            return self.first_name
        return f"{self.first_name} {self.last_name}"

    @property
    def get_name(self):
        if self.get_is_firm:
            return self.first_name
        else:
            return f"{self.first_name} {self.last_name}"

    @property
    def get_is_firm(self):
        if self.name_of_firm:
            return True
        return False

    def __str__(self):
        return self.get_name


class Facture(models.Model):
    number_of_facture = models.CharField(max_length=15)
    type_of_facture = models.CharField(max_length=16, choices=[
        ('Проформа Фактура', 'Проформа Фактура'),
        ('Фактура', 'Фактура')
    ])
    date_of_facture = models.DateField(auto_now_add=True)
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)
    firm = models.ForeignKey(Firm, on_delete=models.CASCADE)
    owner_firm = models.ForeignKey(OwnerFirm, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    bank = models.ForeignKey(BankAccount, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.number_of_facture} / {self.date_of_facture}"
