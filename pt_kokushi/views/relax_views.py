from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from pt_kokushi.models.relax_models import Column

def relaxation_room(request):
    columns = Column.objects.all().order_by('-published_date')[:5]  # 最新の5件のコラムを取得
    context = {
        'columns': columns,
    }
    return render(request, 'relax/relaxation_room.html', context)

def column_detail(request, pk):
    column = get_object_or_404(Column, pk=pk)
    return render(request, 'relax/column_detail.html', {'column': column})