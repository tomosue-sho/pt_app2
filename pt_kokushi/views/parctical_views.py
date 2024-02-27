from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.timezone import now
from django.views.generic import CreateView
from django.views.decorators.http import require_POST
from pt_kokushi.models.kokushi_models import QuizQuestion, Exam, Choice,QuizUserAnswer,KokushiQuizSession,Bookmark
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
import random

class PracticalChoiceView(View):
    def get(self, request, *args, **kwargs):
        years = Exam.objects.values_list('year', flat=True).distinct()
        return render(request, 'practical/practical_choice.html', {'years': years})

    def post(self, request, *args, **kwargs):
        year = request.POST.get('year')
        question_count = int(request.POST.get('questionCount', 10))

        if year == 'random':
            year_ids = Exam.objects.values_list('id', flat=True)
            year_id = random.choice(list(year_ids))
            questions = QuizQuestion.objects.filter(exam_id=year_id).order_by('?')[:question_count]
        else:
            questions = QuizQuestion.objects.filter(exam__year=year).order_by('?')[:question_count]

        question_ids = [question.id for question in questions]
        request.session['question_ids'] = question_ids
        request.session['current_question_index'] = 0

        if question_ids:
            first_question_id = question_ids[0]
            return redirect('pt_kokushi:practical_quiz', question_id=first_question_id)
        else:
            return render(request, 'error_page.html', {'message': '問題が見つかりませんでした。'})

class PracticalQuizView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        question_id = kwargs.get('question_id')
        selected_choice_ids = request.POST.getlist('choices')
        user = request.user
        question = get_object_or_404(QuizQuestion, pk=question_id)

        # 選択肢が選択されていない場合のエラーメッセージ
        if not selected_choice_ids:
            messages.error(request, '選択肢を選んでください。')
            return redirect(reverse('pt_kokushi:practical_quiz', kwargs={'question_id': question_id}))

        # ユーザーの選択を保存
        quiz_user_answer = QuizUserAnswer.objects.create(user=user, question=question, start_time=now())
        quiz_user_answer.end_time = now()
        for choice_id in selected_choice_ids:
            selected_choice = get_object_or_404(Choice, pk=choice_id)
            quiz_user_answer.selected_choices.add(selected_choice)
        quiz_user_answer.save()

        # 次の問題へのインデックスを更新
        question_ids = request.session.get('question_ids', [])
        current_index = question_ids.index(question_id) + 1

        # 正誤判定（仮実装、実際のロジックに応じて調整が必要）
        if quiz_user_answer.is_correct():  # is_correctメソッドは適切に実装する
            messages.success(request, "正解です！")
        else:
            messages.error(request, "不正解です。")

        # 次の問題があればそのページにリダイレクト、そうでなければ結果ページへ
        if current_index < len(question_ids):
            next_question_id = question_ids[current_index]
            return redirect(reverse('pt_kokushi:practical_quiz', kwargs={'question_id': next_question_id}))
        else:
            # セッションからクイズ関連の情報をクリア
            del request.session['question_ids']
            del request.session['current_question_index']
            return redirect('pt_kokushi:practical_quiz_result')
    
    def get(self, request, *args, **kwargs):
        question_id = kwargs.get('question_id')
        question = get_object_or_404(QuizQuestion, pk=question_id)
        choices = question.choices.all()  # QuestionモデルとChoiceモデルがリレーションを持っていると仮定

        # ユーザーが以前にこの問題に対して選択した回答を取得するロジックをここに追加（オプション）
        # user_answers = QuizUserAnswer.objects.filter(user=request.user, question=question)

        context = {
            'question': question,
            'choices': choices,
            # 'user_answers': user_answers,  # ユーザーの回答をテンプレートに渡す場合
        }
        return render(request, 'practical/practical_quiz.html', context)
    
@login_required
def practical_quiz_result(request):
    user = request.user
    question_ids = request.session.get('practical_questions_ids', [])

    results = []
    correct_count = 0
    for question_id in question_ids:
        question = QuizQuestion.objects.get(id=question_id)
        correct_choices = question.choices.filter(is_correct=True)
        correct_answer_texts = [choice.choice_text for choice in correct_choices]

        # ユーザーの回答を取得
        user_answer = QuizUserAnswer.objects.filter(user=user, question=question).first()

        # 正誤判定
        is_correct = user_answer and user_answer.is_correct()
        if is_correct:
            correct_count += 1

        results.append({
            'question': question,
            'user_answer': ', '.join([choice.choice_text for choice in user_answer.selected_choices.all()]) if user_answer else None,
            'correct_answer': ', '.join(correct_answer_texts),
            'is_correct': is_correct,
        })

    total_questions = len(question_ids)
    accuracy = (correct_count / total_questions) * 100 if total_questions else 0

    context = {
        'results': results,
        'total_questions': total_questions,
        'correct_count': correct_count,
        'accuracy': accuracy,
    }

    # 成績ページのテンプレートに変更
    return render(request, 'practical/practical_quiz_result.html', context)

@require_POST
def toggle_bookmark(request):
    question_id = request.POST.get('question_id')
    question = get_object_or_404(QuizQuestion, pk=question_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, question=question)
    if not created:
        bookmark.delete()  # 既にブックマークされていた場合は削除
        return JsonResponse({'status': 'removed'})
    return JsonResponse({'status': 'added'})