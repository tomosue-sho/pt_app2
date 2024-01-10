from django.shortcuts import render, redirect
from .forms import  LoginForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login as auth_login, get_user_model
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .forms import CustomUserForm #forms.pyで定義したユーザー認証画面用フォームをインポート
from datetime import date

#これを使わないとDjangoのUserを使ってしまう
CustomUser = get_user_model()


class TopView(TemplateView):
    template_name = "top.html"

#ユーザーアカウント登録
def signup_view(request):
    
    #POSTは他人に見られたくない情報を送るときに使用する
    if request.method == 'POST':
        
        #request.POSTのデータを受け取ったformのオブジェクトを生成する
        signup_form = CustomUserForm(request.POST)
        
        #form.is_valid()でバリデーション（入力値の正しさのチェック）を行う
        #要はフォームに記載された内容が問題なければ処理を実行するということ
        if signup_form.is_valid():
            
            #cleaned_dataにバリデーション後に正しかったデータが入る
            #POSTの値をcleaned_dataして辞書型のデータに整形し、get()にキーを入力して取り出す
            #signup_form
            username = signup_form.cleaned_data.get('username')
            email = signup_form.cleaned_data.get('email')
            password = signup_form.cleaned_data.get('password')
            password2 = signup_form.cleaned_data.get('password2')
            gender = signup_form.cleaned_data.get('gender')
            birth_year = signup_form.cleaned_data.get('birth_year')
            birth_month = signup_form.cleaned_data.get('birth_month')
            birth_day = signup_form.cleaned_data.get('birth_day')
            prefecture = signup_form.cleaned_data.get('prefecture')
            birth_date = signup_form.cleaned_data.get('birth_date')
            
            #CustomUser.objects.create_userはユーザーの作成に使われるヘルパー関数（すでにある関数的な感じ）
            #models.pyでCustomUser→AbstractBaseUserなどを継承したことで使えるようになる
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                password2=password2,
                gender=gender,
                birth_year=birth_year,
                birth_month=birth_month,
                birth_day=birth_day,
                prefecture=prefecture
                )
            
            user.save()
            
            #POSTされた値はハッシュ化されているためそのままでは使えない
            #なのでauthenticate()関数を使う。引数で渡したIDとPWが一致していた場合インスタンスを返す関数
            user = authenticate(request, username=username, password=password)
            
            #settings.pyで複数の認証方法を追加している場合はbackendに＝’’の内容が必要になる
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            #message.SUCCESSで処理が成功したら''内のメッセージが通知される。Django公式のフレームワーク
            messages.add_message(request, messages.SUCCESS, 'ユーザー登録が完了しました！')
            
            #登録が完了したらログイン画面に飛ぶ
            return redirect('login_app/login.html')
    else:
        signup_form = CustomUserForm()
        

    
    #contextにサインアップフォームとプロフィールフォームを入れる（後でテンプレートに渡すため）
    #contextにforms.pyの内容を入れてrender関数で出力する
    context = {
        'signup_form': signup_form,
    }
    
    #login_app/signup.htmlにcontextの内容は渡す
    #signupの{{form}}を入力したところに入力フォームが表示される
    return render(request, 'login_app/signup.html', context)


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
