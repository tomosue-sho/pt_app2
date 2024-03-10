from django.db import models

class Column(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "chatGPT小説" 
        verbose_name_plural = "chatGPT小説" 
        
class AozoraBook(models.Model):
    title = models.CharField(max_length=200, verbose_name="タイトル")
    content = models.TextField(verbose_name="内容")

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "青空文庫" 
        verbose_name_plural = "青空文庫" 