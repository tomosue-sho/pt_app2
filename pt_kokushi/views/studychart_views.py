from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from pt_kokushi.models.studychart_models import StudyLog
from pt_kokushi.forms.studychart_forms import StudyLogForm
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.db.models import Sum ,Q
from django.utils.timezone import now, timedelta
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model

User = get_user_model()

def studychart(request):
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

    # 学習統計の計算
    weekly_total = calculate_weekly_total(request.user)
    monthly_total = calculate_monthly_total(request.user)
    yearly_total = calculate_yearly_total(request.user)
    total_study_time = calculate_total_study_time(request.user)

    context = {
        'form': form,
        'weekly_total': weekly_total / 60,  # 分を時間に変換
        'monthly_total': monthly_total / 60,
        'yearly_total': yearly_total / 60,
        'total_study_time': total_study_time / 60,
    }

    # フォームと学習統計をテンプレートに渡す
    return render(request, 'login_app/studychart.html', context)
@login_required
def study_log_data(request):
    # ログインユーザーに紐づくログのみを取得
    logs = StudyLog.objects.filter(user=request.user).order_by('study_date')
    data = list(logs.values('study_date', 'study_duration'))
    return JsonResponse(data, safe=False)

#学習時間の合計の計算--------------------------------------
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
    if request.method == 'POST':
        form = StudyLogForm(request.POST)
        if form.is_valid():
            # フォームのデータが有効な場合は、保存するなどの処理を行う
            form.save()
            return redirect('適切なリダイレクト先')
    else:
        form = StudyLogForm()

    # ここで学習時間の集計を行う
    user = request.user  # 現在のユーザーを取得
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)

    weekly_total = StudyLog.objects.filter(
        user=user,
        study_date__range=[start_of_week, today]
    ).aggregate(total=Sum('study_duration'))['total'] or 0

    monthly_total = StudyLog.objects.filter(
        user=user,
        study_date__range=[start_of_month, today]
    ).aggregate(total=Sum('study_duration'))['total'] or 0

    yearly_total = StudyLog.objects.filter(
        user=user,
        study_date__range=[start_of_year, today]
    ).aggregate(total=Sum('study_duration'))['total'] or 0

    total_study_time = StudyLog.objects.filter(
        user=user
    ).aggregate(total=Sum('study_duration'))['total'] or 0

    context = {
        'form': form,
        'weekly_total': weekly_total / 60,  # 分を時間に変換
        'monthly_total': monthly_total / 60,
        'yearly_total': yearly_total / 60,
        'total_study_time': total_study_time / 60,
    }

    return render(request, '適切なテンプレートパス', context)

#学習記録の表示用
def study_content(request):
    objects_list = StudyLog.objects.filter(user=request.user).order_by('-study_date')
    paginator = Paginator(objects_list, 5)  # 5オブジェクトごとにページ分割

    page_number = request.GET.get('page')  # URLからページ番号を取得
    page_obj = paginator.get_page(page_number)  # 対応するページのオブジェクトを取得

    return render(request, 'login_app/studychart.html', {'page_obj': page_obj})

#ランキング用
def study_time_ranking_view(request):
    today = timezone.now()
    start_of_week = today - timedelta(days=today.weekday())  # 今週の始まり
    start_of_month = today.replace(day=1)  # 今月の始まり
    start_of_year = today.replace(month=1, day=1)  # 今年の始まり

    # ユーザーごとのトータル学習時間を集計
    user_study_time = StudyLog.objects.values('user__username')\
        .annotate(
            total_time=Sum('study_duration'),
            weekly_total=Sum('study_duration', filter=Q(study_date__gte=start_of_week)),
            monthly_total=Sum('study_duration', filter=Q(study_date__gte=start_of_month)),
            yearly_total=Sum('study_duration', filter=Q(study_date__gte=start_of_year))
        ).order_by('-total_time')

    # ランキングデータをテンプレートに渡す
    context = {'user_study_time': user_study_time}
    return render(request, 'login_app/studychart.html', context)
