from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse_lazy
from pt_kokushi.models.calender_models import Event
from pt_kokushi.forms_org import CustomLoginForm, forms
from pt_kokushi.forms_org import CustomUserForm, TestYearForm
from pt_kokushi.forms_org import CustomPasswordChangeForm, CustomNicknameChangeForm
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
from django.urls import reverse
from datetime import date, datetime ,timedelta
from pt_kokushi.helpers import calculate_login_streak
from pt_kokushi.models.LoginHistory_models import LoginHistory
from pt_kokushi.models.kokushi_models import Exam
from pt_kokushi.helpers import calculate_login_streak

#これを使わないとDjangoのUserを使ってしまう
CustomUser = get_user_model()

class TopView(TemplateView):
    template_name = "top.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Examモデルから全年度を取得
        context['years'] = Exam.objects.all().order_by('-year').values_list('year', flat=True)
    
        if self.request.user.is_authenticated:
            # ログインユーザーの連続ログイン日数を計算
            login_streak = calculate_login_streak(self.request.user)
            # コンテキストに連続ログイン日数を追加
            context['login_streak'] = login_streak
    
        return context

    def post(self, request, *args, **kwargs):
        exam_year = request.POST.get('exam_year')
        if exam_year:
            request.session['exam_year'] = int(exam_year)
            return redirect(reverse('pt_kokushi:timer'))
        else:
            # 何らかのエラーメッセージをセットするか、適切にハンドル
            return super().get(request, *args, **kwargs)

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
            password = signup_form.cleaned_data.get('password1')
            gender = signup_form.cleaned_data.get('gender')
            prefecture = signup_form.cleaned_data.get('prefecture')
            birth_of_date = signup_form.cleaned_data.get('birth_of_date')
            school_year = signup_form.cleaned_data.get('school_year')
            test_year = signup_form.cleaned_data.get('test_year')
            
            #CustomUser.objects.create_userはユーザーの作成に使われるヘルパー関数（すでにある関数的な感じ）
            #models.pyでCustomUser→AbstractBaseUserなどを継承したことで使えるようになる
            user = CustomUser.objects.create_user(
                nickname=nickname,
                email=email,
                password=password,
                gender=gender,
                birth_of_date=birth_of_date,
                prefecture=prefecture,
                school_year=school_year,
                test_year=test_year,
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
        form = CustomLoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            # authenticateを使用してユーザーを取得
            user = authenticate(request, email=form.cleaned_data['email'], password=form.cleaned_data['password'])
      
            if user:
                login(request, user)
                messages.success(request, 'ログイン成功しました')
                return redirect('pt_kokushi:top')  # ログイン後のリダイレクト先を指定
            else:
                messages.error(request, 'メールアドレスかパスワードが間違っています。')
        else:
            messages.error(request, 'フォームが有効ではありません')
            # フォームが無効な場合にエラーメッセージをフォームに紐づける
            return render(request, 'login_app/login.html', {'form': form})
    else:
        form = CustomLoginForm()
    return render(request, 'login_app/login.html', {'form': form})

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

#マイページでのパスワード変更用のviews  
@login_required
def my_page_view(request):
    user = request.user
    test_dates = {
        "2024": "2024-02-18 09:50:00",
        "2025": "2025-02-16 09:50:00",
        "2026": "2026-02-15 09:50:00",
        "2027": "2027-02-21 09:50:00",
        "2028": "2028-02-20 09:50:00",
    }

    remaining_days = None
    if isinstance(user, CustomUser):
        remaining_time = user.get_remaining_time(test_dates)
        if remaining_time and remaining_time.days >= 0:
            remaining_days = remaining_time.days
    
    events = Event.objects.all()  # すべてのイベントを取得
    context = {
        'events': events,
        'remaining_days': remaining_days  
    }

    return render(request, 'login_app/my_page.html', context)
    

def change_password_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'パスワードが変更されました。')
            return redirect('pt_kokushi:my_page')
        else:
            messages.error(request, 'パスワード変更に失敗しました。')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'login_app/change_password.html', {'form': form})

@login_required
def change_nickname_view(request):
    if request.method == 'POST':
        form = CustomNicknameChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'ニックネームが変更されました。')
            return redirect('pt_kokushi:my_page')
        else:
            messages.error(request, 'ニックネームの変更に失敗しました。')
    else:
        form = CustomNicknameChangeForm(instance=request.user)
    return render(request, 'login_app/change_nickname.html', {'form': form})

class CustomPasswordChangeView(FormView):
    template_name = 'login_app/password_change.html'  # カスタムテンプレートを指定
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('pt_kokushi:password_change_done')  # パスワード変更完了後のリダイレクト先

    def form_valid(self, form):
        # ユーザーのパスワードを変更
        form.save()
        messages.success(self.request, 'パスワードを変更しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'パスワードの変更に失敗しました。')
        return super().form_invalid(form)

    def get_form_kwargs(self):
        # 現在のユーザー情報をフォームに渡す
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
class CustomNicknameChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['nickname']  # ニックネームを変更するフィールド


    def form_valid(self, form):
        # ニックネームを変更して保存する処理
        self.request.user.nickname = form.cleaned_data['nickname']
        self.request.user.save()
        return super().form_valid(form)
    

def get_remaining_time(request):
    user = request.user
    test_dates = {
        "2024": "2024-02-18 09:50:00",
        "2025": "2025-02-16 09:50:00",
        "2026": "2026-02-15 09:50:00",
        "2027": "2027-02-21 09:50:00",
        "2028": "2028-02-20 09:50:00",
    }

    if hasattr(user, 'test_year') and user.test_year in test_dates:
        test_date = datetime.strptime(test_dates[user.test_year], "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        remaining_time = test_date - now
        if remaining_time.total_seconds() > 0:
            return JsonResponse({
                'remaining_seconds': remaining_time.total_seconds()
            })
    
    return JsonResponse({'remaining_seconds': None})

def update_test_year(request):
    if request.method == 'POST':
        form = TestYearForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('pt_kokushi:my_page')  # 保存後にリダイレクトするページ
    else:
        form = TestYearForm(instance=request.user)
    return render(request, 'login_app/update_test_year.html', {'form': form})

#年度の表示を5個にするよう（メディアクエリ）
def load_more_years(request):
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 5))
    years = Exam.objects.all().order_by('-year')[offset:offset + limit]
    
    years_data = [{'year': year.year, 'id': year.id} for year in years]
    new_offset = offset + limit
    
    return JsonResponse({'years': years_data, 'new_offset': new_offset})