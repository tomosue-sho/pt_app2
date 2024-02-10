from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.urls import reverse
from django.http import HttpResponseRedirect
from pt_kokushi.models.kokushi_models import Exam,QuizQuestion


# 試験回選択用
def exam_selection_view(request):
    years = list(reversed(range(49, 60)))  # 49から59までのリストを作成
    if request.method == 'POST':
        exam_year = request.POST.get('exam_year')
        request.session['exam_year'] = int(exam_year)
        return HttpResponseRedirect(reverse('pt_kokushi:timer'))
    else:
        return render(request, 'top.html', {'years': years})

#試験年度のforループ用
def your_view_function(request):
    years = list(range(49, 59))  # Python 3ではrangeをlistに変換する必要がある
    return render(request, 'top.html', {'years': years})

# 国試タイマー用
def time_setting_view(request):
    if request.method == 'POST':
        # 時間設定を受け取る
        time_limit = request.POST.get('time_limit')
        custom_time_limit = request.POST.get('custom_time_limit')
        
        exam_year = request.POST.get('exam_year')

        if time_limit:
            # 事前定義された時間をセッションに保存
            request.session['time_limit'] = int(time_limit)
        elif custom_time_limit:
            try:
                # 任意の時間を整数としてセッションに保存
                request.session['time_limit'] = int(custom_time_limit)
            except ValueError:
                # 不正な入力の場合、エラーメッセージを設定
                return render(request, 'kokushi/timer.html', {'error': '有効な時間を入力してください。'})
        else:
            # 時間設定がない場合のエラーハンドリング
            return render(request, 'kokushi/timer.html', {'error': '時間を設定してください。'})
        
        if exam_year:
            request.session['exam_year'] = int(exam_year)

        # 正常に時間設定が完了した場合、quiz_questions_viewにリダイレクト
        return HttpResponseRedirect(reverse('pt_kokushi:quiz_questions'))
    else:
        # GETリクエストの場合は時間設定ページを表示
        return render(request, 'kokushi/timer.html')
    
def quiz_questions_view(request):
    # セッションから試験年度と時間設定を取得
    exam_year = request.session.get('exam_year')
    time_limit = request.session.get('time_limit')

    if not exam_year:
        # 試験年度がセッションに存在しない場合はエラーメッセージを表示
        return HttpResponse("試験年度が選択されていません。")

    try:
        # 試験年度に基づいたExamオブジェクトを取得
        exam = Exam.objects.get(year=exam_year)
    except Exam.DoesNotExist:
        # 指定された年度の試験が存在しない場合はエラーメッセージを表示
        return HttpResponse("指定された試験年度のデータが存在しません。")

    # 選択された試験年度に基づく問題を取得
    questions = QuizQuestion.objects.filter(exam=exam)

    # テンプレートに渡すデータをcontextにセット
    context = {
        'exam': exam,
        'questions': questions,
        'time_limit': time_limit,  # 時間設定をテンプレートに渡す
    }
    
    return render(request, 'kokushi/quiz_questions.html', context)
