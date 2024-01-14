from django.shortcuts import render, redirect
from .forms import  LoginForm
from .forms import CustomPasswordChangeForm, CustomNicknameChangeForm
from django.views import generic
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .forms import CustomUserForm #forms.pyで定義したユーザー認証画面用フォームをインポート
from datetime import date
from django.urls import reverse_lazy

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
            nickname = signup_form.cleaned_data.get('nickname')
            email = signup_form.cleaned_data.get('email')
            password = signup_form.cleaned_data.get('password')
            gender = signup_form.cleaned_data.get('gender')
            prefecture = signup_form.cleaned_data.get('prefecture')
            birth_of_date = signup_form.cleaned_data.get('birth_of_date')
            school_year = signup_form.cleaned_data.get('school_year')
            
            #CustomUser.objects.create_userはユーザーの作成に使われるヘルパー関数（すでにある関数的な感じ）
            #models.pyでCustomUser→AbstractBaseUserなどを継承したことで使えるようになる
            user = CustomUser.objects.create_user(
                nickname=nickname,
                email=email,
                password=password,
                gender=gender,
                birth_of_date=birth_of_date,
                prefecture=prefecture,
                school_year=school_year
                )
            
            user.save()
            
            #POSTされた値はハッシュ化されているためそのままでは使えない
            #なのでauthenticate()関数を使う。引数で渡したIDとPWが一致していた場合インスタンスを返す関数
            user = authenticate(request, email=email, password=password)
            
            #settings.pyで複数の認証方法を追加している場合はbackendに＝’’の内容が必要になる
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            #message.SUCCESSで処理が成功したら''内のメッセージが通知される。Django公式のフレームワーク
            messages.add_message(request, messages.SUCCESS, 'ユーザー登録が完了しました！')
            
            #登録が完了したらログイン画面に飛ぶ
            return redirect('pt_kokushi:login')
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
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, email=email, password=password)

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

class index(LoginRequiredMixin, generic.TemplateView):
    """メニュービュー"""
    template_name = 'pt_kokushi/password_change.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # 継承元のメソッドCALL
        context["form_name"] = "password_change"
        return context

class PasswordChange(LoginRequiredMixin, PasswordChangeView):
    """パスワード変更ビュー"""
    success_url = reverse_lazy('pt_kokushi:password_change_done')
    template_name = 'login_app/password_change.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # 継承元のメソッドCALL
        context["form_name"] = "password_change"
        return context

class PasswordChangeDone(LoginRequiredMixin,PasswordChangeDoneView):
    """パスワード変更完了"""
    template_name = 'login_app/password_change_done.html'
    
@login_required
def my_page_view(request):
    # パスワード変更フォーム
    password_form = CustomPasswordChangeForm(request.user)
    
    # ニックネーム変更フォーム
    nickname_form = CustomNicknameChangeForm(request.user)

    return render(request, 'login_app/my_page.html', {'password_form': password_form, 'nickname_form': nickname_form})


class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'login_app/password_change.html'
    success_url = reverse_lazy('password_change_done')  # パスワード変更完了後のリダイレクト先

class CustomNicknameChangeView(FormView):
    template_name = 'login_app/nickname_change.html'
    form_class = CustomNicknameChangeForm
    success_url = reverse_lazy('my_page')  # ニックネーム変更完了後のリダイレクト先

    def form_valid(self, form):
        # ニックネームを変更して保存する処理
        self.request.user.nickname = form.cleaned_data['nickname']
        self.request.user.save()
        return super().form_valid(form)