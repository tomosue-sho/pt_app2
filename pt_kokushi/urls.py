from . import views_org
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from pt_kokushi.views.calender_views import create_event,calendar_events,delete_event,update_event
from pt_kokushi.views.todo_views import create_todo_item, todo_list, update_todo_item, delete_todo_item
from pt_kokushi.views.post_views import PostListView, PostDetailView,PostCreateView,PostDeleteView,CommentDeleteView,add_comment_to_post
from pt_kokushi.views.timetable_views import create_timetable,timetable_list,delete_timetable,update_timetable
from pt_kokushi.views.quiz_views import start_quiz,quiz,initialize_quiz,quiz_page,quiz_results,select_field,submit_answer,select_subfield,select_sub2field,select_sub2field_template,reset_quiz_count,all_users_quiz_results,weekly_ranking_view,some_view

app_name = 'pt_kokushi'

urlpatterns = [
    path('top/', views_org.TopView.as_view(), name='top'),
    path('signup/', views_org.signup_view, name='signup'),
    path('login/', views_org.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/', views_org.user_view, name='user'),
    path('my_page/', views_org.my_page_view, name='my_page'),
    path('password_change/', views_org.PasswordChange.as_view(), name='password_change'), #追加
    path('password_change/done/', views_org.PasswordChangeDone.as_view(), name='password_change_done'), #追加
    path('password_reset/', views_org.PasswordReset.as_view(), name='password_reset'), #追加
    path('password_reset/done/', views_org.PasswordResetDone.as_view(), name='password_reset_done'), #追加
    path('reset/<uidb64>/<token>/', views_org.PasswordResetConfirm.as_view(), name='password_reset_confirm'), #追加
    path('reset/done/', views_org.PasswordResetComplete.as_view(), name='password_reset_complete'), #追加
    path('change_password/', views_org.change_password_view, name='change_password'),
    path('change_nickname/', views_org.change_nickname_view, name='change_nickname'),
    path('get-remaining-time/', views_org.get_remaining_time, name='get-remaining-time'),
    path('posts/', PostListView.as_view(), name='post_list'),  # 掲示板投稿一覧
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),  # 掲示板投稿詳細
    path('post/new/', PostCreateView.as_view(), name='post_new'),  # 掲示板新規投稿
    path('post/<int:pk>/comment/', add_comment_to_post, name='add_comment_to_post'),  # 掲示板コメント追加
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),#掲示板
    path('comment/<int:pk>/delete/',CommentDeleteView.as_view(), name='comment_delete'),#掲示板
    path('todo/create/', create_todo_item, name='create_todo_item'),  # ToDoアイテム作成ページ
    path('todo/list/', todo_list, name='todo_list'),  # ToDoリストページ
    path('todo/update/<int:pk>/', update_todo_item, name='update_todo_item'),#ToDo変更
    path('todo/delete/<int:pk>/', delete_todo_item, name='delete_todo_item'),#ToDo削除
    path('create-event/', create_event, name='create_event'),#カレンダー
    path('calendar-events/', calendar_events, name='calendar_events'),#カレンダー
    path('event/delete/<int:event_id>/', delete_event, name='delete_event'),#カレンダー
    path('event/update/<int:event_id>/', update_event, name='update_event'),#カレンダー
    path('create-timetable/', create_timetable, name='create_timetable'),#時間割
    path('timetable/', timetable_list, name='timetable_list'),#時間割
    path('timetable/delete/<int:timetable_id>/', delete_timetable, name='delete_timetable'),#時間割
    path('timetable/update/<int:timetable_id>/', update_timetable, name='update_timetable'),#時間割
    path('start_quiz/', start_quiz, name='start_quiz'),
    path('quiz/results/', quiz_results, name='quiz_results'),
    path('select_field/', select_field, name='select_field'),
    path('select_subfield/<int:field_id>/', select_subfield, name='select_subfield'),
    path('select_sub2field/<int:subfield_id>/', select_sub2field, name='select_sub2field'),
    path('quiz/subfield/<int:subfield_id>/', quiz, name='quiz_subfield'),
    path('quiz/sub2field/<int:sub2field_id>/', quiz, name='quiz_sub2field'),
    path('quiz/<int:subfield_id>/', quiz, name='quiz'),
    path('quiz/<str:field>/', quiz, name='quiz_field'),
    path('submit_answer/', submit_answer, name='submit_answer'),
    path('quiz/results/', quiz_results, name='quiz_results'),
    path('initialize_quiz/', initialize_quiz, name='initialize_quiz'),
    path('select_sub2field_template/<int:subfield_id>/', select_sub2field_template, name='select_sub2field_template'),
    path('reset-quiz-count/', reset_quiz_count, name='reset_quiz_count'),
    ]

if settings.DEBUG:
     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)