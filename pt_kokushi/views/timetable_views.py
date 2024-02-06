from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from pt_kokushi.models.timetable_models import TimeTable
from pt_kokushi.forms.timetable_forms import TimeTableForm

#時間割表用views.py
def create_timetable(request):
    if request.method == 'POST':
        form = TimeTableForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pt_kokushi:timetable_list')
    else:
        form = TimeTableForm()
    return render(request, 'login_app/create_timetable.html', {'form': form})

def timetable_list(request):
    timetables = TimeTable.objects.all()
    days = ['月', '火', '水', '木', '金', '土', '日']  # 曜日のリスト
    time_slots = ['1限', '2限', '3限', '4限', '5限', '6限']  # 時限のリスト

    # 時間割表を作成するためのデータ構造を作成
    timetable_data = {day: {time_slot: None for time_slot in time_slots} for day in days}

    for timetable in timetables:
        period_str = f'{timetable.period}限'  # 数値を文字列に変換
        timetable_data[timetable.day][period_str] = {
            'id': timetable.id,
            'subject': timetable.subject
    }


    return render(request, 'login_app/timetable_list.html', {
        'timetable_data': timetable_data,
        'days': days,
        'time_slots': time_slots,
    })


#時間割削除と変更機能
def delete_timetable(request, timetable_id):
    timetable = get_object_or_404(TimeTable, id=timetable_id)
    timetable.delete()
    return redirect('pt_kokushi:timetable_list')

def update_timetable(request, timetable_id):
    timetable = get_object_or_404(TimeTable, id=timetable_id)
    if request.method == 'POST':
        form = TimeTableForm(request.POST, instance=timetable)
        if form.is_valid():
            form.save()
            return redirect('pt_kokushi:timetable_list')
    else:
        form = TimeTableForm(instance=timetable)
    return render(request, 'login_app/edit_timetable.html', {'form': form, 'timetable': timetable})
