from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from pt_kokushi.models.kokushi_models import QuizQuestion, Exam, Choice,QuizUserAnswer
from pt_kokushi.models.kokushi_models import KokushiQuizSession,Bookmark,KokushiField
from ..helpers import calculate_field_quiz_results

def field_choice(request):
    if request.method == "POST":
        field_id = request.POST.get('field')
        return redirect('pt_kokushi:field_quiz', field_id=field_id)
    else:
        fields = KokushiField.objects.all()
        return render(request, 'field/field_choice.html', {'fields': fields})


def field_quiz(request, field_id):
    field = get_object_or_404(KokushiField, pk=field_id)
    questions = QuizQuestion.objects.filter(field=field).order_by('?')[:10]  # 例: ランダムに10問選択

    question = questions.first() if questions.exists() else None
    exam = question.exam if question else None

    return render(request, 'field/field_quiz.html', {
        'questions': questions,
        'field': field,
        'question': question,
        'exam': exam,
    })

@login_required
def field_quiz_answer(request, field_id, question_id):
    if request.method == "POST":
        user = request.user
        question = get_object_or_404(QuizQuestion, pk=question_id)
        selected_choice_ids = request.POST.getlist('choices')

        # ユーザーの選択を保存
        user_answer, created = QuizUserAnswer.objects.get_or_create(
            user=user, question=question
        )
        user_answer.selected_choices.clear()
        for choice_id in selected_choice_ids:
            choice = get_object_or_404(Choice, pk=choice_id)
            user_answer.selected_choices.add(choice)
        user_answer.save()

        # 全ての問題に回答したかどうかをチェック
        all_questions = QuizQuestion.objects.filter(field_id=field_id).order_by('id')
        answered_questions = QuizUserAnswer.objects.filter(user=user, question__field_id=field_id).values_list('question_id', flat=True).distinct()
        
        if set(all_questions.values_list('id', flat=True)) == set(answered_questions):
            # 全ての問題に回答した場合は成績ページへリダイレクト
            return redirect('pt_kokushi:field_quiz_result', field_id=field_id)
        else:
            # まだ回答していない問題がある場合は次の問題へ
            next_question = all_questions.exclude(id__in=answered_questions).first()
            if next_question is not None:
                return redirect('pt_kokushi:field_quiz_question', field_id=field_id, question_id=next_question.id)
            else:
                # ここにエラーハンドリングを追加
                messages.error(request, "全ての問題に回答しましたが、成績ページへのリダイレクトに失敗しました。")
                return redirect('pt_kokushi:field_quiz_result', field_id=field_id)
    else:
        # 不正なリクエストの場合はエラーメッセージを表示
        messages.error(request, "不正なアクセスです。")
        return redirect('pt_kokushi:field_quiz', field_id=field_id)
    
    
@require_POST
def toggle_bookmark(request):
    question_id = request.POST.get('question_id')
    question = get_object_or_404(QuizQuestion, pk=question_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, question=question)
    if not created:
        bookmark.delete()  # 既にブックマークされていた場合は削除
        return JsonResponse({'status': 'removed'})
    return JsonResponse({'status': 'added'})