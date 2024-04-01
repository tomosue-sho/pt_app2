from django.shortcuts import render
from pt_kokushi.models.exam_results_models import ExamResult

def exam_results(request):
    results = ExamResult.objects.all().order_by('-exam_year')
    return render(request, 'exam_result/exam_results.html', {'results': results})
