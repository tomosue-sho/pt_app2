from . import views
from django.urls import path

app_name = 'pt_kokushi'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('user/', views.user_view, name='user'),
    path('password_change/', views.PasswordChange.as_view(), name='password_change'), #追加
    path('password_change/done/', views.PasswordChangeDone.as_view(), name='password_change_done'), #追加
]

