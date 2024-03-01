from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from django.urls import reverse
from django.utils.timezone import now,timedelta,datetime
from django.db.models import Q
from pt_kokushi.models.kokushi_models import Exam,QuizQuestion, Choice, QuizUserAnswer
from pt_kokushi.models.kokushi_models import KokushiQuizSession, Bookmark
from django.db.models import Count, Sum, Avg,Q,Case,When,Value,OuterRef, Subquery
from django.db.models import F, FloatField, ExpressionWrapper,IntegerField,fields
from django.db.models.functions import Cast
from django.utils.duration import duration_string 
from ..helpers import calculate_field_accuracy,calculate_field_accuracy_all,calculate_all_users_question_accuracy
from ..helpers import calculate_median,calculate_all_user_average_accuracy,calculate_new_user_accuracy,calculate_user_question_accuracy
from ..helpers import calculate_specific_point_accuracy,is_answer_correct,calculate_questions_accuracy
import json


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

        # 不要なセッション情報をクリア
        if 'last_question_id' in request.session:
            del request.session['last_question_id']

        # フォームから時間制限と試験年度を取得
        time_limit = request.POST.get('time_limit')
        custom_time_limit = request.POST.get('custom_time_limit')
        exam_year = request.POST.get('exam_year')

        # 試験年度に基づいて試験オブジェクトを取得
        exam = None
        if exam_year:
            try:
                exam = Exam.objects.get(year=exam_year)
            except Exam.DoesNotExist:
                return render(request, 'kokushi/timer.html', {'error': '指定された試験が存在しません。'})

        # タイマー設定
        time_limit_seconds = int(time_limit) * 60 if time_limit else int(custom_time_limit) * 60
        end_time = now() + timedelta(seconds=time_limit_seconds)

        # 新しいセッションを作成または更新
        KokushiQuizSession.objects.update_or_create(
            user=user,
            exam=exam,
            defaults={'start_time': now(), 'end_time': end_time}
        )

        # 新しいセッション情報をセッションに保存
        request.session['exam_year'] = exam_year

        return HttpResponseRedirect(reverse('pt_kokushi:quiz_questions'))
    else:
        return render(request, 'kokushi/timer.html')

def start_kokushi_quiz(request):
    # クイズ開始時刻を現在時刻とする
    start_time = datetime.now()
    # タイマーを30分に設定
    end_time = start_time + timedelta(minutes=30)
    # 開始時刻と終了時刻をセッションに保存
    request.session['start_time'] = start_time.strftime('%Y-%m-%d %H:%M:%S')
    request.session['end_time'] = end_time.strftime('%Y-%m-%d %H:%M:%S')
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
    question = get_object_or_404(QuizQuestion, pk=question_id) if question_id else None
    questions = QuizQuestion.objects.filter(exam=exam)
    quiz_session = KokushiQuizSession.objects.filter(user=request.user, exam=exam).first()
    
    if not questions.exists():
        return render(request, 'kokushi/no_questions.html', {'exam': exam})
    
    # question_idが指定されていればその質問を、そうでなければ最初の質問を取得
    if question_id:
        question = get_object_or_404(QuizQuestion, exam=exam, id=question_id)
    else:
        question = QuizQuestion.objects.filter(exam=exam).first()
        
    if question_id is None:
        # ここで、例えば最初の質問のIDを取得するか、エラーページにリダイレクトするなどの処理を行う
        first_question = QuizQuestion.objects.order_by('id').first()
        if first_question:
            return redirect('pt_kokushi:quiz_questions_detail', question_id=first_question.id)
        else:
            # 適切なエラーメッセージを表示するか、エラーページにリダイレクト
            return redirect('pt_kokuhsi:quiz_questions')
        
    previous_question = QuizQuestion.objects.filter(id__lt=question_id).order_by('-id').first()
    
    context = {
        'exam': exam,
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
    # 試験年度をセッションから取得する例（必要に応じて実装を追加）
    exam_year = request.session.get('exam_year', None)

    # 条件に基づいて問題をフィルタリング（ここではシンプルに時間帯でフィルタリング）
    questions_am = QuizQuestion.objects.filter(time='午前', exam__year=exam_year).order_by('question_number')
    questions_pm = QuizQuestion.objects.filter(time='午後', exam__year=exam_year).order_by('question_number')
    user_answers = QuizUserAnswer.objects.filter(user=request.user).values_list('question_id', flat=True)

    # 各問題に対する回答状態を追加
    # 午前と午後の問題を一緒に処理する
    all_questions = list(questions_am) + list(questions_pm)
    for question in all_questions:
        question.answered = question.id in user_answers

    context = {
        'questions_am': questions_am,
        'questions_pm': questions_pm,
        'user_answers': user_answers,
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
            return redirect('pt_kokushi:quiz_questions_detail', question_id=question_id)

        exam_year = request.session.get('exam_year', None)

        # 既存のQuizUserAnswerインスタンスを検索して取得するのではなく、新しいインスタンスを常に作成します。
        quiz_user_answer = QuizUserAnswer.objects.create(
            user=user,
            question=current_question,
            start_time=now()
        )
        # end_timeを設定して保存
        quiz_user_answer.end_time = now()
        quiz_user_answer.save()

        # 新しい選択肢を追加（以前の選択をクリアする必要はありません）
        for choice_id in selected_choice_ids:
            selected_choice = get_object_or_404(Choice, pk=choice_id)
            quiz_user_answer.selected_choices.add(selected_choice)
         
        # ここでのスコア計算やフィードバックの即時表示は行わない
        # 正解の選択肢IDセットとユーザーの選択肢IDセットを比較
        correct_choice_ids = set(current_question.choices.filter(is_correct=True).values_list('id', flat=True))
        selected_choice_ids_set = set(map(int, selected_choice_ids))

        # 次の問題へのリダイレクトまたは結果ページへのリダイレクトを行う
        next_question = QuizQuestion.objects.filter(id__gt=question_id).order_by('id').first()
        if next_question:
            return redirect('pt_kokushi:quiz_questions_detail', question_id=next_question.id)
        else:
            # 全問題に回答したかどうかをチェック
            if exam_year:
                total_questions = QuizQuestion.objects.filter(exam__year=exam_year).count()
                answered_questions = QuizUserAnswer.objects.filter(user=user, question__exam__year=exam_year).count()

                if total_questions == answered_questions:
                    # 全問題に回答した場合、試験セッションの終了時刻を更新
                    quiz_session = KokushiQuizSession.objects.filter(user=user, exam__year=exam_year).last()
                    if quiz_session:
                        quiz_session.end_time = now()
                        quiz_session.save()
            
            # 全ての回答が終了したら、結果ページへリダイレクト
            # 結果ページでは、ユーザーの全回答を集計してフィードバックを表示
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

    if not quiz_session:
        return redirect('top')

    # 各種正答率の計算
    user_accuracy_all = calculate_new_user_accuracy(user, exam, quiz_session.start_time, quiz_session.end_time)
    user_3_point_accuracy = calculate_specific_point_accuracy(user, exam, 3, quiz_session.start_time, quiz_session.end_time)
    user_1_point_accuracy = calculate_specific_point_accuracy(user, exam, 1, quiz_session.start_time, quiz_session.end_time)
    all_user_average_accuracy = calculate_all_user_average_accuracy(exam)

    # ユーザーが回答した問題を取得
    user_answers = QuizUserAnswer.objects.filter(
        user=user,
        question__exam=exam
    )

    # ユーザーが回答した問題のIDのリストを取得（重複なし）
    answered_question_ids = QuizUserAnswer.objects.filter(
    user=user,
    question__exam=exam
    ).values_list('question', flat=True).distinct()

    questions_accuracy = []
    for question_id in answered_question_ids:
        question = QuizQuestion.objects.get(id=question_id)
    
        # 特定のユーザーの正答率
        user_accuracy = calculate_user_question_accuracy(user, question)
    
        # 全ユーザーの正答率
        all_users_accuracy = calculate_all_users_question_accuracy(question)

        
        questions_accuracy.append({
        'question': question,
        'user_accuracy': user_accuracy,
        #'is_correct_text': correct_text,
        'all_users_accuracy': all_users_accuracy,
        })

    context = {
        'exam': exam,
        'user_accuracy_all': user_accuracy_all,
        'user_3_point_accuracy': user_3_point_accuracy,
        'user_1_point_accuracy': user_1_point_accuracy,
        'all_user_average_accuracy': all_user_average_accuracy,
        'quiz_session': quiz_session,
        'questions_accuracy': questions_accuracy,
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

    return redirect('pt_kokushi:quiz_questions_detail', question_id=1)

#前回の続きから用
def continue_quiz_view(request):
    last_question_id = request.session.get('last_question_id', None)
    if last_question_id is not None:
        # 最後に解答した質問のIDがある場合、次の質問を探す
        next_question = QuizQuestion.objects.filter(id__gt=last_question_id).order_by('id').first()
        if next_question:
            # 次の質問が存在する場合、その質問のページにリダイレクト
            return redirect('pt_kokushi:quiz_questions_detail', question_id=next_question.id)
        else:
            # 次の質問が存在しない場合（最後の質問に回答済み）、クイズ結果ページなどにリダイレクト
            return redirect('pt_kokushi:kokushi_results')
    else:
        # セッションに最後の質問のIDがない場合、クイズの最初の質問から開始
        first_question = QuizQuestion.objects.order_by('id').first()
        if first_question:
            return redirect('pt_kokushi:quiz_questions_detail', question_id=first_question.id)
        else:
            # 質問が一つもない場合は別のページにリダイレクト（エラーページなど）
            return redirect('pt_kokushi:error_page')  # 適切なリダイレクト先に変更してください

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