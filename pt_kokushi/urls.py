from . import views_org
from . import views
from pt_kokushi.views_org import update_test_year
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from pt_kokushi.views.calender_views import create_event,calendar_events,delete_event,update_event
from pt_kokushi.views.todo_views import create_todo_item, todo_list, update_todo_item, delete_todo_item
from pt_kokushi.views.post_views import PostListView, PostDetailView,PostCreateView,PostDeleteView
from pt_kokushi.views.post_views import CommentDeleteView,add_comment_to_post
from pt_kokushi.views.timetable_views import create_timetable,timetable_list,delete_timetable,update_timetable
from pt_kokushi.views.quiz_views import quiz,initialize_quiz,quiz_page,quiz_results,select_field
from pt_kokushi.views.quiz_views import submit_answer,select_subfield,select_sub2field,select_sub2field_template
from pt_kokushi.views.quiz_views import reset_quiz_count,all_users_quiz_results,weekly_ranking_view
from pt_kokushi.views.quiz_views import reset_quiz_session_for_sub2field,quiz_page_for_sub2field
from pt_kokushi.views.studychart_views import save_study_log,study_log_data,studychart,study_log_form
from pt_kokushi.views.studychart_views import study_content
from pt_kokushi.views.kokushi_views import exam_selection_view,time_setting_view,quiz_questions_view,submit_quiz_answers
from pt_kokushi.views.kokushi_views import continue_quiz_view,restart_kokushi_quiz_view,exit_quiz, kokushi_results_view
from pt_kokushi.views.kokushi_views import add_bookmark,remove_bookmark,bookmark_list,question_detail,check_answer
from pt_kokushi.views.kokushi_views import start_kokushi_quiz, quiz_page,quiz_question_list,calculate_questions_accuracy
from pt_kokushi.views.random_views import random_question_display, random_quiz,submit_random_quiz_answers,quiz_question_detail
from pt_kokushi.views.random_views import random_quiz_result
from pt_kokushi.views.practical_views import PracticalChoiceView,PracticalQuizView,toggle_bookmark,practical_quiz_result
from pt_kokushi.views.practical_views import clear_quiz_session
from pt_kokushi.views.field_views import field_choice,field_quiz,field_quiz_answer,field_quiz_result

app_name = 'pt_kokushi'

urlpatterns = [
    path('top/', views_org.TopView.as_view(), name='top_view'),
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
    path('update-test-year/', update_test_year, name='update_test_year'),
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
    path('studychart/', studychart, name='studychart'),
    path('save_study_log/', save_study_log, name='save_study_log'),#学習チャート記録用
    path('study-log-data/', study_log_data, name='study_log_data'),#API用の学習チャート関数
    path('study_content/',study_content, name='study_content'),
    path('study-log-form/', study_log_form, name='study_log_form'),
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
    path('top/', exam_selection_view, name='top'),#国試年度選択用
    path('timer/', time_setting_view, name='timer'),#国試試験時間,
    path('quiz_questions/', quiz_questions_view, name='quiz_questions'),  # 質問一覧または最初の質問
    path('quiz_questions/<int:question_id>/', quiz_questions_view, name='quiz_questions_detail'),  # 特定の質問ID
    path('quiz/<int:question_id>/submit_quiz/', submit_quiz_answers, name='submit_quiz_answers'),
    path('quiz_questions/continue/', continue_quiz_view, name='continue_quiz'),#前回の続きから
    path('quiz_questions/start/', restart_kokushi_quiz_view, name='restart_kokushi_quiz'),#最初から解き直す
    path('quiz_question/exit/', exit_quiz, name='exit_quiz'),
    path('quiz_question/kokushi_results/', kokushi_results_view, name='kokushi_results'),#国試成績
    path('quiz_question/<int:question_id>/add_bookmark/', add_bookmark, name='add_bookmark'),
    path('quiz_question/<int:question_id>/remove_bookmark/', remove_bookmark, name='remove_bookmark'),
    path('quiz_question/bookmarks/', bookmark_list, name='bookmark_list'),
    path('question/<int:question_id>/', question_detail, name='question_detail'),
    path('quiz_question/check_answer/<int:question_id>/', check_answer, name='check_answer'),
    path('start-quiz/', start_kokushi_quiz, name='start_quiz'),  # クイズを開始するためのURL
    path('quiz/',quiz_page, name='quiz_page'),  # クイズページのURL
    path('quiz_questions/list/', quiz_question_list, name='quiz_question_list'),  # 問題一覧ページへのURL
    path('calculate_questions_accuracy/',calculate_questions_accuracy, name='calculate_questions_accuracy'),
    path('random/quiz/', random_quiz, name='random_quiz'),
    path('random/question/', random_question_display, name='random_question_display'),#ランダム問題表示
    path('random/quiz/', random_quiz, name='random_choice'),#ランダム問題選択
    path('random/submit/<int:question_id>/', submit_random_quiz_answers, name='submit_random_quiz_answers'),
    path('random/result/', random_quiz_result, name='random_quiz_result'), #ランダム成績表
    path('quiz/question/<int:question_id>/', quiz_question_detail, name='quiz_question_detail'),
    path('practical/choice/', PracticalChoiceView.as_view(), name='practical_choice'),#3点問題選択
    path('practical/quiz/<int:question_id>/', PracticalQuizView.as_view(), name='practical_quiz'),#３点問題の問題表示
    path('practical-quiz-result/', practical_quiz_result, name='practical_quiz_result'),#3点問題成績用
    path('clear-quiz-session/', clear_quiz_session, name='clear_quiz_session'),
    path('toggle_bookmark/', toggle_bookmark, name='toggle_bookmark'),
    path('field_choice/', field_choice, name='field_choice'),#分野選択
    path('field_quiz/<int:field_id>/<int:question_id>/', field_quiz, name='field_quiz'),
    path('field_quiz/<int:field_id>/', field_quiz, name='field_quiz'),  # 分野ごとの問題
    path('field_quiz/<int:field_id>/<int:question_id>/answer/', field_quiz_answer, name='field_quiz_answer'),
    path('field_quiz_result/<int:field_id>/', field_quiz_result, name='field_quiz_result'),

]

if settings.DEBUG:
     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)