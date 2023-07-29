from django import forms
from allauth.account.forms import SignupForm, LoginForm
from .models import Firm, CustomUserModel


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'placeholder': "Вашето Име"
    }))
    email = forms.EmailField(widget=forms.TextInput(attrs={
        'placeholder': "Вашият Имейл"
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Вашето съобщение'
    }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = "Име"
        self.fields['email'].label = "Имейл"
        self.fields['message'].label = "Съобщение"

class CustomSignupForm(SignupForm):
    email = forms.EmailField(max_length=254, label='Имейл', widget=forms.TextInput(attrs={
        'placeholder': "Имейл"}))
    username = forms.CharField(max_length=30, label='Потребителско Име', widget=forms.TextInput(attrs={
        'placeholder': "Потребителско Име"}))
    first_name = forms.CharField(max_length=30, label='Първо Име', widget=forms.TextInput(attrs={
        'placeholder': "Първо Име"
    }))
    last_name = forms.CharField(max_length=30, label='Второ Име', widget=forms.TextInput(attrs={
        'placeholder': "Второ Име"
    }))
    phone = forms.CharField(max_length=10, label='Телефон', widget=forms.TextInput(attrs={
        'placeholder': "Телефон"}))

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.save()
        return user


class FirmForm(forms.ModelForm):
    class Meta:
        model = Firm
        fields = '__all__'
        exclude = ['user']
        labels = {
            'name_of_firm': 'Име на Фирма',
            'bulstat': 'ЕИК',
            'VAT_number': 'Номер по ЗДДС (по избор)',
            'address_by_registration': 'Адрес на фирма по регистрация',
            'owner_of_firm': 'МОЛ',
        }
        widgets = {
            'name_of_firm': forms.TextInput(
                attrs={
                    'placeholder': 'Име на Фирма',
                }
            ),
            'bulstat': forms.TextInput(
                attrs={
                    'placeholder': 'ЕИК',
                }
            ),
            'VAT_number': forms.TextInput(
                attrs={
                    'placeholder': 'Номер по ЗДДС (по избор)',
                }
            ),
            'address_by_registration': forms.TextInput(
                attrs={
                    'placeholder': 'Адрес на фирма по регистрация',
                }
            ),
            'owner_of_firm': forms.TextInput(
                attrs={
                    'placeholder': 'МОЛ',
                }
            )
        }


class EditUserForm(forms.ModelForm):
    class Meta:
        model = CustomUserModel
        fields = ['first_name', 'last_name', 'email', 'phone_number']
        labels = {
            'first_name': 'Име',
            'last_name': 'Фамилия',
            'email': 'Имейл',
            'phone_number': 'Телефон',
        }
        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'placeholder': 'Име',
                }
            ),
            'last_name': forms.TextInput(
                attrs={
                    'placeholder': 'Фамилия',
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'placeholder': 'Имейл',
                }
            ),
            'phone_number': forms.TextInput(
                attrs={
                    'placeholder': 'Телефон',
                }
            ),

        }
