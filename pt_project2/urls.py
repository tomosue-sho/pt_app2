"""
URL configuration for pt_project2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path ,include
from pt_kokushi import views_org
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from pt_kokushi.views.studychart_views import studychart_view,save_study_log,study_date,study_log_data

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views_org.TopView.as_view(), name="top"),
    path('login_app/', include('pt_kokushi.urls')),
    path('login_app/studychart/', include([
        path('studychart/', studychart_view, name='studychart'),#学習チャート
        path('save_study_log/', save_study_log, name='save_study_log'),#学習チャート記録用
        path('study_date/', study_date, name='study_date'),  #学習チャートの日付選択用
        path('study-log-data/', study_log_data, name='study_log_data')
        ])),
]

