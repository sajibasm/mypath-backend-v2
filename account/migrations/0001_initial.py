# Generated by Django 4.2.9 on 2025-05-22 18:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("wheelchair", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("name", models.CharField(max_length=100)),
                ("com_number", models.CharField(max_length=100)),
                ("is_active", models.BooleanField(default=True)),
                ("is_staff", models.BooleanField(default=False)),
                ("is_superuser", models.BooleanField(default=False)),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("superadmin", "Super Admin"),
                            ("admin", "Admin"),
                            ("user", "User"),
                        ],
                        default="user",
                        max_length=20,
                    ),
                ),
                ("terms_accepted", models.BooleanField(default=True)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "User",
                "verbose_name_plural": "Users",
                "db_table": "account_user",
            },
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("height", models.CharField(blank=True, max_length=20)),
                ("weight", models.CharField(blank=True, max_length=20)),
                ("gender", models.CharField(blank=True, max_length=20)),
                ("age", models.CharField(blank=True, max_length=20, null=True)),
                (
                    "user",
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "User Profile",
                "verbose_name_plural": "User Profiles",
                "db_table": "account_profile",
            },
        ),
        migrations.CreateModel(
            name="WheelchairRelation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("identifier", models.CharField(default="temp-id", max_length=30)),
                ("wheel_number", models.IntegerField()),
                (
                    "height",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
                ),
                (
                    "width",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("active", "Active"), ("inactive", "Inactive")],
                        db_index=True,
                        default="active",
                        max_length=10,
                    ),
                ),
                ("is_default", models.BooleanField(default=False)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "wheelchair_drive_type",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="WheelchairDriveType",
                        to="wheelchair.wheelchairdrivetype",
                    ),
                ),
                (
                    "wheelchair_tire_material",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="WheelchairTireMaterial",
                        to="wheelchair.wheelchairtirematerial",
                    ),
                ),
                (
                    "wheelchair_type",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="WheelchairType",
                        to="wheelchair.wheelchairtype",
                    ),
                ),
            ],
            options={
                "verbose_name": "WheelchairRelation",
                "verbose_name_plural": "WheelchairRelations",
                "db_table": "account_wheelchair_relation",
                "unique_together": {("user", "identifier")},
            },
        ),
    ]
