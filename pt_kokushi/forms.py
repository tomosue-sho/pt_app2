from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth import get_user_model
from datetime import datetime

CustomUser = get_user_model()

class CustomUserForm(UserCreationForm):
    
    #ここの記述がinputタグと同じ役割があると考える()内でplaceholder指定的な記述をする
    username = forms.CharField()
    email = forms.CharField()
    
    password = forms.CharField(widget=forms.PasswordInput)
    password1 = forms.CharField(required=False)
    password2 = forms.CharField(
              label="確認用パスワード",
              widget=forms.PasswordInput
                )
    
    #ChoiceFieldで複数の選択肢から１つを選ぶフィールド
    #テンプレートには以下のように記述する
    #<select name="フィールド名"><option value="choice.key">choice.value</option>...</select>
    CHOICES = (
        ('female', '女性',),
        ('male', '男性',),
        ('not_applicable', '秘密',)
        )
    
    gender = forms.ChoiceField(
        widget=forms.RadioSelect, #ラジオボタンに設定する
        choices=CHOICES, 
        required=False) #Falseなので入力必須ではない
    
    birth_date = forms.DateField(
               widget=forms.SelectDateWidget
    )
    
    #from_xは日付範囲の開始地点
    #to_yは日付範囲の終了地点
    #datesは日付範囲が格納されるリスト
    #incrementは日付範囲を増加させる可動かを決めるTrueなのでfrom_xからto_yまでのリストをdatesに追加する
    def make_select_object(from_x, to_y, dates, increment=True):
        if increment:
            for i in range(from_x, to_y):
                dates.append([i, i])
        else:
            for i in range(from_x, to_y, -1):
                dates.append([i, i])
        return dates
    
    #Djangoのフォームで使用されるChoiceFieldオブジェクトを生成するためのもの
    #引数select_objectによってmake_select_object関数で生成された日付範囲のリストが渡される
    def make_select_field(select_object):
        
        #forms.ChoiceFieldクラスで新しい日付選択フィールドを作成する（’date_fields’）
        dates_field = forms.ChoiceField(
            widget=forms.Select,
            choices=select_object,
            required=False
        )
        return dates_field
    #まずmake_select_object 関数を使用して日付範囲のリストを生成し
    #その後 make_select_field 関数にそのリストを渡して、Djangoのフォームで使用できる日付選択フィールドを作成する。

    #年の選択フィールド
    years = [["",""]]
    current_year = datetime.now().year #現在の年
    years = make_select_object(current_year, current_year-80, years, increment=False)
    birth_year = make_select_field(years)

    #月の選択フィールド
    months = [["",""]]
    months = make_select_object(1, 13, months)
    birth_month = make_select_field(months)
    
    #日の選択フィールド
    days = [["",""]]
    days = make_select_object(1, 32, days)
    birth_day = make_select_field(days)
    

    class Meta:
        
        #どのモデルを選択するか
        model = CustomUser
        
        # fieldsにユーザー作成時に必要な情報を指定する
        #{{form}}でテンプレートに表示できる
        fields = ('username', 'email', 'password','password2', 'gender','birth_year', 'birth_month', 'birth_day')

class LoginForm(AuthenticationForm):
    pass