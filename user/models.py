from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.is_active = True 
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):  # ✅ PermissionsMixin 꼭 추가!
    AR_STATE = [
        (0, "카카오"),
        (1, "페이스북"),
        (2, "구글")
    ]

    id = models.AutoField(primary_key=True)
    email = models.CharField('이메일', unique=True, max_length=50)
    password = models.CharField('비밀번호', max_length=200)
    name = models.CharField('이름', max_length=50, null=True, blank=True)
    log_method = models.IntegerField(choices=AR_STATE, default=0, null=True, blank=True)
    tel_first = models.CharField('연락처', max_length=20, null=True, blank=True)
    sign_in = models.DateTimeField('회원가입일', auto_now_add=True, null=True, blank=True)
    last_login = models.DateTimeField('로그인', auto_now=True, null=True, blank=True)

    # ✅ 관리자 권한 필수 필드
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # admin site 접근 여부

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email
