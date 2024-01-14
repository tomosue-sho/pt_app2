from django.db import models
from django.contrib import auth
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import PermissionsMixin
from datetime import date
import math
from django.utils import timezone
from django.core.validators import MinLengthValidator, RegexValidator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

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
        max_length = 5, 
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
