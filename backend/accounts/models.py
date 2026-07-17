from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', User.Role.MEMBER)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', User.Role.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrator'
        MEMBER = 'MEMBER', 'Member'

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    is_suspended = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=32, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ['email']

    def __str__(self):
        return self.email

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip() or self.email


class MemberInterest(models.Model):
    """Genres/authors a member has declared interest in — feeds recommendations."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interests')
    genre = models.ForeignKey('catalog.Genre', on_delete=models.CASCADE, null=True, blank=True, related_name='+')
    author = models.ForeignKey('catalog.Author', on_delete=models.CASCADE, null=True, blank=True, related_name='+')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'genre'], name='unique_user_genre_interest'),
            models.UniqueConstraint(fields=['user', 'author'], name='unique_user_author_interest'),
        ]

    def __str__(self):
        target = self.genre or self.author
        return f'{self.user.email} interested in {target}'