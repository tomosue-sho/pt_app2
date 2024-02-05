from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ..forms import EventForm
from ..models import Event

#カレンダー用のviews.py
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user_email = request.user.email  # ユーザーのメールアドレスを設定
            event.save()
            return redirect('pt_kokushi:my_page')  # 適切なリダイレクト先に変更
    else:
        form = EventForm()
    return render(request, 'login_app/create_event.html', {'form': form})


def calendar_events(request):
    events = Event.objects.all()
    event_data = [{
        'id': event.id, 
        'title': event.title,
        'start': event.start_date.isoformat(),
        'end': event.end_date.isoformat(),
    } for event in events]
    return JsonResponse(event_data, safe=False)

#カレンダーイベント削除
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    return redirect('pt_kokushi:my_page')

    
#カレンダーイベント更新
def update_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('pt_kokushi:my_page')
    else:
        form = EventForm(instance=event)

    # コンテキストに event オブジェクトを追加
    context = {
        'form': form,
        'event': event  # この行を追加
    }
    return render(request, 'login_app/update_event.html', context)