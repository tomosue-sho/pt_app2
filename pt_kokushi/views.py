from django.shortcuts import render, redirect
import json
from .forms import PostForm
from .forms import EventForm
from .forms import CommentForm
from .forms import CustomLoginForm, forms
from .forms import CustomUserForm
from .forms import CustomPasswordChangeForm, CustomNicknameChangeForm
from .forms import TimeTableForm
from .forms import ToDoItemForm
from django.http import JsonResponse
from django.urls import reverse_lazy
from .models import Post, Comment
from .models import Event
from .models import ToDoItem
from .models import TimeTable
from .models import Field,  Subfield, Sub2field
from .models import Question, UserAnswer, UserScore
from django.views import generic
from django.views.generic import DeleteView
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
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
from django.utils import timezone
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



#掲示板用
class PostListView(generic.ListView):
    model = Post
    template_name = 'posts/post_list.html'
    paginate_by = 12  # 1ページあたりのアイテム数
    page_kwarg = 'p'  # クエリパラメータ 'p' をページネーションのために使用
    context_object_name = 'posts'
    ordering = ['-last_commented_at']

class PostDetailView(generic.DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        obj.view_count += 1
        obj.save(update_fields=['view_count'])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        return context

class PostCreateView(generic.CreateView):
    model = Post
    form_class = PostForm
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
            if not comment.nickname:
                comment.nickname = "Anonymous"
            comment.author = request.user
            comment.save()
            
            # 最新のコメント日時を更新
            post.last_commented_at = timezone.now()
            post.save(update_fields=['last_commented_at'])

            return redirect('pt_kokushi:post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'posts/add_comment_to_post.html',  {'form': form, 'post': post})

class PostDeleteView(UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'posts/post_confirm_delete.html'
    success_url = reverse_lazy('pt_kokushi:post_list')
    
    def test_func(self):
        return self.request.user.is_staff

class CommentDeleteView(UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'posts/comment_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('pt_kokushi:post_detail', kwargs={'pk': self.object.post.pk})
    
    def test_func(self):
        return self.request.user.is_staff
    
    
#ToDoリストのためのviews.py
# views.py
def create_todo_item(request):
    if request.method == 'POST':
        form = ToDoItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pt_kokushi:todo_list')  # 正しい名前空間を使用
    else:
        form = ToDoItemForm()

    return render(request, 'todolist/create_todo_item.html', {'form': form})


# ToDoアイテムのリストを表示するためのビュー
def todo_list(request):
    items = ToDoItem.objects.all().order_by('-priority', 'deadline')  # 優先度と期限で並べ替え
    return render(request, 'todolist/todo_list.html', {'todo_items': items})


#ToDo変更view
def update_todo_item(request, pk):
    todo_item = get_object_or_404(ToDoItem, pk=pk)
    if request.method == 'POST':
        form = ToDoItemForm(request.POST, instance=todo_item)
        if form.is_valid():
            form.save()
            return redirect('pt_kokushi:todo_list')
    else:
        form = ToDoItemForm(instance=todo_item)

    return render(request, 'todolist/update_todo_item.html', {'form': form, 'todo_item': todo_item})

#ToDo削除view
def delete_todo_item(request, pk):
    todo_item = get_object_or_404(ToDoItem, pk=pk)
    if request.method == 'POST':
        todo_item.delete()
        return redirect('pt_kokushi:todo_list')
    return render(request, 'todolist/delete_todo_item.html', {'todo_item': todo_item})

#カレンダー用のviews.py
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user_email = request.user.email  # ユーザーのメールアドレスを設定
            event.save()
            return redirect('pt_kokushi:my_page')  # 適切なリダイレクト先に変更
    else:
        form = EventForm()
    return render(request, 'login_app/create_event.html', {'form': form})


def calendar_events(request):
    events = Event.objects.all()
    event_data = [{
        'id': event.id, 
        'title': event.title,
        'start': event.start_date.isoformat(),
        'end': event.end_date.isoformat(),
    } for event in events]
    return JsonResponse(event_data, safe=False)

#カレンダーイベント削除
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    return redirect('pt_kokushi:my_page')

    
#カレンダーイベント更新
def update_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('pt_kokushi:my_page')
    else:
        form = EventForm(instance=event)

    # コンテキストに event オブジェクトを追加
    context = {
        'form': form,
        'event': event  # この行を追加
    }
    return render(request, 'login_app/update_event.html', context)

#時間割表用views.py
def create_timetable(request):
    if request.method == 'POST':
        form = TimeTableForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pt_kokushi:timetable_list')
    else:
        form = TimeTableForm()
    return render(request, 'login_app/create_timetable.html', {'form': form})

def timetable_list(request):
    timetables = TimeTable.objects.all()
    days = ['月', '火', '水', '木', '金', '土', '日']  # 曜日のリスト
    time_slots = ['1限', '2限', '3限', '4限', '5限', '6限']  # 時限のリスト

    # 時間割表を作成するためのデータ構造を作成
    timetable_data = {day: {time_slot: None for time_slot in time_slots} for day in days}

    for timetable in timetables:
        period_str = f'{timetable.period}限'  # 数値を文字列に変換
        timetable_data[timetable.day][period_str] = {
            'id': timetable.id,
            'subject': timetable.subject
    }


    return render(request, 'login_app/timetable_list.html', {
        'timetable_data': timetable_data,
        'days': days,
        'time_slots': time_slots,
    })


#時間割削除と変更機能
def delete_timetable(request, timetable_id):
    timetable = get_object_or_404(TimeTable, id=timetable_id)
    timetable.delete()
    return redirect('pt_kokushi:timetable_list')

def update_timetable(request, timetable_id):
    timetable = get_object_or_404(TimeTable, id=timetable_id)
    if request.method == 'POST':
        form = TimeTableForm(request.POST, instance=timetable)
        if form.is_valid():
            form.save()
            return redirect('pt_kokushi:timetable_list')
    else:
        form = TimeTableForm(instance=timetable)
    return render(request, 'login_app/edit_timetable.html', {'form': form, 'timetable': timetable})

#2択問題のためのviews.py
def start_quiz(request):
    # 分野を選択するページを表示
    fields = ['解剖学', 'ROM','MMT']
    return render(request, '2quiz/start_quiz.html', {'fields': fields})

def quiz(request, field=None, subfield_id=None, sub2field_id=None):
    # クエリパラメータに応じて問題をフィルタリング
    if sub2field_id:
        sub2field = get_object_or_404(Sub2field, id=sub2field_id)
        questions = Question.objects.filter(sub2field=sub2field)
    elif subfield_id:
        subfield = get_object_or_404(Subfield, id=subfield_id)
        questions = Question.objects.filter(subfield=subfield)
    else:
        questions = Question.objects.filter(field=field)

    # ランダムな問題を選択
    question = questions.order_by('?').first()

    if request.method == 'POST':
        selected_answer = request.POST.get('selected_answer')
        # ユーザーの回答を保存
        UserAnswer.objects.create(user=request.user, question=question, selected_answer=selected_answer)
        # 成績を更新（省略）

    return render(request, '2quiz/quiz.html', {'question': question})

def quiz_page(request):
    questions = Question.objects.all()[:5]  # 最初の5問を取得
    questions_json = json.dumps(list(questions.values('id', 'question_text', 'correct_answer')))
    return render(request, 'quiz_page.html', {'questions_json': questions_json})

def quiz_results(request):
    # 成績情報を取得
    user_score = UserScore.objects.get(user=request.user)
    return render(request, '2quiz/results.html', {'user_score': user_score})

#分野選択のためのviews
def select_field(request):
    fields = Field.objects.all()
    return render(request, '2quiz/select_field.html', {'fields': fields})

@csrf_exempt
@require_POST
def submit_answer(request):
    # JSONデータを解析
    data = json.loads(request.body)
    selected_answer = data.get('selected_answer')
    question_id = data.get('question_id')

    # ログインしているユーザーを取得
    user = request.user

    # 選択した回答に対応する問題を取得
    question = Question.objects.get(pk=question_id)

    # ユーザーの回答を保存
    user_answer = UserAnswer(user=user, question=question, selected_answer=selected_answer)
    user_answer.save()

    # ユーザーのスコアを更新
    user_score, created = UserScore.objects.get_or_create(user=user)
    is_correct = selected_answer == question.correct_answer
    if is_correct:
        user_score.total_correct_answers += 1
        user_score.total_score += 1
    user_score.total_questions_attempted += 1
    user_score.save()

    # JSONレスポンスを返す
    return JsonResponse({'status': 'success', 'is_correct': is_correct})

def get_question(request, question_id):
    question = Question.objects.get(pk=question_id)
    return JsonResponse({
        'question_text': question.question_text,
        'correct_answer': question.correct_answer  # 実際のアプリケーションでは正解をクライアントに送信しない方が良い
    })

def select_subfield(request, field_id):
    # 選択されたフィールドを取得
    field = get_object_or_404(Field, id=field_id)
    # 選択されたフィールドに関連する詳細な分野を取得
    subfields = Subfield.objects.filter(field=field)

    return render(request, '2quiz/select_subfield.html', {'field': field, 'subfields': subfields})

def select_sub2field(request, subfield_id):
    subfield = get_object_or_404(Subfield, id=subfield_id)
    sub2fields = Sub2field.objects.filter(subfield=subfield)
    field = subfield.field
    
    return render(request, '2quiz/select_sub2field.html', {'field': field, 'subfield': subfield, 'sub2fields': sub2fields})

