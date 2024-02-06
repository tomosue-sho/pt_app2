from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.urls import reverse
from django.http import HttpResponseRedirect
from pt_kokushi.models.kokushi_models import Exam


# 試験回選択用
def exam_selection_view(request):
    years = list(reversed(range(49, 60)))  # 49から59までのリストを作成
    if request.method == 'POST':
        exam_year = request.POST.get('exam_year')
        request.session['exam_year'] = exam_year
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

        if time_limit:
            # 事前定義された時間をセッションに保存
            request.session['time_limit'] = int(time_limit)
        elif custom_time_limit:
            try:
                # 任意の時間を整数としてセッションに保存
                request.session['time_limit'] = int(custom_time_limit)
            except ValueError:
                # 不正な入力の場合、エラーメッセージを設定
                # フォームにエラーメッセージを表示するためには、contextにエラーを追加して再度テンプレートをレンダリングする
                return render(request, 'kokushi/timer.html', {'error': '有効な時間を入力してください。'})

        # 問題ページへリダイレクト。まだ未作成
        return HttpResponseRedirect(reverse('pt_kokushi:kokushi_quiz_page'))
    else:
        # GETリクエストの場合は時間設定ページを表示
        return render(request, 'kokushi/timer.html')

#エラー回避の仮views.py
def kokushi_quiz_page(request):
    return HttpResponse("これは問題ページの仮のビューです。")
