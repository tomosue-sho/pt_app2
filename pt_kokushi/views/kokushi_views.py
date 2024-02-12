from django.shortcuts import redirect, render
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db.models import Q
from pt_kokushi.models.kokushi_models import Exam,QuizQuestion,QuizQuestion, Choice, QuizUserAnswer
from django.db.models import Count, Sum, Avg


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

# 国試タイマー用
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
def submit_quiz_answers(request, question_id):
    if request.method == 'POST':
        user = request.user
        current_question = get_object_or_404(QuizQuestion, pk=question_id)
        selected_choice_ids = request.POST.getlist(f'question_{question_id}')

        # QuizUserAnswer インスタンスを作成または取得
        quiz_user_answer, created = QuizUserAnswer.objects.get_or_create(
            user=user,
            question=current_question
        )
        
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
            return redirect('quiz_result')


def result_view(request):
    user = request.user  # 現在のユーザーを取得
    
    if user.is_authenticated:
        # 分野ごとの得点を集計
        field_scores = QuizUserAnswer.objects.filter(
            user=user,
            selected_choices__is_correct=True
        ).values('question__field').annotate(
            total_score=Sum('question__point')
        )

        # 設定点数ごとの正解率を計算
        point_accuracy = QuizUserAnswer.objects.filter(
            user=user
        ).values('question__point').annotate(
            correct_count=Count('id', filter=Q(selected_choices__is_correct=True)),
            total_count=Count('id')
        )

        # 集計結果をテンプレートに渡す
        context = {
            'field_scores': field_scores,
            'point_accuracy': point_accuracy,
        }
        return render(request, 'kokushi_results.html', context)
    else:
        return redirect('pt_kokushi:top')
    
    
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

