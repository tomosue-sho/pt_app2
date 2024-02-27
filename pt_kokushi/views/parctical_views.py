from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
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
    
    def get(self, request, *args, **kwargs):
        question_id = kwargs.get('question_id')
        question = get_object_or_404(QuizQuestion, pk=question_id)
        exam = question.exam 
        return render(request, 'practical/practical_quiz.html', {'question': question, 'exam': exam})
    
    def post(self, request, *args, **kwargs):
        question_id = request.POST.get('question_id')
        selected_choice_ids = request.POST.getlist('choices')
        question = get_object_or_404(QuizQuestion, pk=question_id)
        user = request.user

        # 選択された選択肢の取得と正誤判定
        selected_choices = Choice.objects.filter(id__in=selected_choice_ids)
        is_correct = question.quizuseranswer_set.create(
            user=user,
            question=question
        ).is_correct()
        for choice in selected_choices:
            QuizUserAnswer.objects.latest('id').selected_choices.add(choice)

        # 正誤に応じたメッセージ
        if is_correct:
            messages.success(request, "正解です！")
        else:
            messages.error(request, "不正解です。")

        # 次の問題へのリダイレクト
        next_question_id = self.get_next_question_id(request)
        if next_question_id is not None:
            return redirect(reverse('pt_kokushi:practical_quiz', kwargs={'question_id': next_question_id}))
        else:
            # 全ての問題が終了した場合、結果ページまたは適当なページにリダイレクト
            return redirect('some_result_page')

    def get_next_question_id(self, request):
        question_ids = request.session.get('question_ids', [])
        current_index = request.session.get('current_question_index', 0) + 1

        if current_index < len(question_ids):
            request.session['current_question_index'] = current_index
            return question_ids[current_index]
        else:
            return None

@require_POST
def toggle_bookmark(request):
    question_id = request.POST.get('question_id')
    question = get_object_or_404(QuizQuestion, pk=question_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, question=question)
    if not created:
        bookmark.delete()  # 既にブックマークされていた場合は削除
        return JsonResponse({'status': 'removed'})
    return JsonResponse({'status': 'added'})