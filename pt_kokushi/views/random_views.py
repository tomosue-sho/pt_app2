from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from pt_kokushi.models.kokushi_models import QuizQuestion, QuizQuestion, Choice, QuizUserAnswer,Exam
from ..helpers import calculate_field_accuracy,calculate_field_accuracy_all,calculate_all_user_average_accuracy
from ..helpers import calculate_random_questions_accuracy,calculate_random_quiz_results,calculate_questions_accuracy
import random
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

def random_quiz(request):
    # セッションデータのクリア
    request.session.pop('random_questions_ids', None)
    request.session.pop('current_question_index', None)
    
    # ユーザーの古い回答データをクリア
    QuizUserAnswer.objects.filter(user=request.user).delete()
    
    question_numbers = list(range(5, 101, 5))
    if request.method == "POST":
        num_questions = int(request.POST.get('num_questions', 10))
        questions = list(QuizQuestion.objects.order_by('?')[:num_questions])
        request.session['random_questions_ids'] = [q.id for q in questions]
        request.session['current_question_index'] = 0
        return redirect('pt_kokushi:random_question_display')
    return render(request, 'random/random_choice.html', {'question_numbers': question_numbers})

def random_question_display(request):
    question_ids = request.session.get('random_questions_ids', [])
    current_index = request.session.get('current_question_index', 0)

    if current_index >= len(question_ids):
        # 全ての問題が終了したら成績ページにリダイレクト
        return redirect('pt_kokushi:random_quiz_result')

    question = QuizQuestion.objects.get(id=question_ids[current_index])
    if request.method == "POST":
        # ユーザーの回答を処理
        # 成功したら、次の問題へ
        request.session['current_question_index'] = current_index + 1
        return redirect('random_question_display')

    return render(request, 'random/random_question_display.html', {'question': question})

@login_required
def submit_random_quiz_answers(request, question_id):
    if request.method == 'POST':
        user = request.user
        question_ids = request.session.get('random_questions_ids', [])
        current_index = request.session.get('current_question_index', 0)
        
        # 全問題終了時のリダイレクト先
        if current_index >= len(question_ids):
            return redirect('pt_kokushi:random_quiz_result')
        
        current_question_id = question_ids[current_index]
        current_question = get_object_or_404(QuizQuestion, pk=current_question_id)
        selected_choice_ids = request.POST.getlist(f'question_{current_question_id}')
        
        # 選択肢が選択されていない場合のエラーメッセージ
        if not selected_choice_ids:
            messages.error(request, '選択肢を選んでください。')
            return redirect('pt_kokushi:random_question_display')
        
        # ユーザーの選択を保存
        quiz_user_answer, created = QuizUserAnswer.objects.get_or_create(
            user=user,
            question=current_question,
            defaults={'start_time': now()}
        )
        quiz_user_answer.end_time = now()
        quiz_user_answer.selected_choices.clear()
        for choice_id in selected_choice_ids:
            selected_choice = get_object_or_404(Choice, pk=choice_id)
            quiz_user_answer.selected_choices.add(selected_choice)
        quiz_user_answer.save()
        
        # 次の問題へのインデックスを更新
        request.session['current_question_index'] = current_index + 1
        
        # 次の問題へリダイレクト、全問題終了後は結果ページへ
        if current_index + 1 < len(question_ids):
            return redirect('pt_kokushi:random_question_display')
        else:
            return redirect('pt_kokushi:random_quiz_result')

    # POST以外のリクエストの場合はクイズ選択ページにリダイレクト
    return redirect('pt_kokushi:random_quiz')

@login_required
def random_quiz_result(request):
    user = request.user
    question_ids = request.session.get('random_questions_ids', [])

    # calculate_random_quiz_results 関数を使用して結果を計算
    results, accuracy, correct_count, total_questions = calculate_random_quiz_results(user, question_ids)

    context = {
        'results': results,
        'total_questions': total_questions,
        'correct_count': correct_count,
        'accuracy': accuracy,
    }

    return render(request, 'random/random_quiz_result.html', context)

#成績ページから各問題に遷移するための関数
@login_required
def quiz_question_detail(request, question_id):
    question = get_object_or_404(QuizQuestion, pk=question_id)
    context = {
        'question_id': question.id, 
        'question': question,
    }
    return render(request, 'random/quiz_question_detail.html', context)
