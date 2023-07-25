from django import forms


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
