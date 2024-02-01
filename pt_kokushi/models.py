from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.contrib import auth
from django.core.exceptions import ValidationError
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, RegexValidator
from django.core.mail import send_mail
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from datetime import date ,datetime
from django.utils import timezone
import math

#Usermmanagerはコピペで不用意な部分を削除や追加して使う
class UserManager(BaseUserManager):
    
    #今回設定するクラスを設定するための設定
    use_in_migrations = True
        
        #--------ここから通常ユーザーを作成--------
        #**extra_fieldsによりemail,passwordフィールド以外のフィールドが辞書で格納される
        #**extra_fieldはemail,password以外のフィールドとも捉えられる
    def _create_user(self, email, password, **extra_fields):
        
        #raiseは意図的に例外を発生させる機能（例外処理）
        #emailがない場合はエラー
        if not email:
            raise ValueError("メールアドレスが必要です")
        
        #self.normalizeによりemailの@以下が正規化される（小文字にする）
        user = self.model(
            email = self.normalize_email(email), **extra_fields
        )
        
        #make_password()関数によりpassword引数に渡された値はハッシュ化（暗号化）される
        user.password = make_password(password)
        
        #user/save()でデータベースへの保存を表す
        #self._dbでsettings.pyでDATABASEとして定義されたDBへ保存する
        user.save(using=self._db)
        
        # user.save(using=self._db)
        return user
    
    #views.pyのsignup_viewで使ってる
    def create_user(self, email, password=None, **extra_fields):
        
        #setdefault()メソッドでは「第一引数：key（キー）,第二引数：value（値）」を指定する
        #新規ユーザーが登録された場合のみ登録されるメソッドでスタッフとスーパーユーザーにはならないようにしている
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        
        #setdefaultでの返り値として
        return self._create_user(email, password, **extra_fields)
    
    #create_superuserの記述がないとスーパーユーザーで管理画面にログインできない
    def create_superuser(self, email=None, password=None, **extra_fields):
        
        #管理画面にログインできるユーザーの条件が以下の２つ
        #スーパーユーザーはis_staffとis_superuserがTrueになるように設定してある
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    def with_perm(
        self, perm, is_active=True, include_superusers=True, backend=None, obj=None
    ):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    "You have multiple authentication backends configured and "
                    "therefore must provide the `backend` argument."
                )
        elif not isinstance(backend, str):
            raise TypeError(
                "backend must be a dotted import path string (got %r)." % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, "with_perm"):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()
    
def generate_test_year_choices():
    current_year = datetime.now().year
    return [(str(current_year + i), f"{current_year + i}年度") for i in range(5)]

 
#ここに追加したいフィールドやメソッドを追加する
class CustomUser(AbstractBaseUser, PermissionsMixin):
      
    #モデルフィールドの設定（テーブル定義を行うところ）(使いたいフィールドを追加)
    nickname = models.CharField(
        verbose_name = 'ニックネーム', #verbose_nameで管理画面での表示が変わる
        max_length = 20,
        )
        
    email = models.EmailField(
        _("email address"),#_("")は多言語対応のためのマーク付け
        unique = True,
        blank = False
        )
    
    birth_of_date = models.DateField(
        verbose_name = "誕生日", #verbose_nameで管理画面での表示が変わる
        blank = True, 
        null = True
        )
    
    school_year = models.IntegerField(
        verbose_name = "学年",
        blank = True,
        null = True,
        )
    
    prefecture = models.CharField(
        _('都道府県'), #_("")は多言語対応のためのマーク付け
        max_length = 10, 
        blank = True, 
        null = True
        )
    #アクティブユーザー（一回以上利用があったユーザーのこと)
    is_active = models.BooleanField(
        default=True
        )
    
    #登録日のこと
    date_joined = models.DateTimeField( 
        verbose_name = "登録日",
        default=timezone.now
        )
    
    #誕生日から年齢を計算
    def get_age(self):
        if self.birth_of_date:
            today = date.today()
            return today.year - self.birth_of_date.year - ((today.month, today.day) < (self.birth_of_date.month, self.birth_of_date.day))
        return None
    
    #Boolean=真偽値
    is_staff = models.BooleanField(
        _("staff status"),
        #default(初期値)の設定。この場合初期値は「False」
        default = False,
        help_text = _("管理サイトへのログインの権利を判断します"),
    )
    
    gender = models.CharField(
        max_length = 20, 
        blank = True
        )
    
    TEST_YEAR_CHOICES = generate_test_year_choices()

    test_year = models.CharField(
        verbose_name='国試受験年度',
        max_length=10,
        choices=TEST_YEAR_CHOICES,
        blank=False,
        null=False
    )
    def get_remaining_time(self, test_dates):
        if self.test_year and self.test_year in test_dates:
            test_date = datetime.strptime(test_dates[self.test_year], "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            remaining_time = test_date - now
            return remaining_time
        return None
    
    #ユーザーモデルの情報を参照する
    #プログラムが扱うデータは全てobjectsと言える（UserManagerとUserを紐付けしている)
    objects = UserManager()

    EMAIL_FIELD = "email"
    
    #usernameを使って認証するということ。ユニークである必要がある
    #ログインをemailとpasswordのみに変更すると"email"でも設定できるようになる
    USERNAME_FIELD = "email"
    
    #登録画面の入力の項目（ユーザー名とパスワードは自動で存在する.入れたらエラーになる）
    REQUIRED_FIELDS = ['birth_of_date','school_year','prefecture','is_active','date_joined','gender',]

    #ModelFormやUserCreationFormを実装するときに使用する
    #このクラスを使うことでモデルのフィールフィールドを自動で共有することができる
    class Meta:
        #verbose_nameは、Metaクラス内で定義する
        verbose_name = _("user")
        #_pluralだと複数形にした時の名前を指定する
        verbose_name_plural = _("users")
        #abstract = True

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)
    
    def get(self, some_argument):
        pass
    
#掲示板機能用のmodels.py    
class Post(models.Model):
    title = models.CharField(max_length=100, verbose_name="タイトル")
    content = models.TextField(verbose_name="内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="投稿日時")
    nickname = models.CharField(max_length=20, verbose_name="ニックネーム",blank=True)
    last_commented_at = models.DateTimeField(auto_now=True, verbose_name="最終コメント日時")
    ordering = ['-last_commented_at']
    view_count = models.PositiveIntegerField(default=0, verbose_name="ビュー数")

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-last_commented_at']

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name="対応する投稿")
    content = models.TextField(verbose_name="コメント内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="コメント日時")
    nickname = models.CharField(max_length=20, verbose_name="ニックネーム",blank=True) 

    def __str__(self):
        return f"{self.author} - {self.post}"
    

#ToDoリストのmodels.py
class ToDoItem(models.Model):
    # 優先度を表す選択肢
    PRIORITY_CHOICES = [
        (1, '低'),
        (2, '中'),
        (3, '高'),
    ]

    title = models.CharField(max_length=100, verbose_name="タイトル")
    content = models.TextField(verbose_name="内容")
    purpose = models.TextField(verbose_name="目的", blank=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2, verbose_name="優先度")
    deadline = models.DateField(verbose_name="期限", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-priority', '-created_at']  # 優先度が高く、作成日が新しい順に並べる

#カレンダー機能用のmodels.py
class Event(models.Model):
    title = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    user_email = models.EmailField()  # ユーザーのemailを直接保存

    def __str__(self):
        return self.title
    
#時間割表用models.py
class TimeTable(models.Model):
    DAY_CHOICES = [
        ('月', '月曜日'),
        ('火', '火曜日'),
        ('水', '水曜日'),
        ('木', '木曜日'),
        ('金', '金曜日'),
    ]
    PERIOD_CHOICES = [
        (1, '1限'),
        (2, '2限'),
        (3, '3限'),
        (4, '4限'),
        (5, '5限'),
        (6, '6限'),
    ]

    day = models.CharField(max_length=2, choices=DAY_CHOICES)
    period = models.IntegerField(choices=PERIOD_CHOICES)
    subject = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.get_day_display()} - {self.get_period_display()} - {self.subject}"
    
#4択問題用のmodels.py
#基礎学習分野選択ページ
class Field(models.Model):
    name = models.CharField(max_length=100, verbose_name="分野名")
    description = models.TextField(verbose_name="説明")
    icon = models.ImageField(upload_to='field_icons/', blank=True, null=True, verbose_name="アイコン")

    def __str__(self):
        return self.name

class Subfield(models.Model):
    has_detailed_selection = models.BooleanField(default=False, verbose_name='さらに詳細な分野選択を可能にする')
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name="分野名")
    description = models.TextField(verbose_name="説明")
    icon = models.ImageField(upload_to='subfield_icons/', blank=True, null=True, verbose_name="アイコン")

    def __str__(self):
        return self.name
    
class Sub2field(models.Model):
    subfield = models.ForeignKey(Subfield, on_delete=models.CASCADE, related_name='sub2fields')
    has_detailed_selection = models.BooleanField(default=False, verbose_name='さらに詳細な分野選択')
    name = models.CharField(max_length=100, verbose_name="分野名")
    description = models.TextField(verbose_name="説明")
    icon = models.ImageField(upload_to='subfield_icons/', blank=True, null=True, verbose_name="アイコン")
    
    def __str__(self):
        return self.name
    
class Question(models.Model):
    
    question_text = models.TextField()
    field = models.ForeignKey(Field, on_delete=models.SET_NULL, null=True, blank=True, related_name='questions')
    subfield = models.ForeignKey(Subfield, on_delete=models.SET_NULL, null=True, blank=True, related_name='questions')
    sub2field = models.ForeignKey(Sub2field, on_delete=models.SET_NULL, null=True, blank=True, related_name='questions')
    score = models.IntegerField(default=1) 
    choice1 = models.CharField(max_length=200)  # 選択肢1
    choice2 = models.CharField(max_length=200)  # 選択肢2
    choice3 = models.CharField(max_length=200)  # 選択肢3
    choice4 = models.CharField(max_length=200)  # 選択肢4
    
    correct_answer = models.CharField(max_length=1, choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')])
    
    def __str__(self):
        return self.question_text
    
    def save(self, *args, **kwargs):
        # subfield と sub2field の整合性をチェック
        if self.sub2field and self.subfield != self.sub2field.subfield:
            raise ValidationError("選択した sub2field は選択した subfield に属していません。")

        super().save(*args, **kwargs)
    
# ユーザーの回答を記録するモデル
class UserAnswer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=1, choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')])
    timestamp = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Answer: {self.question.question_text}"


# ユーザーのスコアを記録するモデル
class UserScore(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_score = models.IntegerField(default=0)
    total_questions_attempted = models.IntegerField(default=0)
    total_correct_answers = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Score: {self.total_score}"

    def update_score(self, question, selected_answer):
        # ユーザーの回答と正解を比較してスコアを更新するメソッドを追加できます
        if selected_answer == question.correct_answer:
            self.total_correct_answers += 1
            self.total_score += 1
        self.total_questions_attempted += 1
        self.save()
        