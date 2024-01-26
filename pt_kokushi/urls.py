from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from .views import calendar_events
from django.urls import path

app_name = 'pt_kokushi'

urlpatterns = [
    path('top/', views.TopView.as_view(), name='top'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/', views.user_view, name='user'),
    path('my_page/', views.my_page_view, name='my_page'),
    path('password_change/', views.PasswordChange.as_view(), name='password_change'), #追加
    path('password_change/done/', views.PasswordChangeDone.as_view(), name='password_change_done'), #追加
    path('password_reset/', views.PasswordReset.as_view(), name='password_reset'), #追加
    path('password_reset/done/', views.PasswordResetDone.as_view(), name='password_reset_done'), #追加
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(), name='password_reset_confirm'), #追加
    path('reset/done/', views.PasswordResetComplete.as_view(), name='password_reset_complete'), #追加
    path('change_password/', views.change_password_view, name='change_password'),
    path('change_nickname/', views.change_nickname_view, name='change_nickname'),
    path('get-remaining-time/', views.get_remaining_time, name='get-remaining-time'),
    path('posts/', views.PostListView.as_view(), name='post_list'),  # 投稿一覧
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),  # 投稿詳細
    path('post/new/', views.PostCreateView.as_view(), name='post_new'),  # 新規投稿
    path('post/<int:pk>/comment/', views.add_comment_to_post, name='add_comment_to_post'),  # コメント追加
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('comment/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),
    path('todo/create/', views.create_todo_item, name='create_todo_item'),  # ToDoアイテム作成ページ
    path('todo/list/', views.todo_list, name='todo_list'),  # ToDoリストページ
    path('todo/update/<int:pk>/', views.update_todo_item, name='update_todo_item'),#ToDo変更
    path('todo/delete/<int:pk>/', views.delete_todo_item, name='delete_todo_item'),
    path('create-event/', views.create_event, name='create_event'),
    path('calendar-events/', calendar_events, name='calendar_events'),
    path('event/delete/<int:event_id>/', views.delete_event, name='delete_event'),
    path('event/update/<int:event_id>/', views.update_event, name='update_event'),
    path('create-timetable/', views.create_timetable, name='create_timetable'),
    path('timetable/', views.timetable_list, name='timetable_list'),
    path('timetable/delete/<int:timetable_id>/', views.delete_timetable, name='delete_timetable'),
    path('timetable/update/<int:timetable_id>/', views.update_timetable, name='update_timetable'),
    path('start_quiz/', views.start_quiz, name='start_quiz'),
    path('quiz/<str:field>/', views.quiz, name='quiz'),
    path('quiz/results/', views.quiz_results, name='quiz_results'),
    path('select_field/', views.select_field, name='select_field'),
    path('submit_answer/', views.submit_answer, name='submit_answer'),
    path('select_subfield/<int:field_id>/', views.select_subfield, name='select_subfield'),
]


