from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} logged in on {self.login_date}"
