import os
import django

# Djangoプロジェクトのsettingsモジュールを指定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pt_project2.settings')

# Django環境をセットアップ
django.setup()

# ここからDjangoのモデルやその他の機能を利用できます
from pt_kokushi.models.question_models import QuizSession
from pt_kokushi.models import QuizSession, Question

# モデルを操作するコードなど
questions = QuizSession.objects.all()

def initialize_quiz(request):
    if request.method == 'POST':
        print("Before reset:", request.session.get('current_quiz_correct_answers', 'Not set'))  # リセット前の値をログ出力
        request.session['current_quiz_correct_answers'] = 0
        request.session['current_question_index'] = 0
        request.session.modified = True
        print("After reset:", request.session['current_quiz_correct_answers'])  # リセット後の値をログ出力
        
        subfield_id = request.POST.get('subfield_id', None)
        sub2field_id = request.POST.get('sub2field_id', None)