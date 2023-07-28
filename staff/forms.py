from django import forms

from cart.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'title',
            'image',
            'description',
            'price',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = 'Име'
        self.fields['image'].label = 'Снимка'
        self.fields['description'].label = 'Описание'
        self.fields['price'].label = 'Цена'

