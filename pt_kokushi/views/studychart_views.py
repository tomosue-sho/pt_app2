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

def calculate_total_study_time_for_all_users():
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)

    # ユーザー全体のランキングデータ集計
    user_study_time = StudyLog.objects.values('user__nickname')\
        .annotate(
            total_time=Sum('study_duration'),
            weekly_total=Sum('study_duration', filter=Q(study_date__gte=start_of_week)),
            monthly_total=Sum('study_duration', filter=Q(study_date__gte=start_of_month)),
            yearly_total=Sum('study_duration', filter=Q(study_date__gte=start_of_year))
        ).order_by('-total_time')

    return user_study_time

def studychart(request):
    # 週間、月間、年間、トータルの学習時間を計算
    weekly_total = calculate_weekly_total(request.user)
    monthly_total = calculate_monthly_total(request.user)
    yearly_total = calculate_yearly_total(request.user)
    total_study_time = calculate_total_study_time(request.user)
    
    today = datetime.today()
    start_week = today - timedelta(days=today.weekday())
    end_week = start_week + timedelta(days=6)
    start_month = today.replace(day=1)
    end_month = (start_month + timedelta(days=31)).replace(day=1) - timedelta(days=1)
    start_year = today.replace(day=1, month=1)
    end_year = today.replace(day=31, month=12)

    total_study_time_for_all_users = User.objects.annotate(
        weekly_total=Sum('studylog__study_duration', filter=Q(studylog__study_date__range=[start_week, end_week])),
        monthly_total=Sum('studylog__study_duration', filter=Q(studylog__study_date__range=[start_month, end_month])),
        yearly_total=Sum('studylog__study_duration', filter=Q(studylog__study_date__range=[start_year, end_year])),
        total_time=Sum('studylog__study_duration')
    ).order_by('-total_time')
    
    total_study_time_for_all_users = calculate_total_study_time_for_all_users()
    study_logs = StudyLog.objects.filter(user=request.user).order_by('-study_date') 
    
    paginator = Paginator(study_logs, 5)  # 1ページあたりの表示数を5に設定
    page_number = request.GET.get('page')  # URLからページ番号を取得
    page_obj = paginator.get_page(page_number)  # ページオブジェクトを取得

    # テンプレートに渡すコンテキストを作成
    context = {
        'weekly_total': weekly_total / 60,  # 分を時間に変換
        'monthly_total': monthly_total / 60,  # 分を時間に変換
        'yearly_total': yearly_total / 60,  # 分を時間に変換
        'total_study_time': total_study_time / 60,  # 分を時間に変換
        'total_study_time_for_all_users': total_study_time_for_all_users, 
        'study_logs': study_logs,
        'page_obj': page_obj,
    }

    return render(request, 'login_app/studychart.html', context)

@login_required
def save_study_log(request):
    if request.method == 'POST':
        form = StudyLogForm(request.POST)
        if form.is_valid():
            study_log = form.save(commit=False)
            study_log.user = request.user
            study_log.save()

    else:
        form = StudyLogForm()

    # 学習統計の計算
    weekly_total, monthly_total, yearly_total, total_study_time = calculate_totals(request.user)

    # 全ユーザーのランキングデータの計算
    user_study_time_ranking = calculate_user_study_time_ranking()

    context = {
        'form': form,
        'weekly_total': weekly_total / 60,  # 分を時間に変換
        'monthly_total': monthly_total / 60,
        'yearly_total': yearly_total / 60,
        'total_study_time': total_study_time / 60,
        'user_study_time_ranking': user_study_time_ranking,  # ランキングデータをコンテキストに追加
    }

    # フォーム、学習統計、ランキングデータをテンプレートに渡す
    return render(request, 'login_app/studychart.html', context)

@login_required
def study_log_data(request):
    # ログインユーザーに紐づくログのみを取得
    logs = StudyLog.objects.filter(user=request.user).order_by('study_date')
    data = list(logs.values('study_date', 'study_duration'))
    return JsonResponse(data, safe=False)

#学習時間の合計の計算--------------------------------------
#個人の計算
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

#全ユーザーの計算
def calculate_totals(user):
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)

    weekly_total = StudyLog.objects.filter(
        user=user,
        study_date__gte=start_of_week
    ).aggregate(total=Sum('study_duration'))['total'] or 0

    monthly_total = StudyLog.objects.filter(
        user=user,
        study_date__gte=start_of_month
    ).aggregate(total=Sum('study_duration'))['total'] or 0

    yearly_total = StudyLog.objects.filter(
        user=user,
        study_date__gte=start_of_year
    ).aggregate(total=Sum('study_duration'))['total'] or 0

    total_study_time = StudyLog.objects.filter(
        user=user
    ).aggregate(total=Sum('study_duration'))['total'] or 0

    return weekly_total, monthly_total, yearly_total, total_study_time

#ランキング計算
def calculate_user_study_time_ranking():
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)

    user_study_time_ranking = StudyLog.objects.values('user__nickname')\
        .annotate(
            total_time=Sum('study_duration'),
            weekly_total=Sum('study_duration', filter=Q(study_date__gte=start_of_week)),
            monthly_total=Sum('study_duration', filter=Q(study_date__gte=start_of_month)),
            yearly_total=Sum('study_duration', filter=Q(study_date__gte=start_of_year))
        ).order_by('-total_time')

    return user_study_time_ranking


#学習記録の表示用
def study_content(request):
    objects_list = StudyLog.objects.filter(user=request.user).order_by('-study_date')
    paginator = Paginator(objects_list, 5)  # 5オブジェクトごとにページ分割

    page_number = request.GET.get('page')  # URLからページ番号を取得
    page_obj = paginator.get_page(page_number)  # 対応するページのオブジェクトを取得

    return render(request, 'login_app/studychart.html', {'page_obj': page_obj})

#フォーム用
@login_required
def study_log_form(request):
    if request.method == 'POST':
        form = StudyLogForm(request.POST)
        if form.is_valid():
            study_log = form.save(commit=False)
            study_log.user = request.user
            study_log.save()
            return redirect('pt_kokushi:studychart')
    else:
        form = StudyLogForm()

    return render(request, 'login_app/study_log_form.html', {'form': form})