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
    
        #**extra_fieldsによりemail,passwordフィールド以外のフィールドが辞書で格納される
        #**extra_fieldはemail,password以外のフィールドとも捉えられる
    def _create_user(self, username, email, password, **extra_fields):
        
        #raiseは意図的に例外を発生させる機能（例外処理）
        #usernameがない場合はエラー
        if not username:
            raise ValueError ('名前が必要ようです')
        
        #emailがない場合はエラー
        elif not email:
            raise ValueError("メールアドレスが必要です")
        
        #self.normalizeによりemailの@以下が正規化される（小文字にする）
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        
        #make_password()関数によりpassword引数に渡された値はハッシュ化（暗号化）される
        user.password = make_password(password)
        
        #user/save()でデータベースへの保存を表す
        #self._dbでsettings.pyでDATABASEとして定義されたDBへ保存する
        user.save(using=self._db)
        
        # user.save(using=self._db)
        return user
    
    #views.pyのsignup_viewで使ってる
    def create_user(self, email=None, password=None, **extra_fields):
        
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
    
    #名前が重複しないか確認するusernameで使ってる
    username_validator = UnicodeUsernameValidator()
    
    #モデルフィールドの設定（テーブル定義を行うところ）
    username = models.CharField(
        verbose_name='名前', #verbose_nameで管理画面での表示が変わる
        max_length=20, 
        unique=True, #ユニーク制約（重複しないようにすること）を解除
        validators = [username_validator],
        error_messages={
            "unique": _("その名前はすでに使われています"),
        },)
        
    email = models.EmailField(
        _("email address"),#_("")は多言語対応のためのマーク付け
        unique=True,
        blank=False
        )
    
    date_of_birth = models.DateField(
        verbose_name="誕生日", #verbose_nameで管理画面での表示が変わる
        blank=True, 
        null=True
        )
    
    school_year = models.IntegerField(
        verbose_name="学年",
        blank = True
        )
    
    prefecture = models.CharField(
        _('都道府県'), #_("")は多言語対応のためのマーク付け
        max_length=5, 
        blank=True, 
        null=True
        )
    
    #アクティブユーザー（一回以上利用があったユーザーのこと)
    is_active = models.BooleanField(
        default=True
        )
    #登録日のこと
    date_joined = models.DateTimeField(
        verbose_name="登録日",
        auto_now_add=True, #DBにインサート（追加挿入）するたびに更新
        null=True,
        blank=True
        )
    #誕生日から年齢を計算
    def get_age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    
    #Boolean=真偽値
    is_staff = models.BooleanField(
        _("staff status"),
        #default(初期値)の設定。この場合初期値は「False」
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    
    
    #ユーザーモデルの情報を参照する
    #プログラムが扱うデータは全てobjectsと言える
    objects = UserManager()

    EMAIL_FIELD = "email"
    
    #usernameを使って認証するということ
    #ログインをemailとpasswordのみに変更すると"email"でも設定できるようになる
    USERNAME_FIELD = "username"
    
    #登録画面の入力の項目（ユーザー名とパスワードは自動で存在する.入れたらエラーになる）
    REQUIRED_FIELDS = ['email','date_of_birth','school_year','prefecture','is_active','date_joined']

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


#ユーザーの新規登録と同期して、登録されたユーザーにひもづくProfileレコードが挿入される
class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    gender = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=30, blank=True)
    favorite_words = models.CharField(max_length=50, blank=True)

#recieverというモジュールとpost_saveというモジュールを使う    
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
