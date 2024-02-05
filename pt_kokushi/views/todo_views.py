from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from ..models import ToDoItem
from ..forms import ToDoItemForm

#ToDoリストのためのviews.py
# views.py
def create_todo_item(request):
    if request.method == 'POST':
        form = ToDoItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pt_kokushi:todo_list')  # 正しい名前空間を使用
    else:
        form = ToDoItemForm()

    return render(request, 'todolist/create_todo_item.html', {'form': form})


# ToDoアイテムのリストを表示するためのビュー
def todo_list(request):
    items = ToDoItem.objects.all().order_by('-priority', 'deadline')  # 優先度と期限で並べ替え
    return render(request, 'todolist/todo_list.html', {'todo_items': items})


#ToDo変更view
def update_todo_item(request, pk):
    todo_item = get_object_or_404(ToDoItem, pk=pk)
    if request.method == 'POST':
        form = ToDoItemForm(request.POST, instance=todo_item)
        if form.is_valid():
            form.save()
            return redirect('pt_kokushi:todo_list')
    else:
        form = ToDoItemForm(instance=todo_item)

    return render(request, 'todolist/update_todo_item.html', {'form': form, 'todo_item': todo_item})

#ToDo削除view
def delete_todo_item(request, pk):
    todo_item = get_object_or_404(ToDoItem, pk=pk)
    if request.method == 'POST':
        todo_item.delete()
        return redirect('pt_kokushi:todo_list')
    return render(request, 'todolist/delete_todo_item.html', {'todo_item': todo_item})