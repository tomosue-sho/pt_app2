from . import views
from django.urls import path

app_name = 'pt_kokushi'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('user/', views.user_view, name='user'),
]
