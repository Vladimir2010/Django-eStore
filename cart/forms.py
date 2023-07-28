from django.contrib.auth import get_user_model
from django import forms
from .models import (OrderItem, Product, Address)

User = get_user_model()


class AddToCartForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=1, initial=1)

    class Meta:
        model = OrderItem
        fields = ['quantity']

    def __init__(self, *args, **kwargs):
        self.product_id = kwargs.pop('product_id')
        product = Product.objects.get(id=self.product_id)
        super().__init__(*args, **kwargs)
        self.fields["quantity"].label = "Количество"

    def clean(self):
        product_id = self.product_id
        product = Product.objects.get(id=self.product_id)
        quantity = self.cleaned_data['quantity']
        if product.stock < quantity:
            raise forms.ValidationError(
                f"Максималното налично количество е: {product.stock}")


class AddressForm(forms.Form):
    shipping_address_line_1 = forms.CharField(required=False)
    shipping_address_line_2 = forms.CharField(required=False)
    shipping_zip_code = forms.CharField(required=False)
    shipping_city = forms.CharField(required=False)

    selected_shipping_address = forms.ModelChoiceField(Address.objects.none(), required=False)

    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop('user_id')
        super().__init__(*args, **kwargs)

        user = User.objects.get(id=user_id)

        shipping_address_qs = Address.objects.filter(
            user=user,
            address_type='S'
        )

        self.fields['selected_shipping_address'].queryset = shipping_address_qs
        # labels
        self.fields['shipping_address_line_1'].label = "Адрес за доставка"
        self.fields['shipping_address_line_2'].label = "Адрес за доставка 2"
        self.fields['shipping_zip_code'].label = "Пощенски код"
        self.fields['shipping_city'].label = "Град"
        self.fields['selected_shipping_address'].label = "Избери адрес за доставка"
        self.fields['shipping_address_line_2'].required = False

    def clean(self):
        data = self.cleaned_data

        selected_shipping_address = data.get('selected_shipping_address', None)
        if selected_shipping_address is None:
            if not data.get('shipping_address_line_1', None):
                self.add_error("shipping_address_line_1", "Моля попълнете полето")
            # if not data.get('shipping_address_line_2', None):
            #     self.add_error("shipping_address_line_2", "Моля попълнете полето")
            if not data.get('shipping_zip_code', None):
                self.add_error("shipping_zip_code", "Моля попълнете полето")
            if not data.get('shipping_city', None):
                self.add_error("shipping_city", "Моля попълнете полето")
