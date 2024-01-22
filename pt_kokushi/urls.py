from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
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
  ]

