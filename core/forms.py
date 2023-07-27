from django import forms
from allauth.account.forms import SignupForm, LoginForm


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
    name_of_firm = forms.CharField(max_length=100, label="Име на фирма (по избор)", required=False, widget=forms.TextInput(attrs={
        'placeholder': "Име на фирма (по избор)"
    }))
    phone = forms.CharField(max_length=10, label='Телефон', widget=forms.TextInput(attrs={
        'placeholder': "Телефон"}))

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.name_of_firm = self.cleaned_data['name_of_firm']
        user.phone = self.cleaned_data['phone']
        user.save()
        return user

#
# class CustomLoginForm(LoginForm):
#     email = forms.EmailField(max_length=254, label='Имейл', widget=forms.TextInput(attrs={
#         'placeholder': "Имейл"}))
#     password = forms.CharField(max_length=30, label='Парола', widget=forms.TextInput(attrs={
#         'placeholder': "Парола"}))
#
#
#     def login(self, *args, **kwargs):
#         user = super(CustomLoginForm, self).login(request)
#         user.email = self.cleaned_data['email']
#         user.password = self.cleaned_data['password']
#
#

