from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.timezone import now
from django.views.generic import CreateView
from django.views.decorators.http import require_POST
from pt_kokushi.models.kokushi_models import QuizQuestion, Exam, Choice,QuizUserAnswer,KokushiQuizSession,Bookmark
from ..helpers import calculate_practical_quiz_results
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
import random

class PracticalChoiceView(View):
    def get(self, request, *args, **kwargs):
        years = Exam.objects.values_list('year', flat=True).distinct()
        return render(request, 'practical/practical_choice.html', {'years': years})

    def post(self, request, *args, **kwargs):
         # セッションからクイズ関連の情報をクリア
        if 'question_ids' in request.session:
            del request.session['question_ids']
        if 'current_question_index' in request.session:
            del request.session['current_question_index']
            
        QuizUserAnswer.objects.filter(user=request.user).delete()
        
        year = request.POST.get('year')
        question_count = int(request.POST.get('questionCount', 10))

        if year == 'random':
            year_ids = Exam.objects.values_list('id', flat=True)
            year_id = random.choice(list(year_ids))
        # 配点が3点の問題のみを選択するようにフィルタリング条件を追加
            questions = QuizQuestion.objects.filter(exam_id=year_id, point=3).order_by('?')[:question_count]
        else:
        # 同様に、配点が3点の問題のみを選択
            questions = QuizQuestion.objects.filter(exam__year=year, point=3).order_by('?')[:question_count]

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

        # 次の問題があればそのページにリダイレクト、そうでなければ結果ページへ
        if current_index < len(question_ids):
            next_question_id = question_ids[current_index]
            return redirect(reverse('pt_kokushi:practical_quiz', kwargs={'question_id': next_question_id}))
        else:

            return redirect('pt_kokushi:practical_quiz_result')
    
    def get(self, request, *args, **kwargs):
        question_id = kwargs.get('question_id')
        question = get_object_or_404(QuizQuestion, pk=question_id)
        choices = question.choices.all()
        exam = question.exam
        
        context = {
            'question': question,
            'choices': choices,
            'exam': exam,
        }
        return render(request, 'practical/practical_quiz.html', context)
    
@login_required
def practical_quiz_result(request):
    user = request.user
    
    results, accuracy, correct_count, total_questions = calculate_practical_quiz_results(user)
    
    context = {
        'results': results,
        'accuracy': accuracy,
        'correct_count': correct_count,
        'total_questions': total_questions,
    }
    
    return render(request, 'practical/practical_quiz_result.html', context)

def clear_quiz_session(request):
    # セッションからクイズ関連の情報をクリア
    if 'question_ids' in request.session:
        del request.session['question_ids']
    if 'current_question_index' in request.session:
        del request.session['current_question_index']

    # クイズの開始ページまたはトップページにリダイレクトする
    return redirect('pt_kokushi:top')

@require_POST
def toggle_bookmark(request):
    question_id = request.POST.get('question_id')
    question = get_object_or_404(QuizQuestion, pk=question_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, question=question)
    if not created:
        bookmark.delete()  # 既にブックマークされていた場合は削除
        return JsonResponse({'status': 'removed'})
    return JsonResponse({'status': 'added'})