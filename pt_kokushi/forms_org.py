from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from .models_org import CustomUser
from django.utils import timezone
from datetime import datetime, timedelta
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _

CustomUser = get_user_model()

class CustomUserForm(forms.ModelForm):
    
    #ここの記述がinputタグと同じ役割があると考える()内でplaceholder指定的な記述をする
    nickname = forms.CharField(
        label = 'ニックネーム',
        max_length = 20,
        error_messages = {
            "required": "",
        }
        )
    
    email = forms.CharField(
        label = 'メールアドレス',
        widget = forms.EmailInput,
        )
    
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password 確認用', widget=forms.PasswordInput)
    
    test_year = forms.ChoiceField(
        label='国試受験年度',
        choices=CustomUser.TEST_YEAR_CHOICES,
        required=False
    )

    
    #ChoiceFieldで複数の選択肢から１つを選ぶフィールド
    #テンプレートには以下のように記述する
    #<select name="フィールド名"><option value="choice.key">choice.value</option>...</select>
    CHOICES = (
        ('女性', '女性',),
        ('男性', '男性',),
        ('秘密', '秘密',)
        )
    
    gender =  forms.ChoiceField(
        label = '性別',
        widget = forms.RadioSelect,
        choices = CHOICES, 
        required = False
        )
    
    birth_of_date = forms.DateField(
        input_formats=['%Y-%m-%d', '%d/%m/%Y'],
        label="生年月日",
        initial=datetime.now() - timedelta(days=365 * 20),
        widget=forms.SelectDateWidget(
            years=range(timezone.now().year, 1949, -1),
            empty_label=("Year", "Month", "Day"), 
        )
    )

    
    school_year = forms.ChoiceField(
        label = '学年',
        choices = [
            ('1','1年生'),
            ('2','2年生'),
            ('3','3年生'),
            ('4','4年生'),
            ('5','卒業生'),
            ('6','その他')
            ])
    
    prefecture = forms.ChoiceField(
        label = '都道府県',
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
            initial = "東京都"
            )

    class Meta:
        
        #どのモデルを選択するか
        model = CustomUser
        
        # fieldsにユーザー作成時に必要な情報を指定する
        #{{form}}でテンプレートに表示できる
        fields = ('email','password1', 'password2','nickname','test_year','birth_of_date','prefecture', 'school_year','gender')
           
        def clean_password2(self):
            password1 = self.cleaned_data.get("password1")
            password2 = self.cleaned_data.get("password2")
            if password1 and password2 and password1 != password2:
                raise forms.ValidationError("パスワードが違います")
            return password2

        def save(self, commit=True):
            user = super().save(commit=False)
            user.set_password(self.cleaned_data["password1"])
            if commit:
                user.save()
            return user
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''  # ラベルの末尾に何も表示しないように設定

class CustomLoginForm(forms.Form):
    
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput)

class CustomPasswordChangeForm(forms.Form):
    old_password = forms.CharField(label='古いパスワード', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password = forms.CharField(label='新しいパスワード', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(label='新しいパスワード（確認用）', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data['old_password']
        if not authenticate(username=self.user.email, password=old_password):
            raise ValidationError('古いパスワードが間違っています。')
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        new_password2 = cleaned_data.get('new_password2')

        if new_password and new_password2 and new_password != new_password2:
            self.add_error('new_password2', '新しいパスワードが一致しません。')

        return cleaned_data

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password'])
        if commit:
            self.user.save()
        return self.user

class CustomNicknameChangeForm(forms.Form):
    nickname = forms.CharField(max_length=20, required=True, label='新しいニックネーム')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'     
    
class TestYearForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['test_year']  # ユーザーが変更できるフィールドを指定
        labels = {
            'test_year': '国試受験年度',
        }