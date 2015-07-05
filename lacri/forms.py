from django import forms
from django.core.validators import RegexValidator

username_validator = RegexValidator(r'^[\w]+$', 'Alphanumeric characters only')
domain_validator = RegexValidator(r'(\*\.)?[\w\-\.]*[\w\-]', 'Valid domain name only')

class CreateUserForm(forms.Form):
    username = forms.CharField(label='Username', 
            max_length=100, 
            validators=[username_validator], 
            widget=forms.TextInput(attrs={'placeholder': 'Username'}),
    )
    password = forms.CharField(label='Password', 
            max_length=100, 
            widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )

class CreateRootForm(forms.Form):
    common_name = forms.CharField(label='Root Name', 
            max_length=100, 
            widget=forms.TextInput(attrs={'placeholder': 'e.g. My CA', 'style': 'visibility: hidden;'}),
    )

class CreateDomainForm(forms.Form):
    common_name = forms.CharField(label='Domain Name', 
            max_length=100, 
            widget=forms.TextInput(attrs={'placeholder': 'something.example.com', 'style': 'visibility: hidden;'}),
    )
