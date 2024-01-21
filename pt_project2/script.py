import os
import sys

# 必要に応じてPythonのパスを追加
sys.path.append('/Users/tomosue_shou/pt_project2')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pt_project2.settings')

import django
django.setup()

# その他のDjango関連のコードをここに記述

