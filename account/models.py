from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from wheelchair.models import WheelchairType, WheelchairDriveType, WheelchairTireMaterial
from django.utils import timezone
import random
import string


# ======================
# Custom User Manager
# ======================
from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "user")
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault("role", "superadmin")
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("role") != "superadmin":
            raise ValueError("Superuser must have role='superadmin'.")

        return self.create_user(email, name, password, **extra_fields)

# ======================
# User Model
# ======================
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('superadmin', 'Super Admin'),
        ('admin', 'Admin'),
        ('user', 'User'),
    ]

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    com_number = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    terms_accepted = models.BooleanField(default=True)
    is_email_verified = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]


    def __str__(self):
        return self.email

    class Meta:
        db_table = "account_user"
        verbose_name = "User"
        verbose_name_plural = "Users"

# ======================
# User Profile Model
# ======================
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    height = models.CharField(max_length=20, blank=True)
    weight = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    age = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.email if self.user else 'Unknown'}"

    class Meta:
        db_table = "account_profile"
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

class PasswordResetCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_used and (timezone.now() - self.created_at).seconds < 600  # 10 mins

    @staticmethod
    def generate_code():
        return ''.join(random.choices(string.digits, k=6))

# ======================
# User and WheelChair Relations
# ======================
class WheelchairRelation(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    identifier = models.CharField(max_length=30, default='temp-id')
    wheel_number = models.IntegerField()
    wheelchair_type = models.ForeignKey(WheelchairType, on_delete=models.SET_NULL, null=True, related_name='WheelchairType')
    wheelchair_drive_type = models.ForeignKey(WheelchairDriveType, on_delete=models.SET_NULL, null=True, related_name='WheelchairDriveType')
    wheelchair_tire_material = models.ForeignKey(WheelchairTireMaterial, on_delete=models.SET_NULL, null=True, related_name='WheelchairTireMaterial')
    height = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    width = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} ({'Default' if self.is_default else 'Optional'})"

    class Meta:
        db_table = "account_wheelchair_relation"
        verbose_name = "WheelchairRelation"
        verbose_name_plural = "WheelchairRelations"
        unique_together = ('user', 'identifier')  # ✅ Enforce uniqueness per user


