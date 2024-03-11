from django.shortcuts import render, get_object_or_404, redirect
from pt_kokushi.models.kokushi_models import Exam,QuizQuestion, Choice, QuizUserAnswer
from pt_kokushi.models.kokushi_models import KokushiQuizSession, Bookmark, QuestionRange

# 年度選択ビュー
def select_exam_year(request):
    if request.method == 'POST':
        exam_year = request.POST.get('exam_year')
        request.session['exam_year'] = exam_year
        # 正しいリダイレクト先に変更します。問題一覧ページへのリダイレクト
        return redirect('pt_kokushi:kokushi_question_list')
    else:
        # Examモデルから年度を取得して表示
        years = Exam.objects.values_list('year', flat=True).distinct()
        return render(request, 'kokushi_search/kokushi_list.html', {'years': years})

# 選択された年度の問題一覧表示ビュー
def kokushi_question_list(request):
    exam_year = request.session.get('exam_year', None)
    if exam_year is None:
        return redirect('top')

    exam = get_object_or_404(Exam, year=exam_year)
    question_range = get_object_or_404(QuestionRange, exam=exam)

    # 最新のクイズセッションを取得
    latest_session = KokushiQuizSession.objects.filter(user=request.user, exam=exam).order_by('-start_time').first()

    # 午前と午後の問題をフィルタリング
    questions_am = QuizQuestion.objects.filter(
        exam=exam, 
        id__range=(question_range.start_id, question_range.end_id),
        time='午前'
    ).order_by('question_number')

    questions_pm = QuizQuestion.objects.filter(
        exam=exam, 
        id__range=(question_range.start_id, question_range.end_id),
        time='午後'
    ).order_by('question_number')

    context = {
        'questions_am': questions_am,
        'questions_pm': questions_pm,
    }
    return render(request, 'kokushi_search/kokushi_question_list.html', context)
