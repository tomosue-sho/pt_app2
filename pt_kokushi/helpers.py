from pt_kokushi.models.LoginHistory_models import LoginHistory
from datetime import timedelta

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
