from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, WheelchairRelation

# ======================
# Custom User Admin
# ======================
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'name', 'com_number', 'role', 'is_active','is_email_verified', 'is_superuser')
    # list_filter = ('role', 'is_active')
    search_fields = ('email', 'name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'com_number', 'role', 'terms_accepted')}),
        ('Access', {'fields': ('is_active',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'com_number', 'role', 'terms_accepted', 'password1', 'password2'),
        }),
    )

# ======================
# UserProfile Admin
# ======================
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'height', 'weight', 'gender', 'age')
    search_fields = ('user__email', 'gender')
    # list_filter = ('gender',)

# ======================
# WheelchairRelation Admin
# ======================
class WheelchairRelationAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'identifier', 'wheel_number',
        'wheelchair_type', 'wheelchair_drive_type', 'wheelchair_tire_material',
        'height', 'width', 'status', 'is_default'
    )
    search_fields = ('user__email', 'identifier')
    # list_filter = ('status', 'is_default', 'wheelchair_type', 'wheelchair_drive_type')


# ======================
# Register models
# ======================
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(WheelchairRelation, WheelchairRelationAdmin)
