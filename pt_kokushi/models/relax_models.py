from django.db import models

class Column(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "休憩室コラム" 
        verbose_name_plural = "休憩室コラム" 