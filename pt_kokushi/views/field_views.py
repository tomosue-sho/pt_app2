from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
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

    if questions.exists():
        first_question = questions.first()
        # 最初の問題へのリダイレクトではなく、問題リストを表示
        return render(request, 'field/field_quiz.html', {'questions': questions, 'field': field})
    else:
        messages.error(request, 'この分野には問題がありません。')
        return redirect('pt_kokushi:field_choice') 

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

        results = calculate_field_quiz_results(user, field_id)

        # 結果ページへリダイレクト（結果ページのURLやビュー名は適宜設定してください）
        return redirect('pt_kokushi:field_quiz_result', field_id=field_id)
    else:
        # 不正なリクエストの場合はエラーメッセージを表示
        messages.error(request, "不正なアクセスです。")
        return redirect('pt_kokushi:field_quiz', field_id=field_id)