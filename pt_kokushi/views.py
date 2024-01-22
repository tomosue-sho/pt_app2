from django.shortcuts import render, redirect
from .forms import CommentForm
from .forms import CustomLoginForm, forms
from .forms import CustomUserForm
from .forms import CustomPasswordChangeForm, CustomNicknameChangeForm
from django.http import JsonResponse
from django.urls import reverse_lazy
from .models import Post, Comment
from django.views import generic
from django.views.generic import DeleteView
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login ,logout
from django.contrib.auth import authenticate, login as auth_login, get_user_model
from django.contrib.auth import views as auth_views
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from datetime import date, datetime
from django.shortcuts import render, get_object_or_404, redirect


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
    }

    remaining_days = None
    if isinstance(user, CustomUser):
        remaining_time = user.get_remaining_time(test_dates)
        if remaining_time and remaining_time.days >= 0:
            remaining_days = remaining_time.days

    context = {
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



#掲示板用
class PostListView(generic.ListView):
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'

class PostDetailView(generic.DetailView):
    model = Post
    template_name = 'posts/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        return context

class PostCreateView(generic.CreateView):
    model = Post
    fields = ['title', 'content', 'nickname']
    template_name = 'posts/post_create.html'

    def form_valid(self, form):
        return super().form_valid(form)
    
    success_url = reverse_lazy('pt_kokushi:post_list')

def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            # フォームで入力された nickname が空白の場合、デフォルト値を代入
            if not comment.nickname:
                comment.nickname = "Anonymous"
            comment.author = request.user
            comment.save()
            return redirect('pt_kokushi:post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'posts/add_comment_to_post.html', {'form': form})

class PostDeleteView(UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('pt_kokushi:post_list')
    
    def test_func(self):
        return self.request.user.is_staff

class CommentDeleteView(UserPassesTestMixin, DeleteView):
    model = Comment

    def get_success_url(self):
        return reverse_lazy('pt_kokushi:post_detail', kwargs={'pk': self.object.post.pk})
    
    def test_func(self):
        return self.request.user.is_staff