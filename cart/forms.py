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
    name_of_firm = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': "Име на Фирма / Име на физ. лице"
    }))
    bulstat = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': "ЕИК/ЕГН"
    }))
    VAT_number = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': "Номер по ЗДДС (по избор)"
    }))
    address_by_registration = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': "Адрес по регистрация"
    }))
    owner_of_firm = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': "МОЛ"
    }))
    mobile_number = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': "Мобилен номер"
    }))
    static_number = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': "Стационарен номер"
    }))
    email = forms.EmailField(required=False, widget=forms.TextInput(attrs={
        'placeholder': "Имейл"
    }))
    selected_firm_for_order = forms.ModelChoiceField(Firm.objects.none(), required=False)

    class Meta:
        model = Firm
        fields = '__all__'
        exclude = ['user', 'is_deleted']

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
        self.fields['name_of_firm'].label = "Име на Фирма / Име на физ. лице"
        self.fields['bulstat'].label = "ЕИК/ЕГН"
        self.fields['VAT_number'].label = "Номер по ЗДДС (по избор)"
        self.fields['address_by_registration'].label = "Адрес по регистрация"
        self.fields['owner_of_firm'].label = "МОЛ"
        self.fields['mobile_number'].label = "Мобилен номер"
        self.fields['static_number'].label = "Стационарен номер"
        self.fields['email'].label = "Имейл"
        self.fields['selected_firm_for_order'].label = "Избери Фирма за фактура"
        self.fields['VAT_number'].required = False

    def clean(self):
        data = self.cleaned_data

        selected_firm_for_order = data.get('selected_firm_for_order', None)
        if selected_firm_for_order is None:
            if not data.get('name_of_firm', None):
                self.add_error("name_of_firm", "Моля попълнете полето")
            if not data.get('bulstat', None):
                self.add_error('bulstat', "Моля попълнете полето")
            if not data.get('VAT_number', ''):
                data['VAT_number'] = ''
            if not data.get('address_by_registration', None):
                self.add_error("address_by_registration", "Моля попълнете полето")
            if not data.get('owner_of_firm', None):
                self.add_error("owner_of_firm", "Моля попълнете полето")


class AddressForm(forms.Form):
    # Fields
    shipping_address_line_1 = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': "Адрес за доставка"
    }))
    shipping_address_line_2 = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': "Адрес за доставка 2"
    }))
    shipping_zip_code = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': "Пощенски код"
    }))
    shipping_city = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': "Град"
    }))

    # Choise fields

    selected_shipping_address = forms.ModelChoiceField(Address.objects.none(), required=False)

    # Initial and forms query-sets
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
        #
        # if shipping_address_qs.exists():
        #     shipping_address_qs.address_line_2 = ''
        # Labels of fields
        self.fields['selected_shipping_address'].queryset = shipping_address_qs
        # labels
        self.fields['shipping_address_line_1'].label = "Адрес за доставка"
        self.fields['shipping_address_line_2'].label = "Адрес за доставка 2"
        self.fields['shipping_zip_code'].label = "Пощенски код"
        self.fields['shipping_city'].label = "Град"
        self.fields['selected_shipping_address'].label = "Избери адрес за доставка"
        self.fields['shipping_address_line_2'].required = False


    def clean(self):
        # Get data
        data = self.cleaned_data


        # Clean data from shipping address
        selected_shipping_address = data.get('selected_shipping_address', None)
        if selected_shipping_address is None:
            if not data.get('shipping_address_line_1', None):
                self.add_error("shipping_address_line_1", "Моля попълнете полето")
            if not data.get('shipping_address_line_2', ''):
                data['shipping_address_line_2'] = ''
            if not data.get('shipping_zip_code', None):
                self.add_error("shipping_zip_code", "Моля попълнете полето")
            if not data.get('shipping_city', None):
                self.add_error("shipping_city", "Моля попълнете полето")
