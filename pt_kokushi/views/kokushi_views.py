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
            # 事前定義された時間をセッションに保存
            request.session['time_limit'] = int(time_limit)
        elif custom_time_limit:
            try:
                # 任意の時間を整数としてセッションに保存
                request.session['time_limit'] = int(custom_time_limit)
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
    
from django.shortcuts import get_object_or_404, redirect

def quiz_questions_view(request, question_id=None):
    # セッションから試験年度を取得
    exam_year = request.session.get('exam_year', None)
    if not exam_year:
        return redirect('pt_kokushi:top')  # 試験年度が設定されていなければトップページへ

    # 試験年度に基づくExamオブジェクトを取得
    exam = get_object_or_404(Exam, year=exam_year)

    # question_idが指定されていればその質問を、そうでなければ最初の質問を取得
    if question_id:
        question = get_object_or_404(QuizQuestion, exam=exam, id=question_id)
    else:
        question = QuizQuestion.objects.filter(exam=exam).first()

    context = {
        'exam': exam,
        'question': question,  # 一つの質問のみを渡す
    }
    return render(request, 'kokushi/quiz_questions.html', context)


#正解判定ーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
def submit_quiz_answers(request, question_id):
    if request.method == 'POST':
        user = request.user
        total_score = 0
        for question in QuizQuestion.objects.all():
            selected_choices = request.POST.getlist(f'question_{question.id}')
            correct_choices = question.choices.filter(is_correct=True).values_list('id', flat=True)
            selected_correctly = all(choice in map(str, correct_choices) for choice in selected_choices) and len(selected_choices) == len(correct_choices)
            
            if selected_correctly:
                total_score += question.point  # 問題の点数を合計に加算
        
        # 次の問題を見つける
        next_question = QuizQuestion.objects.filter(id__gt=question_id).order_by('id').first()
        if next_question:
            return redirect('pt_kokushi:quiz_questions_view', question_id=next_question.id)
        else:
            # 次の問題がなければ、結果ページやクイズ終了ページへリダイレクト
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
        return redirect('quiz_question', question_id=next_question_id)
    else:
        # 進行状態がなければ、最初の問題から開始
        return redirect('quiz_question', question_id=1)
