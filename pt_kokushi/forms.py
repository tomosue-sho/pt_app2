from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class SignupForm(UserCreationForm):
    email = forms.EmailField(
        label='メールアドレス',
        help_text = ('必須です')
        )
    
    birth_of_date = forms.DateField(
        label = '生年月日',
        help_text = '必須です。YYYY-MM-DD 形式(例:2020-10-06)で入力して下さい。'
    )
    
    school_year = forms.IntegerField(
        label = '学年',
        help_text = '卒業生等の学校に無所属の場合は「０」でお願いします'
    )
    
    class Meta:
        model = CustomUser
        fields = ['email']

class LoginForm(AuthenticationForm):
    pass