from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login as auth_login, get_user_model
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.urls import reverse
from pt_kokushi.models.question_models import Field,  Subfield, Sub2field, QuizSession
from pt_kokushi.models.question_models import Question, UserAnswer, UserScore
from django.db.models import Avg, Count, Sum, Q
from datetime import timedelta
from django.utils import timezone
import json
import random
import logging
logger = logging.getLogger(__name__)

def start_quiz(request):
    # 分野を選択するページを表
    fields = Field.objects.all()
    return render(request, '2quiz/select_field.html', {'fields': fields})

def quiz(request, subfield_id=None, sub2field_id=None):
    # 提示済み問題のIDをセッションから取得（存在しない場合は空のリスト）
    asked_questions = request.session.get('asked_questions', [])

    # subfield_id または sub2field_id に基づいて問題をフィルタリング
    if sub2field_id:
        sub2field = get_object_or_404(Sub2field, id=sub2field_id)
        questions = Question.objects.filter(sub2field=sub2field)
    elif subfield_id:
        subfield = get_object_or_404(Subfield, id=subfield_id)
        questions = Question.objects.filter(subfield=subfield, sub2field__isnull=True)
    else:
        field_id = request.session.get('last_field_id')
        if field_id:
            field = get_object_or_404(Field, id=field_id)
            questions = Question.objects.filter(subfield__field=field, subfield__isnull=True, sub2field__isnull=True)
        else:
            questions = Question.objects.none()

    total_questions = questions.count()

    # 既に全ての問題が提示された場合、または問題が4問以下の場合は、提示済みリストをリセット
    if len(asked_questions) >= total_questions or total_questions <= 4:
        asked_questions = []
        
    question = questions.exclude(id__in=asked_questions).order_by('?').first()

    # 選択した問題のIDをセッションに追加
    if question:
        asked_questions.append(question.id)
        request.session['asked_questions'] = asked_questions

    if not question:
        return render(request, '2quiz/no_questions.html', {})

    choices = [('1', question.choice1), ('2', question.choice2), ('3', question.choice3), ('4', question.choice4)]
    random.shuffle(choices)

    # 現在の問題のインデックスを取得
    current_index = request.session.get('current_question_index', 0) + 1
    request.session['current_question_index'] = current_index

    if current_index > 5:
        # インデックスをリセットし、成績ページへリダイレクト
        request.session['current_question_index'] = 0
        return redirect('pt_kokushi:quiz_results')

    return render(request, '2quiz/quiz.html', {'question': question, 'choices': choices})

def initialize_quiz(request):
    if request.method == 'POST':
        request.session['current_quiz_correct_answers'] = 0
        request.session['current_quiz_total_questions'] = 5  # 問題数をセット
        request.session.modified = True
        
        subfield_id = request.POST.get('subfield_id', None)
        sub2field_id = request.POST.get('sub2field_id', None)
        
        if sub2field_id:
            request.session['selected_sub2field_id'] = sub2field_id
            return redirect('pt_kokushi:quiz_sub2field', sub2field_id=sub2field_id)
        elif subfield_id:
            request.session['selected_subfield_id'] = subfield_id
            return redirect('pt_kokushi:quiz_subfield', subfield_id=subfield_id)
        else:
            # どちらのIDも存在しない場合の処理
            return redirect('pt_kokushi:top')

def quiz_page(request):
    questions = Question.objects.all()[:5]  # 最初の5問を取得
    questions_json = json.dumps(list(questions.values('id', 'question_text', 'correct_answer')))
    return render(request, 'quiz_page.html', {'questions_json': questions_json})


@csrf_exempt
@require_POST
def submit_answer(request):
    try:
        data = json.loads(request.body)
        selected_answer = str(data.get('selected_answer')) 
        question_id = data.get('question_id')
        
        # セッション変数の初期化
        if 'current_quiz_correct_answers' not in request.session:
            request.session['current_quiz_correct_answers'] = 0

        if not selected_answer or not question_id:
            return JsonResponse({'status': 'error', 'message': 'Missing data'}, status=400)

        User = get_user_model()
        user_email = request.user.email
        user = User.objects.get(email=user_email)

        question = Question.objects.get(pk=question_id)
        is_correct = selected_answer == question.correct_answer

        # ユーザーの回答を保存
        is_correct = selected_answer == question.correct_answer
        user_answer = UserAnswer(user=user, question=question, selected_answer=selected_answer, is_correct=is_correct)
        user_answer.save()

        # ユーザーのスコアを更新
        user_score, _ = UserScore.objects.get_or_create(user=user)
        if is_correct:
            user_score.total_correct_answers += 1
            user_score.total_score += 1
            request.session['current_quiz_correct_answers'] += 1
            request.session.modified = True
            print("Current Quiz Correct Answers:", request.session['current_quiz_correct_answers'])  # デバッグ情報の出力
            
        user_score.total_questions_attempted += 1
        user_score.save()

        # 次の問題へのURLを生成
        if question.sub2field_id:
            next_question_url = reverse('pt_kokushi:quiz_sub2field', kwargs={'sub2field_id': question.sub2field_id})
        elif question.subfield_id:
            next_question_url = reverse('pt_kokushi:quiz_subfield', kwargs={'subfield_id': question.subfield_id})
        elif question.field_id:
            next_question_url = reverse('pt_kokushi:quiz_field', kwargs={'field_id': question.field_id})
        else:
         # 適切なURLが生成できない場合の処理
            next_question_url = None
        
        return JsonResponse({'status': 'success', 'is_correct': is_correct, 'next_question_url': next_question_url})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Object not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


#quiz.htmlから途中で抜けた場合の処理（問題を解いた回数をリセットする）
@csrf_exempt
@require_POST
def reset_quiz_count(request):
    # セッション変数のリセット
    request.session['current_quiz_correct_answers'] = 0
    request.session['current_quiz_total_questions'] = 5  # 適切な問題数を設定
    request.session.modified = True  # セッションの変更を保存
    return JsonResponse({'status': 'success', 'message': 'クイズのセッション変数がリセットされました。'})

@csrf_exempt
@require_POST
def reset_quiz_session_for_sub2field(request):
    """
    sub2field経由でクイズを開始する際にセッション変数をリセットする専用関数。
    """
    # セッション変数のリセット
    request.session['current_quiz_correct_answers'] = 0
    request.session['current_quiz_total_questions'] = 5
    request.session['asked_questions'] = []
    request.session['current_question_index'] = 0
    request.session.modified = True  # 変更をセッションに適用

    # リセット成功のレスポンスを返す
    return JsonResponse({'status': 'success', 'message': 'クイズセッションがリセットされました。'})

def quiz_page_for_sub2field(request, sub2field_id):
    # サブフィールドオブジェクトを取得
    sub2field = get_object_or_404(Sub2field, pk=sub2field_id)
    
    # サブフィールドに紐づく質問をランダムに取得
    questions = Question.objects.filter(sub2field=sub2field).order_by('?')
    
    # クイズに使用する問題数を制限する（例えば最初の5問）
    questions = questions[:5]
    
    # クイズ開始時にセッション変数をリセット
    request.session['current_quiz_correct_answers'] = 0
    request.session['current_quiz_total_questions'] = len(questions)
    request.session['asked_questions'] = [question.id for question in questions]
    request.session['current_question_index'] = 0
    request.session.modified = True
    
    # クイズページへのコンテキスト
    context = {
        'sub2field': sub2field,
        'questions': questions,
    }

    # クイズページをレンダリング
    return render(request, 'quiz_page_for_sub2field.html', context)

#------------------------------------成績計算用--------------------
#成績計算用
def all_users_quiz_results(request):
    # 全ユーザーの成績情報を集計
    total_scores = UserScore.objects.aggregate(
        total_questions=Sum('total_questions_attempted'),
        total_correct=Sum('total_correct_answers'),
        average_score=Avg('total_score')
    )

    # 全ユーザーの正答率
    total_accuracy = (total_scores['total_correct'] / total_scores['total_questions'] * 100
                     if total_scores['total_questions'] > 0 else 0)

    return render(request, '2quiz/all_users_results.html', {
        'total_scores': total_scores,
        'total_accuracy': total_accuracy,
        # その他のコンテキスト変数
    })
    
#週間ランキング用
def weekly_ranking_view(request):
    one_week_ago = timezone.now() - timedelta(days=7)

    weekly_scores = UserAnswer.objects.filter(
        timestamp__gte=one_week_ago,
        is_correct=True
    ).values(
        'user__nickname'
    ).annotate(
        total_score=Sum('question__score'),
        total_correct_answers=Count('id', filter=Q(is_correct=True)),
        total_attempts=Count('id')
    ).order_by('-total_score')[:10]

    return render(request, 'weekly_ranking.html', {'weekly_scores': weekly_scores})

def some_view(request):
    # 全クイズセッションの平均正解数を計算
    average_correct_answers = QuizSession.objects.aggregate(average_correct=Avg('correct_answers'))

    # テンプレートに渡すコンテキスト
    context = {
        'average_correct_answers': average_correct_answers['average_correct'],
    }

    return render(request, '2quiz/results.html', context)

def quiz_results(request):
    user_score = UserScore.objects.get(user=request.user)
    subfield_id = request.session.get('last_subfield_id')
    field_id = request.session.get('last_field_id')
    sub2field_id = request.session.get('selected_sub2field_id')
    
    # ユーザーの総合正答率
    user_accuracy = (user_score.total_correct_answers / user_score.total_questions_attempted * 100
                     if user_score.total_questions_attempted > 0 else 0)

# 今回のクイズの正答回数と正答率を計算
    current_quiz_correct_answers = request.session.get('current_quiz_correct_answers', 0)
    # クイズの問題数をセッションから取得、またはデフォルト値5を使用
    current_quiz_total_questions = request.session.get('current_quiz_total_questions', 5)

    # 正答率を計算（0で除算することを避けるためのチェックを含む）
    if current_quiz_total_questions > 0:
        current_quiz_accuracy = (current_quiz_correct_answers / current_quiz_total_questions) * 100
    else:
        current_quiz_accuracy = 0

    # 全ユーザーの成績情報を集計
    total_scores = UserScore.objects.aggregate(
        total_questions=Sum('total_questions_attempted'),
        total_correct=Sum('total_correct_answers'),
        average_score=Avg('total_score')
    )
    total_accuracy = (total_scores['total_correct'] / total_scores['total_questions'] * 100
                      if total_scores['total_questions'] > 0 else 0)
    
    # 週間ランキングデータを集計
    one_week_ago = timezone.now() - timedelta(days=7)
    weekly_scores = UserAnswer.objects.filter(
        timestamp__gte=one_week_ago,
        is_correct=True
    ).values(
        'user__nickname'
    ).annotate(
        total_score=Sum('question__score'),
        total_correct_answers=Count('id', filter=Q(is_correct=True)),
        total_attempts=Count('id')
    ).order_by('-total_correct_answers')[:10]  # 正解数に基づいてランキングを行う

    return render(request, '2quiz/results.html', {
        'user_score': user_score,
        'user_accuracy': user_accuracy,
        'current_quiz_correct_answers': current_quiz_correct_answers, 
        'current_quiz_accuracy': current_quiz_accuracy,
        'total_scores': total_scores,
        'total_accuracy': total_accuracy,
        'weekly_scores': weekly_scores,
        'subfield_id': subfield_id,
        'field_id': field_id,
        'sub2field_id': sub2field_id
    })


#------------------------------------分野選択用----------------
#クイズの分野選択用の関数
def select_field(request):
    if request.method == 'POST':
        field_id = request.POST.get('field_id')
        request.session['last_field_id'] = field_id
        return redirect('pt_kokushi:select_subfield', field_id=field_id)
    else:
        fields = Field.objects.all()
        return render(request, '2quiz/select_field.html', {'fields': fields})

def select_subfield(request, field_id):
    if request.method == 'POST':
        subfield_id = request.POST.get('subfield_id')
        try:
            subfield = Subfield.objects.get(id=subfield_id)
            request.session['last_subfield_id'] = subfield_id
            if not subfield.has_detailed_selection:
                return redirect('pt_kokushi:initialize_quiz')
            else:
                return redirect('pt_kokushi:select_sub2field_template', subfield_id=subfield_id)
        except Subfield.DoesNotExist:
            messages.error(request, "選択されたサブフィールドは存在しません。")
            return redirect('pt_kokushi:select_field')
    else:
        # GET リクエストの処理
        field = get_object_or_404(Field, id=field_id)
        subfields = Subfield.objects.filter(field=field)
        return render(request, '2quiz/select_subfield.html', {'field': field, 'subfields': subfields})

@require_POST
def select_sub2field(request, subfield_id):
    sub2field_id = request.POST.get('sub2field_id')
    request.session['selected_sub2field_id'] = sub2field_id
    
    return redirect('pt_kokushi:select_sub2field_template', subfield_id=subfield_id)

def select_sub2field_template(request, subfield_id):
    subfield = get_object_or_404(Subfield, id=subfield_id)
    sub2fields = Sub2field.objects.filter(subfield=subfield)
    
    if request.method == 'POST':
        sub2field_id = request.POST.get('sub2field_id')
        request.session['selected_subfield_id'] = sub2field_id
        # initialize_quiz ページへリダイレクト
        return redirect('pt_kokushi:initialize_quiz')
    
    return render(request, '2quiz/select_sub2field.html', {'sub2fields': sub2fields, 'subfield': subfield})
