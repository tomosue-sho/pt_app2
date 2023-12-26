from django.shortcuts import render, redirect
from .forms import SignupForm, LoginForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

class TopView(TemplateView):
    template_name = "top.html"

#ユーザーアカウント登録
def signup_view(request):
    if request.method == 'POST':

        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(to='top')

    else:
        form = SignupForm()
    
    param = {
        'form': form
    }

    return render(request, 'login_app/signup.html', param)

#ログイン画面
def login_view(request):
    if request.method == 'POST':
        next = request.POST.get('next')
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            if user:
                login(request, user)
                return redirect(to='top')

    else:
        form = LoginForm()

    param = {
        'form': form,
    }

    return render(request, 'login_app/login.html', param)

#ユーザーの登録内容
@login_required
def user_view(request):
    user = request.user

    params = {
        'email': user.email
    }

    return render(request, 'login_app/user.html', params)
