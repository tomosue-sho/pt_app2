from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from pt_kokushi.models.studychart_models import StudyLog
from pt_kokushi.forms.studychart_forms import StudyLogForm
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.db.models import Sum
from django.utils.timezone import now, timedelta
from django.utils import timezone

def studychart_view(request):
    # 週間、月間、年間、トータルの学習時間を計算
    weekly_total = calculate_weekly_total(request.user)
    monthly_total = calculate_monthly_total(request.user)
    yearly_total = calculate_yearly_total(request.user)
    total_study_time = calculate_total_study_time(request.user)

    # テンプレートに渡すコンテキストを作成
    context = {
        'weekly_total': weekly_total / 60,  # 分を時間に変換
        'monthly_total': monthly_total / 60,  # 分を時間に変換
        'yearly_total': yearly_total / 60,  # 分を時間に変換
        'total_study_time': total_study_time / 60,  # 分を時間に変換
        # 他のコンテキストデータもここに追加
    }

    return render(request, 'login_app/studychart.html', context)

@login_required
@login_required
def save_study_log(request):
    if request.method == 'POST':
        form = StudyLogForm(request.POST)
        if form.is_valid():
            study_log = form.save(commit=False)
            study_log.user = request.user  # ユーザー情報を追加
            study_log.save()
            # 保存後は学習ログページにリダイレクト
            return redirect('pt_kokushi:studychart')
    else:
        form = StudyLogForm()

    # フォームをテンプレートに渡す
    return render(request, 'login_app/studychart.html', {'form': form})

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

    # ここで集計結果をコンソールに出力
    print(f"Weekly total: {weekly_total}, Monthly total: {monthly_total}, Yearly total: {yearly_total}, Total study time: {total_study_time}")

    context = {
        'weekly_total': weekly_total / 60,  # 分を時間に変換
        'monthly_total': monthly_total / 60,  # 分を時間に変換
        'yearly_total': yearly_total / 60,  # 分を時間に変換
        'total_study_time': total_study_time / 60,  # 分を時間に変換
    }
    return render(request, 'login_app/studychart.html', context)

def calculate_weekly_total(user):
    one_week_ago = timezone.now().date() - timedelta(days=7)
    total = StudyLog.objects.filter(user=user, study_date__gte=one_week_ago).aggregate(Sum('study_duration'))['study_duration__sum'] or 0
    return total

def calculate_monthly_total(user):
    one_month_ago = timezone.now().date() - timedelta(days=30)
    total = StudyLog.objects.filter(user=user, study_date__gte=one_month_ago).aggregate(Sum('study_duration'))['study_duration__sum'] or 0
    return total

def calculate_yearly_total(user):
    one_year_ago = timezone.now().date() - timedelta(days=365)
    total = StudyLog.objects.filter(user=user, study_date__gte=one_year_ago).aggregate(Sum('study_duration'))['study_duration__sum'] or 0
    return total

def calculate_total_study_time(user):
    total = StudyLog.objects.filter(user=user).aggregate(Sum('study_duration'))['study_duration__sum'] or 0
    return total

def study_stats_view(request):
    # 週間、月間、年間、トータルの学習時間を計算
    weekly_total = calculate_weekly_total(request.user)  # user引数を渡す
    monthly_total = calculate_monthly_total(request.user)  # user引数を渡す
    yearly_total = calculate_yearly_total(request.user)  # user引数を渡す
    total_study_time = calculate_total_study_time(request.user)  # user引数を渡す

    # テンプレートに渡すコンテキスト
    context = {
        'weekly_total': weekly_total / 60,  # 分を時間に変換
        'monthly_total': monthly_total / 60,  # 分を時間に変換
        'yearly_total': yearly_total / 60,  # 分を時間に変換
        'total_study_time': total_study_time / 60,  # 分を時間に変換
    }

    return render(request, 'login_app/studychart.html', context)
