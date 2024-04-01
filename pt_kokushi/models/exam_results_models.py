from django.db import models

class ExamResult(models.Model):
    exam_year = models.IntegerField(verbose_name='受験年度')
    applicants_total = models.IntegerField(verbose_name='出願者数(総合)')
    applicants_new_graduates = models.IntegerField(verbose_name='出願者数(新卒者)')
    examinees_total = models.IntegerField(verbose_name='受験者数(総合)')
    examinees_new_graduates = models.IntegerField(verbose_name='受験者数(新卒者)')
    passers_total = models.IntegerField(verbose_name='合格者数(総合)')
    passers_new_graduates = models.IntegerField(verbose_name='合格者数(新卒)')

    def __str__(self):
        return f"{self.exam_year}年度"

    @property
    def pass_rate_total(self):
        return (self.passers_total / self.examinees_total) * 100 if self.examinees_total else 0

    @property
    def pass_rate_new_graduates(self):
        return (self.passers_new_graduates / self.examinees_new_graduates) * 100 if self.examinees_new_graduates else 0

    @property
    def pass_rate_non_new_graduates(self):
        examinees_non_new_graduates = self.examinees_total - self.examinees_new_graduates
        passers_non_new_graduates = self.passers_total - self.passers_new_graduates
        return (passers_non_new_graduates / examinees_non_new_graduates) * 100 if examinees_non_new_graduates else 0
    
    class Meta:
        verbose_name = "国試「合格率」" 
        verbose_name_plural = "国試「合格率」"
