from django.db import models

#時間割表用models.py
class TimeTable(models.Model):
    DAY_CHOICES = [
        ('月', '月曜日'),
        ('火', '火曜日'),
        ('水', '水曜日'),
        ('木', '木曜日'),
        ('金', '金曜日'),
        ('土', '土曜日'),
        ('日', '日曜日'),
    ]
    PERIOD_CHOICES = [
        (1, '1限'),
        (2, '2限'),
        (3, '3限'),
        (4, '4限'),
        (5, '5限'),
        (6, '6限'),
    ]

    day = models.CharField(max_length=2, choices=DAY_CHOICES)
    period = models.IntegerField(choices=PERIOD_CHOICES)
    subject = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.get_day_display()} - {self.get_period_display()} - {self.subject}"
    
    class Meta:
        verbose_name = "時間割" 
        verbose_name_plural = "時間割" 
