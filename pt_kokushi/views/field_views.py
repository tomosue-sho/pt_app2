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
        # 新しいクイズが開始される前に、セッションから質問リストをクリア
        if 'question_ids' in request.session:
            del request.session['question_ids']
        
        field_id = request.POST.get('field')
        return redirect('pt_kokushi:field_quiz', field_id=field_id)
    else:
        fields = KokushiField.objects.all()
        return render(request, 'field/field_choice.html', {'fields': fields})


def field_quiz(request, field_id, question_id=None):
    field = get_object_or_404(KokushiField, pk=field_id)

    # セッションから質問IDリストを取得
    if 'question_ids' in request.session:
        question_ids = request.session['question_ids']
    else:
        # セッションに質問IDリストがない場合、質問を選択してセッションに保存
        question_ids = list(QuizQuestion.objects.filter(field=field).order_by('?').values_list('id', flat=True)[:10])
        request.session['question_ids'] = question_ids

    # question_idが指定されている場合、その質問を表示
    if question_id:
        questions = QuizQuestion.objects.filter(id=question_id)
    else:
        # 指定されていない場合、セッションに保存された最初の質問を表示
        questions = QuizQuestion.objects.filter(id__in=question_ids)

    question = questions.first()
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

        # 最新のユーザー回答を取得または新規作成
        user_answers = QuizUserAnswer.objects.filter(user=user, question=question)
        if user_answers.exists():
            user_answer = user_answers.latest('id')  # 最新の回答を取得
        else:
            user_answer = QuizUserAnswer.objects.create(user=user, question=question)

        user_answer.selected_choices.clear()
        for choice_id in selected_choice_ids:
            choice = get_object_or_404(Choice, pk=choice_id)
            user_answer.selected_choices.add(choice)
        user_answer.save()

        # 回答した質問をセッションから回答済みリストに追加
        answered_questions = request.session.get('answered_questions', [])
        if question_id not in answered_questions:
            answered_questions.append(question_id)
            request.session['answered_questions'] = answered_questions

        # 未回答の質問があるかチェック
        remaining_questions = [qid for qid in request.session['question_ids'] if qid not in answered_questions]
        if remaining_questions:
            # 未回答の質問があれば、次の質問へ
            next_question_id = remaining_questions[0]
            return redirect('pt_kokushi:field_quiz', field_id=field_id, question_id=next_question_id)
        else:
            # 全ての質問に回答した場合は成績ページへリダイレクト
            # セッションから質問リストをクリア
            if 'question_ids' in request.session:
                del request.session['question_ids']
            if 'answered_questions' in request.session:
                del request.session['answered_questions']
            return redirect('pt_kokushi:field_quiz_result', field_id=field_id)
    else:
        # 不正なリクエストの場合はエラーメッセージを表示
        messages.error(request, "不正なアクセスです。")
        return redirect('pt_kokushi:field_quiz', field_id=field_id)

@login_required
def field_quiz_result(request, field_id):
    user = request.user
    
    # 分野ごとのクイズ結果を計算する関数。この関数の実装は示されていません。
    results, accuracy, correct_count, total_questions = calculate_field_quiz_results(user, field_id)
    
    context = {
        'results': results,
        'accuracy': accuracy,
        'correct_count': correct_count,
        'total_questions': total_questions,
    }
    
    return render(request, 'field/field_quiz_result.html', context)

@require_POST
def toggle_bookmark(request):
    question_id = request.POST.get('question_id')
    question = get_object_or_404(QuizQuestion, pk=question_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, question=question)
    if not created:
        bookmark.delete()  # 既にブックマークされていた場合は削除
        return JsonResponse({'status': 'removed'})
    return JsonResponse({'status': 'added'})