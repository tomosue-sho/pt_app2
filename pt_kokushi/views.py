from django.shortcuts import render, redirect
from .forms import CustomLoginForm
from .forms import CustomUserForm
from .forms import CustomPasswordChangeForm, CustomNicknameChangeForm
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login ,logout
from django.contrib.auth import authenticate, login as auth_login, get_user_model
from django.contrib.auth import views as auth_views
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
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
            
       # ユーザーが正しく作成されたか確認
            if user is not None:
                auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.add_message(request, messages.SUCCESS, 'ユーザー登録が完了しました！')
                return redirect('pt_kokushi:login')
            else:
                messages.add_message(request, messages.ERROR, 'ユーザーの作成に失敗しました。')
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


# ログイン画面
def login_view(request):
    if request.method == 'POST':
        next = request.POST.get('next')
        form = CustomLoginForm(request, data=request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                # 既存のセッションデータをクリア
                logout(request)
                return redirect(to='top')
            else:
                # 認証に失敗した場合の処理
                messages.error(request, 'ユーザー認証に失敗しました。')
    else:
        form = CustomLoginForm()

    param = {
        'form': form,
    }

    return render(request, 'login_app/login.html', param)


#ユーザーの登録内容(user.htmlだが今は使っていないエラーが出たら嫌なので消してない)
@login_required
def user_view(request):
    user = request.user

    params = {
        'email': user.email
    }

    return render(request, 'login_app/user.html', params)


#ここからパスワード変更のためのコード
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
    
 # --- ここから追加
class PasswordReset(PasswordResetView):
    """パスワード変更用URLの送付ページ"""
    subject_template_name = 'login_app/mail_template/reset/subject.txt'
    email_template_name = 'login_app/mail_template/reset/message.txt'
    template_name = 'login_app/mail_template/password_reset_form.html'
    success_url = reverse_lazy('pt_kokushi:password_reset_done')


class PasswordResetDone(PasswordResetDoneView):
    """パスワード変更用URLを送りましたページ"""
    template_name = 'login_app/mail_template/password_reset_done.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    """新パスワード入力ページ"""
    success_url = reverse_lazy('pt_kokushi:password_reset_complete')
    template_name = 'login_app/mail_template/password_reset_confirm.html'


class PasswordResetComplete(PasswordResetCompleteView):
    """新パスワード設定しましたページ"""
    template_name = 'login_app/mail_template/password_reset_complete.html'

# --- ここまで

    
@login_required
def my_page_view(request):
    # パスワード変更フォーム
    password_form = CustomPasswordChangeForm(request.user)
    
    # ニックネーム変更フォーム
    nickname_form = CustomNicknameChangeForm(request.user)

    return render(request, 'login_app/my_page.html', {'password_form': password_form, 'nickname_form': nickname_form})


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'login_app/password_change.html'  # カスタムテンプレートを指定
    success_url = reverse_lazy('pt_kokushi:password_change_done')  # パスワード変更完了後のリダイレクト先

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'パスワードを変更しました。')  # 成功メッセージの表示
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, 'パスワードの変更に失敗しました。')  # エラーメッセージの表示
        return response

    def get(self, request, *args, **kwargs):
        # ここでGETリクエストが来た場合の処理を追加できます
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # ここでPOSTリクエストが来た場合の処理を追加できます
        return super().post(request, *args, **kwargs)

    # その他、必要なメソッドを追加できる

class CustomNicknameChangeView(FormView):
    template_name = 'login_app/nickname_change.html'
    form_class = CustomNicknameChangeForm
    success_url = reverse_lazy('top')  # ニックネーム変更完了後のリダイレクト先

    def form_valid(self, form):
        # ニックネームを変更して保存する処理
        self.request.user.nickname = form.cleaned_data['nickname']
        self.request.user.save()
        return super().form_valid(form)