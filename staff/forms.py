from django import forms

from cart.models import Product, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'title',
            'image',
            'description',
            'price',
            'active',
            'primary_category',
            'secondary_categories',
            'stock',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = 'Име'
        self.fields['image'].label = 'Снимка'
        self.fields['description'].label = 'Описание'
        self.fields['price'].label = 'Цена'
        self.fields['active'].label = 'Активен ли е продукта?'
        self.fields['primary_category'].label = 'Основна категория'
        self.fields['secondary_categories'].label = 'Вторични категории'
        self.fields['stock'].label = 'Налично количество'


class CreateCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = "Име на категория"
