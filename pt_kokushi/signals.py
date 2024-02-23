from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from pt_kokushi.models.LoginHistory_models import LoginHistory

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    LoginHistory.objects.create(user=user)
