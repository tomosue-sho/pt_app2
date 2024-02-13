from django.shortcuts import redirect, render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse
from django.utils.timezone import now
from django.http import HttpResponseRedirect
from django.db.models import Q
from pt_kokushi.models.kokushi_models import Exam,QuizQuestion,QuizQuestion, Choice, QuizUserAnswer
from django.db.models import Count, Sum, Avg,Q,Case,When,Value,OuterRef, Subquery
from django.db.models import F, FloatField, ExpressionWrapper,IntegerField,fields
from django.db.models.functions import Cast

# 試験回選択用
def exam_selection_view(request):
    years = list(reversed(range(49, 60)))  # 49から59までのリストを作成
    if request.method == 'POST':
        exam_year = request.POST.get('exam_year')
        request.session['exam_year'] = int(exam_year)
        return HttpResponseRedirect(reverse('pt_kokushi:timer'))
    else:
        return render(request, 'top.html', {'years': years})

#試験年度のforループ用
def your_view_function(request):
    years = list(range(49, 59))  # Python 3ではrangeをlistに変換する必要がある
    return render(request, 'top.html', {'years': years})

#国試タイマー
def time_setting_view(request):
    if request.method == 'POST':
        # 時間設定を受け取る
        time_limit = request.POST.get('time_limit')
        custom_time_limit = request.POST.get('custom_time_limit')
        
        exam_year = request.POST.get('exam_year')

        if time_limit:
            time_limit_seconds = int(time_limit) * 60  # 分を秒に変換
            request.session['time_limit'] = time_limit_seconds
        elif custom_time_limit:
            try:
                time_limit_seconds = int(custom_time_limit) * 60  # 分を秒に変換
                request.session['time_limit'] = time_limit_seconds
            except ValueError:
                # 不正な入力の場合、エラーメッセージを設定
                return render(request, 'kokushi/timer.html', {'error': '有効な時間を入力してください。'})
        else:
            # 時間設定がない場合のエラーハンドリング
            return render(request, 'kokushi/timer.html', {'error': '時間を設定してください。'})
        
        if exam_year:
            request.session['exam_year'] = int(exam_year)

        # ここで開始時間を記録
        # ※ この例では、すべての問題に対してstart_timeを設定していますが、
        #    実際には特定の問題や試験セッションに関連付ける必要があります。
        #    また、現在のユーザーと試験年度を基にQuizUserAnswerインスタンスを特定または作成する必要があります。
        questions = QuizQuestion.objects.filter(exam__year=exam_year)
        for question in questions:
            QuizUserAnswer.objects.update_or_create(
                user=request.user,
                question=question,
                defaults={'start_time': now()}
            )

        # 正常に時間設定が完了した場合、quiz_questions_viewにリダイレクト
        return HttpResponseRedirect(reverse('pt_kokushi:quiz_questions'))
    else:
        # GETリクエストの場合は時間設定ページを表示
        return render(request, 'kokushi/timer.html')

def quiz_questions_view(request, question_id=None):
    # セッションから試験年度を取得
    exam_year = request.session.get('exam_year', None)
    time_limit = request.session.get('time_limit')  # 時間設定をセッションから取得
    
    if not exam_year:
        return redirect('pt_kokushi:top')
    
    exam = get_object_or_404(Exam, year=exam_year)
    question = get_object_or_404(QuizQuestion, pk=question_id) if question_id else None
    questions = QuizQuestion.objects.filter(exam=exam)
    
    if not questions.exists():
        return render(request, 'kokushi/no_questions.html', {'exam': exam})
    
    # question_idが指定されていればその質問を、そうでなければ最初の質問を取得
    if question_id:
        question = get_object_or_404(QuizQuestion, exam=exam, id=question_id)
    else:
        question = QuizQuestion.objects.filter(exam=exam).first()
    
    context = {
        'exam': exam,
        'question': question,
        'time_limit': time_limit,  # コンテキストに時間設定を追加
    }
    return render(request, 'kokushi/quiz_questions.html', context)


#正解判定ーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
# 問題に取り組み始めるビュー
def start_quiz_question(request, question_id):
    # 問題の取得
    question = get_object_or_404(QuizQuestion, pk=question_id)
    # QuizUserAnswer インスタンスを作成または更新
    quiz_user_answer, created = QuizUserAnswer.objects.update_or_create(
        user=request.user,
        question=question,
        defaults={'start_time': now()}  # start_time を現在時刻に設定
    )
    # 問題ページにリダイレクト
    return redirect('quiz_question_view', question_id=question_id)


def submit_quiz_answers(request, question_id):
    if request.method == 'POST':
        user = request.user
        current_question = get_object_or_404(QuizQuestion, pk=question_id)
        selected_choice_ids = request.POST.getlist(f'question_{question_id}')

        # QuizUserAnswer インスタンスを取得または作成し、終了時刻を更新
        quiz_user_answer, created = QuizUserAnswer.objects.get_or_create(
            user=user,
            question=current_question,
            defaults={'start_time': now()}  # ここは必要に応じて調整してください
        )
        quiz_user_answer.end_time = now()  # 回答終了時刻を更新
        quiz_user_answer.save()

        # 選択した選択肢をクリアし、新たに選択された選択肢を追加
        quiz_user_answer.selected_choices.clear()
        for choice_id in selected_choice_ids:
            selected_choice = get_object_or_404(Choice, pk=choice_id)
            quiz_user_answer.selected_choices.add(selected_choice)
        # 正解の選択肢を取得
        correct_choices = current_question.choices.filter(is_correct=True)
        correct_choice_ids = set(correct_choices.values_list('id', flat=True))
        selected_correctly = correct_choice_ids == set(map(int, selected_choice_ids))

        if selected_correctly:
            # スコアを更新するロジックをここに追加
            pass

        # 次の問題へのリダイレクトまたは結果ページへのリダイレクトを行う
        next_question = QuizQuestion.objects.filter(id__gt=question_id).order_by('id').first()
        if next_question:
            return redirect('pt_kokushi:quiz_questions', question_id=next_question.id)
        else:
            return redirect('pt_kokushi:kokushi_results')

@login_required
def kokushi_results_view(request):
    user = request.user
    total_questions = QuizQuestion.objects.count()
    exam_year = request.session.get('exam_year', None)  # セッションから試験年度を取得
    if exam_year is not None:
        exam = Exam.objects.get(year=exam_year)  # 試験年度に基づいてExamオブジェクトを取得
    else:
        exam = None 
    
    #回答時間の計算
    user_answers = QuizUserAnswer.objects.filter(user=user).annotate(
        answer_duration=ExpressionWrapper(F('end_time') - F('start_time'), output_field=fields.DurationField())
    )

     # 解答時間をフォーマットし、開始時刻と終了時刻をリストに追加
    formatted_answers = []
    for answer in user_answers:
        # answer_durationを持っていることを前提としていますが、実際には別の計算方法を使うかもしれません
        if answer.end_time:  # end_timeが設定されている場合のみ計算
            duration = answer.end_time - answer.start_time
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            answer_time_str = f"{int(hours)}時間{int(minutes)}分{int(seconds)}秒"
        else:
            answer_time_str = "未完了"

        formatted_answers.append({
            'question_number': answer.question.question_number,
            'answer_time': answer_time_str,
            'start_time': answer.start_time.strftime("%Y-%m-%d %H:%M:%S") if answer.start_time else '未開始',
            'end_time': answer.end_time.strftime("%Y-%m-%d %H:%M:%S") if answer.end_time else '未完了'
        })

    # 個人の分野ごとの正答数と質問数を計算
    field_accuracy = QuizUserAnswer.objects.filter(user=user).annotate(
        is_correct=Case(
            When(selected_choices__is_correct=True, then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        )
    ).values('question__field__name').annotate(
        total=Count('question'),
        correct_sum=Sum('is_correct')
    ).annotate(
        accuracy=ExpressionWrapper(F('correct_sum') * 100.0 / F('total'), output_field=FloatField())
    )
    # 全ユーザーの正答数と正答率
    all_user_answers = QuizUserAnswer.objects.annotate(
        is_correct=Case(
            When(selected_choices__is_correct=True, then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        )
    )
    all_user_correct_count = all_user_answers.aggregate(correct_sum=Sum('is_correct'))['correct_sum'] or 0
    all_users_count = QuizUserAnswer.objects.values('user').distinct().count()
    all_user_accuracy = (all_user_correct_count / (total_questions * all_users_count)) * 100 if all_users_count > 0 else 0
    
# 分野ごとの正答率（全体）の計算を修正
    field_accuracy_all = all_user_answers.values('question__field__name').annotate(
        total=Count('question'),
        correct_sum=Sum('is_correct')
    ).annotate(
        accuracy=ExpressionWrapper(F('correct_sum') * 100.0 / F('total'), output_field=FloatField())
    )
    context = {
        'exam': exam,
        'formatted_answers': formatted_answers,
        'all_user_accuracy': all_user_accuracy,
        'field_accuracy': field_accuracy,
        'field_accuracy_all': field_accuracy_all,
        
    }
    return render(request, 'kokushi/kokushi_results.html', context)

#セッションクリアのための関数（時直し時とかに使う）ーーーーーーーーーーーー
#最初からやり直す関数
def restart_kokushi_quiz_view(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')

    # ユーザーのクイズ回答と進行状態をリセット
    QuizUserAnswer.objects.filter(user=user).delete()
    # 必要に応じてセッション情報のリセットも行う
    # request.session.pop('key', None)

    return redirect('pt_kokushi:quiz_questions_with_id', question_id=1)

#前回の続きから用
def continue_quiz_view(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')

    # ユーザーの最後の進行状態を取得
    last_answer = QuizUserAnswer.objects.filter(user=user).order_by('-id').first()
    if last_answer:
        next_question_id = last_answer.question.id + 1
        return redirect('pt_kokushi:quiz_questions_view', question_id=next_question_id)
    else:
        # 進行状態がなければ、最初の問題から開始
        return redirect('pt_kokushi:quiz_questions_view', question_id=1)
    
def exit_quiz(request):
    # セッションから最後に解答した質問のIDを取得
    last_question_id = request.session.get('last_question_id', None)
    
    if last_question_id is not None:
        # 最後に解答した質問のIDがある場合、適切な処理を行う
        # 例: ユーザーをクイズの結果ページやトップページにリダイレクトする
        return redirect('pt_kokushi:top')
    else:
        # 最後に解答した質問のIDがない場合の処理
        # 例: エラーメッセージを表示する、またはクイズのトップページにリダイレクトする
        return redirect('pt_kokushi:timer')
