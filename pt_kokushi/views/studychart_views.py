from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from pt_kokushi.models.studychart_models import StudyLog
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.db.models import Sum
from django.utils.timezone import now, timedelta

def studychart_view(request):
    # ここでデータを準備する（例: 学習ログのデータ）
    data = {
        'labels': ['1日', '2日', '3日'],  # グラフのラベル（X軸）
        'data': [5, 3, 4],  # 各日の学習時間（Y軸）
    }
    return render(request, 'login_app/studychart.html', {'chart_data': data})

@login_required
def save_study_log(request):
    if request.method == 'POST':
        # フォームからデータを取得
        study_date = request.POST.get('study_date')
        study_duration = request.POST.get('study_duration')
        
        # StudyLogモデルインスタンスを作成し、データベースに保存
        StudyLog.objects.create(
            user=request.user,
            study_date=study_date,
            study_duration=study_duration,
        )
        
        # 保存後は学習ログページにリダイレクト（または任意のページに）
        return redirect(reverse('pt_kokushi:studychart'))  
    else:
        # GETリクエストの場合、フォームページにリダイレクト
        return redirect(reverse('pt_kokushi:studychart'))
    
def study_date(request):
    today = datetime.now().date().isoformat()  # 'YYYY-MM-DD'形式の文字列
    context = {'today': today}
    return render(request, 'login_app/studychart.html', context)

@login_required
def study_log_data(request):
    # ログインユーザーに紐づくログのみを取得
    logs = StudyLog.objects.filter(user=request.user).order_by('study_date')
    data = list(logs.values('study_date', 'study_duration'))
    return JsonResponse(data, safe=False)

#学習時間の合計の計算
def study_summary_view(request):
    today = now()
    start_of_week = today - timedelta(days=today.weekday())  # 今週の月曜日
    start_of_month = today.replace(day=1)  # 今月の初日
    start_of_year = today.replace(month=1, day=1)  # 今年の初日

    weekly_total = StudyLog.objects.filter(
        user=request.user,
        study_date__range=[start_of_week, today]
    ).aggregate(total=Sum('study_duration'))['total'] or 0

    monthly_total = StudyLog.objects.filter(
        user=request.user,
        study_date__range=[start_of_month, today]
    ).aggregate(total=Sum('study_duration'))['total'] or 0

    yearly_total = StudyLog.objects.filter(
        user=request.user,
        study_date__range=[start_of_year, today]
    ).aggregate(total=Sum('study_duration'))['total'] or 0

    total_study_time = StudyLog.objects.filter(
        user=request.user
    ).aggregate(total=Sum('study_duration'))['total'] or 0

    context = {
        'weekly_total': weekly_total / 60,  # 分を時間に変換
        'monthly_total': monthly_total / 60,  # 分を時間に変換
        'yearly_total': yearly_total / 60,  # 分を時間に変換
        'total_study_time': total_study_time / 60,  # 分を時間に変換
    }
    return render(request, 'login_app/studychart.html', context)