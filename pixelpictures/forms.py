from django.contrib.auth.forms import UserCreationForm 
from django import forms

from .models import User

class RegisterUserForm(UserCreationForm):

    class Meta: 
        model = User 
        fields = ['username', 'email', 'password1', 'password2']
    

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Email already exists.',
                code='email_exists'
                )
        return email
