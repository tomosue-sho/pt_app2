from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now,timedelta,datetime
from django.db.models import Q
from pt_kokushi.models.kokushi_models import Exam,QuizQuestion, Choice, QuizUserAnswer
from pt_kokushi.models.kokushi_models import KokushiQuizSession, Bookmark, QuestionRange
from django.db.models import Count, Sum, Avg,Q,Case,When,Value,OuterRef, Subquery
from django.db.models import F, FloatField, ExpressionWrapper,IntegerField,fields
from django.db.models.functions import Cast
from django.utils.duration import duration_string 
from ..helpers import calculate_field_accuracy,calculate_field_accuracy_all,calculate_all_users_question_accuracy,calculate_median
from ..helpers import calculate_median,calculate_all_user_average_accuracy,calculate_new_user_accuracy,calculate_user_question_accuracy
from ..helpers import calculate_specific_point_accuracy,is_answer_correct,calculate_questions_accuracy,get_correctness_text
from ..helpers import get_user_field_accuracy_ranking,calculate_average_accuracy_by_field_for_all_users
import json, random
from django.utils.dateparse import parse_datetime


# 試験回選択用
def exam_selection_view(request):
    years = list(reversed(range(49, 60)))  # 49から59までのリストを作成
    if request.method == 'POST':
        exam_year = request.POST.get('exam_year')
        request.session['exam_year'] = int(exam_year)
        return HttpResponseRedirect(reverse('pt_kokushi:timer'))
    else:
        return render(request, 'top_view', {'years': years})

#国試タイマー
def time_setting_view(request):
    if request.method == 'POST':
        user = request.user

        # Clear unnecessary session information
        if 'last_question_id' in request.session:
            del request.session['last_question_id']

        # Retrieve time limit and exam year from the form
        time_limit = request.POST.get('time_limit')
        custom_time_limit = request.POST.get('custom_time_limit')
        exam_year = request.POST.get('exam_year')

        # Attempt to fetch the exam object based on the specified year
        try:
            exam = Exam.objects.get(year=exam_year)
        except Exam.DoesNotExist:
            return render(request, 'kokushi/timer.html', {'error': '指定された試験が存在しません。'})

        # Attempt to fetch the question range for the exam
        try:
            question_range = QuestionRange.objects.get(exam=exam)
        except QuestionRange.DoesNotExist:
            return render(request, 'kokushi/timer.html', {'error': 'この試験の問題範囲が設定されていません。'})

        # Time limit settings
        time_limit_seconds = int(time_limit) * 60 if time_limit else int(custom_time_limit) * 60
        end_time = timezone.now() + timezone.timedelta(seconds=time_limit_seconds)

        # Add filtering conditions to get an existing session or create a new one
        existing_session = KokushiQuizSession.objects.filter(user=user, exam=exam).first()

        if existing_session:
            existing_session.start_time = timezone.now()
            existing_session.end_time = end_time
            
            existing_session.start_question_id = question_range.start_id
            existing_session.end_question_id = question_range.end_id
            existing_session.save()
        else:
            new_session = KokushiQuizSession.objects.create(
                user=user, 
                exam=exam, 
                start_time=timezone.now(), 
                end_time=end_time,
                start_question_id=question_range.start_id,
                end_question_id=question_range.end_id
            )

        
        request.session['exam_year'] = exam_year
        request.session['start_question_id'] = question_range.start_id
        request.session['end_question_id'] = question_range.end_id

        question_id = 1  # 実際には適切な質問IDを動的に決定する必要があります
        return HttpResponseRedirect(reverse('pt_kokushi:quiz_questions', kwargs={'question_id': question_id}))
    else:
        user = request.user
        user_all_answers = QuizUserAnswer.objects.filter(user=user)
        total_questions_answered_cumulative = user_all_answers.count()
        total_correct_answers_cumulative = sum(1 for answer in user_all_answers if answer.is_correct())
        cumulative_accuracy_rate = (total_correct_answers_cumulative / total_questions_answered_cumulative * 100) if total_questions_answered_cumulative else 0

        context = {
            'total_questions_answered_cumulative': total_questions_answered_cumulative,
            'total_correct_answers_cumulative': total_correct_answers_cumulative,
            'cumulative_accuracy_rate': cumulative_accuracy_rate,
        }
        return render(request, 'kokushi/timer.html', context)
    
    
def start_kokushi_quiz(request):
    # クイズ開始時刻を現在時刻とする
    start_time = datetime.now()
    request.session['start_time'] = start_time.strftime('%Y-%m-%d %H:%M:%S')
 
    # クイズページにリダイレクト
    return redirect('quiz_page')

def quiz_page(request):
    # セッションから終了時刻を取得
    end_time_str = request.session.get('end_time')
    if end_time_str:
        end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')
        # 現在時刻を取得
        now = datetime.now()
        # 残り時間を計算（秒単位）
        remaining_seconds = int((end_time - now).total_seconds())
        remaining_seconds = max(remaining_seconds, 0) # 残り時間が負にならないように
    else:
        remaining_seconds = 0 # 終了時刻がない場合、残り時間を0とする

    context = {
        'remaining_seconds': remaining_seconds,
    }
    return render(request, 'quiz_page.html', context)

def quiz_questions_view(request, question_id=None):
    # セッションから試験年度を取得
    exam_year = request.session.get('exam_year', None)
    time_limit = request.session.get('time_limit')  # 時間設定をセッションから取得
    
    if not exam_year:
        return redirect('pt_kokushi:top')
    
    exam = get_object_or_404(Exam, year=exam_year)
    
    # QuestionRangeから問題IDの範囲を取得
    question_range = get_object_or_404(QuestionRange, exam=exam)
    questions = QuizQuestion.objects.filter(exam=exam, id__range=(question_range.start_id, question_range.end_id))
    
    if not questions.exists():
        return render(request, 'kokushi/no_questions.html', {'exam': exam})
    
    # 指定されたquestion_idが範囲内にあるか確認
    if question_id and (question_range.start_id <= int(question_id) <= question_range.end_id):
        question = get_object_or_404(QuizQuestion, exam=exam, id=question_id)
    else:
        question = questions.first()  # 範囲内の最初の問題を取得
    
    if question:
        previous_question = QuizQuestion.objects.filter(id__lt=question.id, id__range=(question_range.start_id, question_range.end_id)).order_by('-id').first()
    else:
        previous_question = None

    quiz_session = KokushiQuizSession.objects.filter(user=request.user, exam=exam).first()
    
    # 選択肢をランダムにする
    choices = list(question.choices.all()) if question else []
    random.shuffle(choices)
    
    context = {
        'exam': exam,
        'choices': choices,
        'question': question,
        'time_limit': time_limit,
        'quiz_session': quiz_session,
        'has_previous_question': previous_question is not None,
        'previous_question_id': previous_question.id if previous_question else None,
    }
    
    return render(request, 'kokushi/quiz_questions.html', context)

def finish_quiz_view(request):
    # 試験年度をセッションまたは他の方法から取得
    exam_year = request.session.get('exam_year', None)
    if exam_year:
        exam = Exam.objects.get(year=exam_year)
        # 現在のユーザーと試験に対応するセッションを取得し、終了時刻を更新
        session = KokushiQuizSession.objects.get(user=request.user, exam=exam)
        session.end_time = now()
        session.save()

    # 終了後のページにリダイレクト
    return redirect('pt_kokushi:kokushi_results')

#問題一覧表用
def quiz_question_list(request):
    exam_year = request.session.get('exam_year', None)
    if exam_year is None:
        return redirect('適切なページへのリダイレクト')

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

    if latest_session:
        # latest_sessionが存在する場合、そのセッション内で回答された問題のみを対象とする
        user_answers = QuizUserAnswer.objects.filter(
            Q(user=request.user, question__exam=exam) & 
            Q(answered_at__gte=latest_session.start_time) & 
            Q(answered_at__lte=latest_session.end_time if latest_session.end_time else now())
        ).values_list('question_id', flat=True)
    else:
        user_answers = []

    # 各問題に対する回答状態をマーク
    for question in list(questions_am) + list(questions_pm):
        question.answered = question.id in user_answers

    context = {
        'questions_am': questions_am,
        'questions_pm': questions_pm,
    }
    return render(request, 'kokushi/quiz_question_list.html', context)
 
#正解判定ーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
# 問題に取り組み始めるビュー
def submit_quiz_answers(request, question_id):
    if request.method == 'POST':
        user = request.user
        current_question = get_object_or_404(QuizQuestion, pk=question_id)
        selected_choice_ids = request.POST.getlist(f'question_{question_id}')

    if not selected_choice_ids:
        messages.error(request, '選択肢を選んでください。')
        return redirect('pt_kokushi:quiz_questions', question_id=question_id)

    exam_year = request.session.get('exam_year', None)
    exam = get_object_or_404(Exam, year=exam_year)
    question_range = get_object_or_404(QuestionRange, exam=exam)

    quiz_user_answer = QuizUserAnswer.objects.create(
        user=user,
        question=current_question,
        start_time=now()
    )
    quiz_user_answer.end_time = now()
    quiz_user_answer.save()

    for choice_id in selected_choice_ids:
        selected_choice = get_object_or_404(Choice, pk=choice_id)
        quiz_user_answer.selected_choices.add(selected_choice)
    
    request.session['last_answered_question_id'] = question_id

    next_question = QuizQuestion.objects.filter(id__gt=question_id, id__lte=question_range.end_id).order_by('id').first()
    if next_question:
        return redirect('pt_kokushi:quiz_questions', question_id=next_question.id)
    else:
        request.session['end_time'] = now().strftime('%Y-%m-%d %H:%M:%S')
        if exam_year:
            quiz_session = KokushiQuizSession.objects.filter(user=user, exam__year=exam_year).last()
            if quiz_session:
                quiz_session.end_time = now()
                quiz_session.save()

        return redirect('pt_kokushi:kokushi_results')

#成績計算-----------------------------------------------------
@login_required
def kokushi_results_view(request):
    
    # 既存のコード
    user = request.user
    exam_year = request.session.get('exam_year', None)
    exam = get_object_or_404(Exam, year=exam_year) if exam_year else None

    if not exam:
        return redirect('top')

    quiz_session = KokushiQuizSession.objects.filter(user=user, exam=exam).order_by('-start_time').first()
    
    # 一回の挑戦での回答数と正答数
    session_user_answers = QuizUserAnswer.objects.filter(
        user=user,
        question__exam=exam,
        answered_at__gte=quiz_session.start_time,
        answered_at__lte=quiz_session.end_time if quiz_session.end_time else now()
    )
    total_questions_answered_this_session = session_user_answers.count()
    total_correct_answers_this_session = sum(1 for answer in session_user_answers if answer.is_correct())

    if not quiz_session:
        return redirect('top')

    # 各種正答率の計算
    user_accuracy_all = calculate_new_user_accuracy(user, exam, quiz_session.start_time, quiz_session.end_time)
    user_3_point_accuracy = calculate_specific_point_accuracy(user, exam, 3, quiz_session.start_time, quiz_session.end_time)
    user_1_point_accuracy = calculate_specific_point_accuracy(user, exam, 1, quiz_session.start_time, quiz_session.end_time)
    all_user_average_accuracy = calculate_all_user_average_accuracy(exam)

   # ユーザーが回答した問題を「午前・午後」、「問題番号」の順で並べ替える
    user_answers = QuizUserAnswer.objects.filter(
        user=user,
        question__exam=exam
    ).order_by('question__time', 'question__question_number')

    # ユーザーが回答した問題のIDのリストを取得（重複なし）
    questions_seen = set()
    questions_accuracy = []
    is_quiz_incomplete = quiz_session.end_time is None

    for user_answer in user_answers:
        question = user_answer.question
        # 重複チェック
        if question.id in questions_seen:
            continue  # この問題は既にリストに追加されているためスキップ
        questions_seen.add(question.id)
        # 特定のユーザーの正答率
        user_accuracy = calculate_user_question_accuracy(user, question)
        # 全ユーザーの正答率
        all_users_accuracy = calculate_all_users_question_accuracy(question)
    
        user_answer = QuizUserAnswer.objects.filter(user=user, question=question).order_by('-answered_at').first()
        correct_text = get_correctness_text(user_answer) if user_answer else "回答なし"
    
        questions_accuracy.append({
        'question': question,
        'user_accuracy': user_accuracy,
        'is_correct_text': correct_text,
        'all_users_accuracy': all_users_accuracy,
        })
        
    all_users_accuracies = []
    questions = QuizQuestion.objects.filter(exam=exam)
    for question in questions:
        accuracy = calculate_all_users_question_accuracy(question)
        all_users_accuracies.append(accuracy)
        
    all_user_median_accuracy = calculate_median(all_users_accuracies)
    
    if quiz_session.end_time:
        exam_duration = quiz_session.end_time - quiz_session.start_time
    else:
        exam_duration = now() - quiz_session.start_time

    # exam_duration を分単位で計算
    exam_duration_minutes = exam_duration.total_seconds() / 60
    
    total_answered_questions = user_answers.count()
    user_answers = QuizUserAnswer.objects.filter(user=user, question__exam=exam)
    total_correct_answers = sum(1 for answer in user_answers if answer.is_correct())
    user_all_answers = QuizUserAnswer.objects.filter(user=user)
    total_questions_answered_cumulative = user_all_answers.count()
    total_correct_answers_cumulative = sum(1 for answer in user_all_answers if answer.is_correct())
    
    # 累計の正答率を計算（回答数が0の場合は0とする）
    if total_questions_answered_cumulative > 0:
        cumulative_accuracy_rate = (total_correct_answers_cumulative / total_questions_answered_cumulative) * 100
    else:
        cumulative_accuracy_rate = 0

    
    context = {
        'exam': exam,
        'user_accuracy_all': user_accuracy_all,
        'user_3_point_accuracy': user_3_point_accuracy,
        'user_1_point_accuracy': user_1_point_accuracy,
        'all_user_average_accuracy': all_user_average_accuracy,
        'quiz_session': quiz_session,
        'questions_accuracy': questions_accuracy,
        'all_user_median_accuracy': all_user_median_accuracy,
        'exam_duration_minutes': exam_duration_minutes,
        'is_quiz_incomplete': is_quiz_incomplete,
        'questions_accuracy': questions_accuracy,
        'total_answered_questions': total_answered_questions,
        'total_correct_answers': total_correct_answers,
        'total_questions_answered_this_session': total_questions_answered_this_session,
        'total_correct_answers_this_session': total_correct_answers_this_session,
        'total_questions_answered_cumulative': total_questions_answered_cumulative,
        'total_correct_answers_cumulative': total_correct_answers_cumulative,
        'cumulative_accuracy_rate': cumulative_accuracy_rate,
    }

    return render(request, 'kokushi/kokushi_results.html', context)

def evaluate_multiple_choice_answer(user_answer):
    # 正解の選択肢を取得
    correct_choices = user_answer.question.choices.filter(is_correct=True)
    correct_choice_ids = set(correct_choices.values_list('id', flat=True))
    
    # ユーザーが選択した選択肢のIDを取得
    user_selected_choice_ids = set(user_answer.selected_choices.values_list('id', flat=True))
    
    # 完全一致の評価
    if correct_choice_ids == user_selected_choice_ids:
        return 1.0  # 完全一致の場合は1.0のスコアを返す
    
    # 部分的な正解の扱い
    # 正解の選択肢のうち、いくつがユーザーによって選択されたか
    correct_selected_count = len(correct_choice_ids.intersection(user_selected_choice_ids))
    
    # 選択された不正解の選択肢の数
    incorrect_selected_count = len(user_selected_choice_ids - correct_choice_ids)
    
    if correct_selected_count > 0:
        partial_score = correct_selected_count / len(correct_choice_ids)
        return partial_score
    
    return 0

#セッションクリアのための関数（解き直し時とかに使う）ーーーーーーーーーーーー
#最初からやり直す関数
def restart_kokushi_quiz_view(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')

    # ユーザーのクイズ回答と進行状態をリセット
    QuizUserAnswer.objects.filter(user=user).delete()
    # 必要に応じてセッション情報のリセットも行う
    # request.session.pop('key', None)

    return redirect('pt_kokushi:quiz_questions', question_id=1)

#前回の続きから用
def continue_quiz_view(request):
    last_answered_question_id = request.session.get('last_answered_question_id', None)
    if last_answered_question_id is not None:
        # 最後に回答した質問の次の質問を探す
        next_question = QuizQuestion.objects.filter(id__gt=last_answered_question_id).order_by('id').first()
        if next_question:
            # 次の質問が存在する場合、その質問のページにリダイレクト
            return redirect('pt_kokushi:quiz_questions', question_id=next_question.id)
        else:
            # 次の質問が存在しない場合（最後の質問に回答済み）、クイズ結果ページにリダイレクト
            return redirect('pt_kokushi:kokushi_results')
    else:
        # セッションに最後に回答した質問のIDがない場合、クイズの最初の質問から開始
        first_question = QuizQuestion.objects.order_by('id').first()
        if first_question:
            return redirect('pt_kokushi:quiz_questions', question_id=first_question.id)
        else:
            # 質問が一つもない場合はエラーページにリダイレクト
            return redirect('pt_kokushi:error_page')

def exit_quiz(request):
    # セッションから最後に解答した質問のIDを取得
    last_question_id = request.session.get('last_question_id', None)
    
    if last_question_id is not None:
        return redirect('pt_kokushi:top')
    else:
        return redirect('pt_kokushi:timer')

#ブックマーク機能のためのviews.pyーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
# ブックマークを追加する関数
def add_bookmark(request, question_id):
    question = get_object_or_404(QuizQuestion, pk=question_id)
    Bookmark.objects.get_or_create(user=request.user, question=question)
    referer_url = request.META.get('HTTP_REFERER', 'pt_kokushi:top')
    return HttpResponseRedirect(referer_url)

# ブックマークを削除する関数
def remove_bookmark(request, question_id):
    question = get_object_or_404(QuizQuestion, pk=question_id)
    Bookmark.objects.filter(user=request.user, question=question).delete()
    referer_url = request.META.get('HTTP_REFERER', 'quiz_question/bookmarks/')
    return HttpResponseRedirect(referer_url)

def bookmark_list(request):
    mode = request.GET.get('mode', 'year')  # クエリパラメータから表示モードを取得

    user_bookmarks = Bookmark.objects.filter(user=request.user).select_related('question__exam', 'question__field').order_by('question__exam__year', 'question__field__name')

    # 年度ごとまたは分野ごとにブックマークをまとめる
    bookmarks_grouped = {}
    if mode == 'year':
        for bookmark in user_bookmarks:
            year = bookmark.question.exam.year
            bookmarks_grouped.setdefault(year, []).append(bookmark)
    elif mode == 'field':
        for bookmark in user_bookmarks:
            field_name = bookmark.question.field.name
            bookmarks_grouped.setdefault(field_name, []).append(bookmark)

    context = {
        'bookmarks_grouped': bookmarks_grouped,
        'mode': mode,  # 表示モードをコンテキストに追加
    }
    return render(request, 'kokushi/bookmark_list.html', context)

def question_detail(request, question_id):
    exam_year = request.session.get('exam_year', None)
    exam = Exam.objects.get(year=exam_year) if exam_year else None
    
    # 指定されたIDを持つ問題を取得
    question = get_object_or_404(QuizQuestion, pk=question_id)
    
    # ブックマークされているかどうかを確認
    is_bookmarked = Bookmark.objects.filter(user=request.user, question=question).exists()

    # テンプレートに渡すコンテキスト
    context = {
        'exam': exam,
        'question': question,
        'is_bookmarked': is_bookmarked
    }
    
    # テンプレートをレンダリング
    return render(request, 'kokushi/question_detail.html', context)

#ブックマークでの正誤判定
@csrf_exempt
def check_answer(request, question_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_choice_id = data.get('choice_id')
        correct_choice = Choice.objects.filter(question_id=question_id, is_correct=True).first()
        is_correct = str(correct_choice.id) == selected_choice_id
        return JsonResponse({'is_correct': is_correct})
  
#分野ごとの正答率用  
def field_result_view(request, exam_id):
    user = request.user
    exam = get_object_or_404(Exam, pk=exam_id)
    
    # ユーザーのクイズセッションを取得
    quiz_session = KokushiQuizSession.objects.filter(user=user, exam=exam).last()

    # ユーザーの累積成績を計算
    field_accuracy = calculate_field_accuracy(user, exam)
    #ユーザー個人のランキング
    user_ranking = get_user_field_accuracy_ranking(user, exam)
    
    # 全ユーザーの分野ごとの平均正答率を計算
    all_users_average_accuracy = calculate_average_accuracy_by_field_for_all_users(exam)
    all_users_average_accuracy_dict = {item['question__field__name']: item['average_accuracy'] for item in all_users_average_accuracy}

    # field_accuracy に全ユーザーの平均正答率を追加
    field_accuracy_with_avg = []
    for field in field_accuracy:
        field_name = field['question__field__name']
        field['all_users_average_accuracy'] = all_users_average_accuracy_dict.get(field_name, 0)
        field_accuracy_with_avg.append(field)
    
    # 平均正答率でソートしてランキングを作成
    accuracy_ranking = sorted(all_users_average_accuracy, key=lambda x: x['average_accuracy'], reverse=True)

    # quiz_session が存在する場合、その start_time と end_time を使用
    if quiz_session:
        start_time = quiz_session.start_time
        end_time = quiz_session.end_time
        current_exam_accuracy = calculate_field_accuracy_all(exam, start_time, end_time)
    else:
        current_exam_accuracy = []

    context = {
        'user_ranking': user_ranking,
        'field_accuracy': field_accuracy,
        'field_accuracy_with_avg': field_accuracy_with_avg,
        'accuracy_ranking': accuracy_ranking,
        'current_exam_accuracy': current_exam_accuracy,
        'labels': [item['question__field__name'] for item in field_accuracy],
        'percentages': [item['accuracy'] for item in field_accuracy],
        'exam': exam,
        'quiz_session': quiz_session,  # quiz_session をコンテキストに追加
    }
    
    return render(request, 'kokushi/field_result.html', context)

#成績ページのメディアクエリ用
@login_required
def user_stats_view(request):
    user = request.user
    exam_year = request.session.get('exam_year', None)
    exam = get_object_or_404(Exam, year=exam_year) if exam_year else None

    if not exam:
        return redirect('top')

    quiz_session = KokushiQuizSession.objects.filter(user=user, exam=exam).order_by('-start_time').first()

    if not quiz_session:
        return redirect('top')

    # 各種正答率の計算
    user_accuracy_all = calculate_new_user_accuracy(user, exam, quiz_session.start_time, quiz_session.end_time)
    user_3_point_accuracy = calculate_specific_point_accuracy(user, exam, 3, quiz_session.start_time, quiz_session.end_time)
    user_1_point_accuracy = calculate_specific_point_accuracy(user, exam, 1, quiz_session.start_time, quiz_session.end_time)
    all_user_average_accuracy = calculate_all_user_average_accuracy(exam)

   # ユーザーが回答した問題を「午前・午後」、「問題番号」の順で並べ替える
    user_answers = QuizUserAnswer.objects.filter(
        user=user,
        question__exam=exam
    ).order_by('question__time', 'question__question_number')

    # ユーザーが回答した問題のIDのリストを取得（重複なし）
    questions_seen = set()
    questions_accuracy = []

    for user_answer in user_answers:
        question = user_answer.question
        # 重複チェック
        if question.id in questions_seen:
            continue  # この問題は既にリストに追加されているためスキップ
        questions_seen.add(question.id)
        # 特定のユーザーの正答率
        user_accuracy = calculate_user_question_accuracy(user, question)
        # 全ユーザーの正答率
        all_users_accuracy = calculate_all_users_question_accuracy(question)
    
        user_answer = QuizUserAnswer.objects.filter(user=user, question=question).order_by('-answered_at').first()
        correct_text = get_correctness_text(user_answer) if user_answer else "回答なし"
    
        questions_accuracy.append({
        'question': question,
        'user_accuracy': user_accuracy,
        'is_correct_text': correct_text,
        'all_users_accuracy': all_users_accuracy,
        })
        
    all_users_accuracies = []
    questions = QuizQuestion.objects.filter(exam=exam)
    for question in questions:
        accuracy = calculate_all_users_question_accuracy(question)
        all_users_accuracies.append(accuracy)
        
    all_user_median_accuracy = calculate_median(all_users_accuracies)
    
    if quiz_session.end_time:
        exam_duration = quiz_session.end_time - quiz_session.start_time
    else:
        exam_duration = now() - quiz_session.start_time

    # exam_duration を分単位で計算
    exam_duration_minutes = exam_duration.total_seconds() / 60
    
    context = {
        'exam': exam,
        'user_accuracy_all': user_accuracy_all,
        'user_3_point_accuracy': user_3_point_accuracy,
        'user_1_point_accuracy': user_1_point_accuracy,
        'all_user_average_accuracy': all_user_average_accuracy,
        'quiz_session': quiz_session,
        'questions_accuracy': questions_accuracy,
        'all_user_median_accuracy': all_user_median_accuracy,
        'exam_duration_minutes': exam_duration_minutes,
    }
    return render(request, 'kokushi/stats_container.html', context)

