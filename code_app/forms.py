from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *


class SignupForm(UserCreationForm):
	username = forms.CharField(label='Username', max_length=100)
	first_name = forms.CharField(label='First Name', max_length=32, required=False)
	last_name = forms.CharField(label='Last Name', max_length=32, required=False)                
	password1 = forms.CharField(widget=forms.PasswordInput, label='Password', max_length=32)
	password2 = forms.CharField(widget=forms.PasswordInput, label='Re:Password', max_length=32)

	class Meta:
		model = User
		fields = ('username','password1','password2','first_name','last_name')
