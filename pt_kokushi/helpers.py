from pt_kokushi.models.LoginHistory_models import LoginHistory
from pt_kokushi.models.kokushi_models import Exam,QuizQuestion, Choice, QuizUserAnswer
from pt_kokushi.models.kokushi_models import KokushiQuizSession, Bookmark
from datetime import timedelta
from django.db.models import Count, Sum, Avg,Q,Case,When,Value,OuterRef, Subquery
from django.db.models import F, FloatField, ExpressionWrapper,IntegerField,fields
from django.db.models.functions import Cast
from django.utils.duration import duration_string 

# self引数を削除
def calculate_login_streak(user):
    # 最新のログイン記録を取得
    login_history = LoginHistory.objects.filter(user=user).order_by('-login_date')
    if not login_history.exists():
        return 0  # ログイン履歴がない場合は0日

    streak = 1  # 最低でも1日はログインしている
    login_history = list(login_history)  # QuerySetをリストに変換
    for i in range(1, len(login_history)):
        if (login_history[i-1].login_date - login_history[i].login_date) == timedelta(days=1):
            streak += 1
        else:
            break  # 連続していない場合はループを抜ける

    return streak

def is_answer_correct(user_answer):
    correct_choices = set(user_answer.question.choices.filter(is_correct=True).values_list('id', flat=True))
    selected_choices = set(user_answer.selected_choices.values_list('id', flat=True))

    # ユーザーが選択した選択肢が正解の選択肢と完全に一致するかどうかをチェック
    return selected_choices == correct_choices and len(selected_choices) == len(correct_choices)

#1回の試験での3点問題1点問題の計算
def calculate_specific_point_accuracy(user, exam, point, start_time, end_time):
    questions = QuizQuestion.objects.filter(exam=exam, point=point)
    correct_count = 0
    total_attempts = 0  # 回答した質問の数を追跡

    for question in questions:
        user_answers = QuizUserAnswer.objects.filter(
            user=user, 
            question=question, 
            answered_at__gte=start_time, 
            answered_at__lte=end_time
        )

        for user_answer in user_answers:
            user_selected_choice_ids = set(user_answer.selected_choices.values_list('id', flat=True))
            correct_choice_ids = set(question.choices.filter(is_correct=True).values_list('id', flat=True))

            incorrect_choice_selected = not user_selected_choice_ids.issubset(correct_choice_ids)
            all_correct_choices_selected = correct_choice_ids.issubset(user_selected_choice_ids) and user_selected_choice_ids.issubset(correct_choice_ids)

            if all_correct_choices_selected and not incorrect_choice_selected:
                correct_count += 1
            total_attempts += 1

    accuracy = (correct_count / total_attempts) * 100 if total_attempts > 0 else 0
    return accuracy

def calculate_specific_point_data(user, exam, point, start_time, end_time):
    # 特定の点数に関連する質問をフィルタリング
    questions = QuizQuestion.objects.filter(exam=exam, point=point)
    correct_count = 0
    total_questions = questions.count()
    
    for question in questions:
        # 特定のセッション期間内でのユーザーの回答をフィルタリング
        user_answers = QuizUserAnswer.objects.filter(
            user=user, 
            question=question, 
            answered_at__gte=start_time, 
            answered_at__lte=end_time
        )
        
        # 各質問に対するユーザーの回答を確認
        for user_answer in user_answers:
            user_selected_choice_ids = set(user_answer.selected_choices.values_list('id', flat=True))
            correct_choice_ids = set(question.choices.filter(is_correct=True).values_list('id', flat=True))
            
            # 正解判定
            is_correct = user_selected_choice_ids == correct_choice_ids
            if is_correct:
                correct_count += 1
    
    return correct_count, total_questions


#今回の試験全体の正答率
def calculate_new_user_accuracy(user, exam, start_time, end_time):
     # 3点問題の正答率と問題数を取得
    correct_3_point, total_3_point = calculate_specific_point_data(user, exam, 3, start_time, end_time)
    
    # 1点問題の正答率と問題数を取得
    correct_1_point, total_1_point = calculate_specific_point_data(user, exam, 1, start_time, end_time)
    
    # トータルの正答数と問題数を算出
    total_correct = correct_3_point + correct_1_point
    total_questions = total_3_point + total_1_point
    
    # 全体の正答率を計算
    total_accuracy = (total_correct / total_questions) * 100 if total_questions > 0 else 0
    
    return total_accuracy

#１つの問題に対する累積正答率(個人)
def calculate_user_question_accuracy(user, question):
    # 特定のユーザーの特定の問題に対する正答数を集計
    correct_answers_count = QuizUserAnswer.objects.filter(
        user=user,
        question=question,
        selected_choices__is_correct=True
    ).count()

    # 特定のユーザーの特定の問題に対する回答数を集計
    total_answers_count = QuizUserAnswer.objects.filter(
        user=user,
        question=question
    ).count()

    # ユーザーの問題に対する累計正答率を計算（回答がある場合）
    if total_answers_count > 0:
        user_question_accuracy = (correct_answers_count / total_answers_count) * 100
    else:
        user_question_accuracy = 0

    return user_question_accuracy

#１つの問題に対する累積正答率(全ユーザー)
def calculate_all_users_question_accuracy(question):
    # 特定の問題に対する全ユーザーの回答を集計
    total_answers_count = QuizUserAnswer.objects.filter(question=question).count()
    correct_answers_count = QuizUserAnswer.objects.filter(question=question, selected_choices__is_correct=True).count()

    # 全ユーザーの問題に対する累計正答率を計算（回答がある場合）
    if total_answers_count > 0:
        all_users_question_accuracy = (correct_answers_count / total_answers_count) * 100
    else:
        all_users_question_accuracy = 0

    return all_users_question_accuracy

def calculate_questions_accuracy(user, exam, start_time, end_time):
    questions = QuizQuestion.objects.filter(exam=exam).order_by('time', 'question_number')
    questions_with_accuracy = []

    for question in questions:
        user_answers = QuizUserAnswer.objects.filter(user=user, question=question, answered_at__gte=start_time, answered_at__lte=end_time)
        correct_answers_count = user_answers.filter(selected_choices__is_correct=True).count()
        
        total_answers_count = QuizUserAnswer.objects.filter(question=question).count()

        all_user_accuracy = calculate_all_users_question_accuracy(question)

        questions_with_accuracy.append({
            'question_id': question.id,
            'session': question.time,
            'number': question.question_number,
            'field': question.field.name,
            'user_accuracy': (correct_answers_count / total_answers_count * 100) if total_answers_count > 0 else 0,
            'all_user_accuracy': all_user_accuracy, 
            'is_correct_text': '正解' if correct_answers_count > 0 else '不正解',
        })

    return questions_with_accuracy

#分野
def calculate_field_accuracy(user, exam):
    return QuizUserAnswer.objects.filter(user=user, question__exam=exam).annotate(
        is_correct=Case(
            When(selected_choices__is_correct=True, then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        )
    ).values('question__field__name').annotate(
        total=Count('question'),
        correct_sum=Sum('is_correct')
    ).annotate(
        accuracy=ExpressionWrapper(F('correct_sum') * 100.0 / F('total'), output_field=FloatField())
    ).order_by('question__field__name')

def calculate_field_accuracy_all(exam):
    return QuizUserAnswer.objects.filter(question__exam=exam).annotate(
        is_correct=Case(
            When(selected_choices__is_correct=True, then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        )
    ).values('question__field__name').annotate(
        total=Count('question'),
        correct_sum=Sum('is_correct')
    ).annotate(
        accuracy=ExpressionWrapper(F('correct_sum') * 100.0 / F('total'), output_field=FloatField())
    ).order_by('question__field__name')
    
def calculate_all_user_average_accuracy(exam):
    # 全ユーザーの全問題に対する正答数を集計
    correct_answers_count = QuizUserAnswer.objects.filter(
        question__exam=exam,
        selected_choices__is_correct=True
    ).count()

    # 全ユーザーの全問題に対する回答数を集計
    total_answers_count = QuizUserAnswer.objects.filter(
        question__exam=exam
    ).count()

    # 平均正答率を計算（回答がある場合）
    if total_answers_count > 0:
        all_user_average_accuracy = (correct_answers_count / total_answers_count) * 100
    else:
        all_user_average_accuracy = 0

    return all_user_average_accuracy

def calculate_median(values_list):
    if not values_list:
        return 0
    sorted_list = sorted(values_list)
    list_length = len(sorted_list)
    index = (list_length - 1) // 2

    if list_length % 2:
        return sorted_list[index]
    else:
        return (sorted_list[index] + sorted_list[index + 1]) / 2.0
    
#ランダム問題用
def calculate_random_quiz_results(user, question_ids):
    results = []
    correct_count = 0
    total_questions = len(question_ids)

    for question_id in question_ids:
        question = QuizQuestion.objects.get(id=question_id)
        user_answer = QuizUserAnswer.objects.filter(user=user, question=question).first()

        if user_answer:
            user_selected_choice_ids = set(user_answer.selected_choices.values_list('id', flat=True))
            correct_choice_ids = set(question.choices.filter(is_correct=True).values_list('id', flat=True))
            
            incorrect_choice_selected = not user_selected_choice_ids.issubset(correct_choice_ids)
            all_correct_choices_selected = user_selected_choice_ids.issuperset(correct_choice_ids)
            
            is_correct = user_selected_choice_ids == correct_choice_ids
            
            if is_correct:
                correct_count += 1

            results.append({
                 'question_id': question.id,  # 質問のIDを追加
                 'question_text': question.question_text,  # 質問テキスト
                 'user_answer': ', '.join([choice.choice_text for choice in user_answer.selected_choices.all()]) if user_answer else "未回答",
                 'correct_answer': ', '.join([choice.choice_text for choice in question.choices.filter(is_correct=True)]),
                 'is_correct': is_correct,
            })

        else:
            results.append({
                'question_id': question.id,  # 質問のIDを追加
                'question_text': question.question_text,  # 質問テキスト
                'user_answer': ', '.join([choice.choice_text for choice in user_answer.selected_choices.all()]) if user_answer else "未回答",
                'correct_answer': ', '.join([choice.choice_text for choice in question.choices.filter(is_correct=True)]),
                'is_correct': is_correct,
            })

    accuracy = (correct_count / total_questions) * 100 if total_questions > 0 else 0

    return results, accuracy, correct_count, total_questions

def calculate_random_questions_accuracy(user, question_ids):
    questions_with_accuracy = []
    for question_id in question_ids:
        question = QuizQuestion.objects.get(id=question_id)
        user_answers = QuizUserAnswer.objects.filter(user=user, question=question)
        correct_answers = user_answers.filter(selected_choices__is_correct=True).count()
        total_answers = user_answers.count()

        user_accuracy = (correct_answers / total_answers * 100) if total_answers else 0
        questions_with_accuracy.append({
            'session': question.time,
            'number': question.question_number,
            'field': question.field.name,
            'user_accuracy': user_accuracy,
            'is_correct': correct_answers == question.correct_choices_count()
        })

    return questions_with_accuracy

#3点問題用
def calculate_practical_quiz_results(user):
    answered_questions = QuizUserAnswer.objects.filter(user=user).values_list('question', flat=True).distinct()
    results = []
    correct_count = 0
    total_questions = len(answered_questions)
    
    for question_id in answered_questions:
        question = QuizQuestion.objects.get(id=question_id)
        user_answer = QuizUserAnswer.objects.filter(user=user, question=question).first()

        # 正解の選択肢のIDのセット
        correct_choice_ids = set(question.choices.filter(is_correct=True).values_list('id', flat=True))
        # correct_choice_ids から Choice オブジェクトを取得
        correct_choices = Choice.objects.filter(id__in=correct_choice_ids)
        # Choice オブジェクトから choice_text を取り出して結合
        correct_answer_texts = ', '.join([choice.choice_text for choice in correct_choices])

        if user_answer:
            # ユーザーが選んだ選択肢のIDのセット
            user_selected_choice_ids = set(user_answer.selected_choices.values_list('id', flat=True))
            
            # 不正解の選択肢が含まれているかをチェック
            incorrect_choice_selected = not user_selected_choice_ids.issubset(correct_choice_ids)
            # 正解の選択肢を全て選んでいるかをチェック
            all_correct_choices_selected = user_selected_choice_ids == correct_choice_ids
            
            # 正解判定
            is_correct = all_correct_choices_selected and not incorrect_choice_selected
            
            if is_correct:
                correct_count += 1
                
            results.append({
                'question': question.question_text,
                'user_answer': ', '.join([choice.choice_text for choice in user_answer.selected_choices.all()]),
                'correct_answer': correct_answer_texts,
                'is_correct': is_correct,
            })
        else:
            results.append({
                'question': question.question_text,
                'user_answer': "未回答",
                'correct_answer': correct_answer_texts,
                'is_correct': False,
            })
    
    accuracy = (correct_count / total_questions) * 100 if total_questions else 0
    return results, accuracy, correct_count, total_questions

#分野用の計算
def calculate_field_quiz_results(user, field_id):
    # 特定の分野に関連する問題のIDを取得
    question_ids = QuizQuestion.objects.filter(field_id=field_id).values_list('id', flat=True)
    results = []
    correct_count = 0
    total_questions = len(question_ids)

    for question_id in question_ids:
        question = QuizQuestion.objects.get(id=question_id)
        user_answer = QuizUserAnswer.objects.filter(user=user, question=question).first()

        if user_answer:
            # ユーザーが選んだ選択肢のIDのセット
            user_selected_choice_ids = set(user_answer.selected_choices.values_list('id', flat=True))
            # 正解の選択肢のIDのセット
            correct_choice_ids = set(question.choices.filter(is_correct=True).values_list('id', flat=True))
            
            # 不正解の選択肢が含まれているかどうか、および全ての正解が選ばれているかをチェック
            incorrect_choice_selected = not user_selected_choice_ids.issubset(correct_choice_ids)
            all_correct_choices_selected = user_selected_choice_ids == correct_choice_ids
            
            # 正解判定
            is_correct = all_correct_choices_selected and not incorrect_choice_selected
            
            if is_correct:
                correct_count += 1
            
            # 結果リストへの追加
            results.append({
                'question_id': question.id,
                'question_text': question.question_text,
                'user_answer': ', '.join([choice.choice_text for choice in user_answer.selected_choices.all()]) if user_answer else "未回答",
                'correct_answer': ', '.join([choice.choice_text for choice in question.choices.filter(is_correct=True)]),
                'is_correct': is_correct,
            })
        else:
            # ユーザーが回答していない場合
            results.append({
                'question_id': question.id,
                'question_text': question.question_text,
                'user_answer': "未回答",
                'correct_answer': ', '.join([choice.choice_text for choice in question.choices.filter(is_correct=True)]),
                'is_correct': False,
            })

    # 正確性の計算
    accuracy = (correct_count / total_questions) * 100 if total_questions > 0 else 0

    return results, accuracy, correct_count, total_questions

#ログイン日数の計算
def calculate_login_streak(user):
    login_dates = LoginHistory.objects.filter(user=user).order_by('login_date').values_list('login_date', flat=True)
    
    # 連続ログイン日数
    streak = 0
    # 前日の日付を記録する変数
    prev_date = None
    
    for login_date in login_dates:
        if prev_date is None or login_date == prev_date + timedelta(days=1):
            streak += 1
        elif login_date != prev_date:
            streak = 1
        prev_date = login_date
    
    return streak