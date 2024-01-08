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
    email = forms.CharField(widget=forms.EmailInput)
    
    password = forms.CharField(widget=forms.PasswordInput)
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
    
    school_year = forms.ChoiceField(label='学年',
                                     choices = [
                                     ('1','1年生'),
                                     ('2','2年生'),
                                     ('3','3年生'),
                                     ('4','4年生'),
                                     ('5','卒業生'),
                                     ('6','その他')
                                     ])
    prefecture = forms.ChoiceField(label='都道府県',
                                 choices = [
                                    ("北海道"  ,"北海道"  ),  
                                    ("青森県"  ,"青森県"  ),  
                                    ("岩手県"  ,"岩手県"  ),  
                                    ("宮城県"  ,"宮城県"  ),  
                                    ("秋田県"  ,"秋田県"  ),  
                                    ("山形県"  ,"山形県"  ),  
                                    ("福島県"  ,"福島県"  ),  
                                    ("茨城県"  ,"茨城県"  ),  
                                    ("栃木県"  ,"栃木県"  ),  
                                    ("群馬県"  ,"群馬県"  ),  
                                    ("埼玉県"  ,"埼玉県"  ),  
                                    ("千葉県"  ,"千葉県"  ),  
                                    ("東京都"  ,"東京都"  ),  
                                    ("神奈川県","神奈川県" ),
                                    ("新潟県"  ,"新潟県"  ),  
                                    ("富山県"  ,"富山県"  ),  
                                    ("石川県"  ,"石川県"  ),  
                                    ("福井県"  ,"福井県"  ),  
                                    ("山梨県"  ,"山梨県"  ),  
                                    ("長野県"  ,"長野県"  ),  
                                    ("岐阜県"  ,"岐阜県"  ),  
                                    ("静岡県"  ,"静岡県"  ),  
                                    ("愛知県"  ,"愛知県"  ),  
                                    ("三重県"  ,"三重県"  ),  
                                    ("滋賀県"  ,"滋賀県"  ),  
                                    ("京都府"  ,"京都府"  ),  
                                    ("大阪府"  ,"大阪府"  ),  
                                    ("兵庫県"  ,"兵庫県"  ),  
                                    ("奈良県"  ,"奈良県"  ),  
                                    ("和歌山県","和歌山県"),
                                    ("鳥取県"  ,"鳥取県"  ),  
                                    ("島根県"  ,"島根県"  ),  
                                    ("岡山県"  ,"岡山県"  ),  
                                    ("広島県"  ,"広島県"  ),  
                                    ("山口県"  ,"山口県"  ),  
                                    ("徳島県"  ,"徳島県"  ),  
                                    ("香川県"  ,"香川県"  ),  
                                    ("愛媛県"  ,"愛媛県"  ),  
                                    ("高知県"  ,"高知県"  ),  
                                    ("福岡県"  ,"福岡県"  ),  
                                    ("佐賀県"  ,"佐賀県"  ),  
                                    ("長崎県"  ,"長崎県"  ),  
                                    ("熊本県"  ,"熊本県"  ),  
                                    ("大分県"  ,"大分県"  ),  
                                    ("宮崎県"  ,"宮崎県"  ),  
                                    ("鹿児島県","鹿児島県"),
                                    ("沖縄県"  ,"沖縄県"  ),    
                                 ],
                                 initial ="東京都"
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
        fields = ('username', 'email', 'password','password2', 'school_year','prefecture','gender','birth_year', 'birth_month', 'birth_day')

class LoginForm(AuthenticationForm):
    pass