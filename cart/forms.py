from django.contrib.auth import get_user_model
from django import forms
from .models import (OrderItem, Product, Address)
from core.models import Firm

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


class AddFirmToOrder(forms.ModelForm):
    selected_firm_for_order = forms.ModelChoiceField(Firm.objects.none(), required=False)

    class Meta:
        model = Firm
        fields = '__all__'
        exclude = ['user', 'is_deleted']
        widgets = {
            'name_of_firm': forms.TextInput(attrs={
                'placeholder': "Име на Фирма / Име на физ. лице"
            }),
            'bulstat': forms.TextInput(attrs={
                'placeholder': "ЕИК/ЕГН"
            }),
            'vat_number': forms.TextInput(attrs={
                'placeholder': "Номер по ЗДДС (по избор)"
            }),
            'address_by_registration': forms.TextInput(attrs={
                'placeholder': "Адрес по регистрация"
            }),
            'owner_of_firm': forms.TextInput(attrs={
                'placeholder': "МОЛ"
            }),
            'mobile_number': forms.TextInput(attrs={
                'placeholder': "Мобилен номер"
            }),
            'static_number': forms.TextInput(attrs={
                'placeholder': "Стационарен номер"
            }),
            'email': forms.TextInput(attrs={
                'placeholder': "Имейл"
            })
        }
        labels = {
            'name_of_firm': "Име на Фирма / Име на физ. лице",
            'bulstat': "ЕИК/ЕГН",
            'VAT_number': "Номер по ЗДДС (по избор)",
            'address_by_registration': "Адрес по регистрация",
            'owner_of_firm': "МОЛ",
            'mobile_number': "Мобилен номер",
            'static_number': "Стационарен номер",
            'email': "Имейл"
        }


    def __init__(self, *args, **kwargs):
        user_id = kwargs.get('user_id')
        if kwargs.get('user_id'):
            user_id = kwargs.pop('user_id')
            super().__init__(*args, **kwargs)
        else:
            super().__init__(*args, **kwargs)

        user = User.objects.get(id=user_id)

        firm_form_qs = Firm.objects.filter(
            user=user,
            is_deleted=False
        )

        self.fields['selected_firm_for_order'].queryset = firm_form_qs
        self.fields['selected_firm_for_order'].label = "Избери Фирма за фактура"


class AddressForm(forms.ModelForm):
    selected_shipping_address = forms.ModelChoiceField(Address.objects.none(), required=False)

    class Meta:
        model = Address
        fields = '__all__'
        exclude = ['user', 'default', 'address_type']
        widgets = {
            'address_line_1': forms.TextInput(attrs={
                'placeholder': "Адрес за доставка",

            }),
            'address_line_2': forms.TextInput(attrs={
                'placeholder': "Адрес за доставка 2"
            }),
            'zip_code': forms.TextInput(attrs={
                'placeholder': "Пощенски код"
            }),
            'city': forms.TextInput(attrs={
                'placeholder': "Град"
            }),
        }
        labels = {
            'address_line_1': "Адрес за доставка",
            'address_line_2': "Адрес за доставка 2",
            'zip_code': "Пощенски код",
            'city': "Град",

        }

    def __init__(self, *args, **kwargs):
        if kwargs.get('user_id'):
            user_id = kwargs.pop('user_id')
            super().__init__(*args, **kwargs)
        else:
            super().__init__(*args, **kwargs)

        user = User.objects.get(id=user_id)

        shipping_address_qs = Address.objects.filter(
            user=user,
            address_type='S'
        )
        self.fields['selected_shipping_address'].queryset = shipping_address_qs
        self.fields['selected_shipping_address'].label = "Избери адрес за доставка"

