# account/serializers.py
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, UserProfile
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import WheelchairRelation
from wheelchair.models import WheelchairType, WheelchairDriveType, WheelchairTireMaterial
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.exceptions import NotFound


class CustomTokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(write_only=True)

    def validate(self, attrs):
        refresh_token = attrs.get('refresh_token')
        if not refresh_token:
            raise serializers.ValidationError({'refresh_token': 'This field is required.'})

        try:
            refresh = RefreshToken(refresh_token)
            access = refresh.access_token
        except TokenError as e:
            raise InvalidToken(str(e))

        return {
            'refresh': str(refresh),
            'access': str(access),
        }

# For Login
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        user = authenticate(request=self.context.get('request'), email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password")
        if not user.is_active:
            raise serializers.ValidationError("This account is inactive")

        data["user"] = user
        return data

#  User Signup/Register
class RegisterSerializer(serializers.ModelSerializer):
    # Add profile fields here
    password = serializers.CharField(write_only=True)
    terms_condition = serializers.BooleanField(write_only=True)

    height = serializers.CharField(write_only=True, required=False, allow_blank=True)
    weight = serializers.CharField(write_only=True, required=False, allow_blank=True)
    gender = serializers.CharField(write_only=True, required=False, allow_blank=True)
    age = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            'email', 'name', 'password', 'terms_condition',
            'height', 'weight', 'gender', 'age'
        )

    def create(self, validated_data):
        # Extract profile fields
        profile_data = {
            'height': validated_data.pop('height', ''),
            'weight': validated_data.pop('weight', ''),
            'gender': validated_data.pop('gender', ''),
            'age': validated_data.pop('age', ''),
        }
        validated_data['terms_accepted'] = validated_data.pop('terms_condition', True)

        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        # Create user profile
        UserProfile.objects.create(
            user=user,
            **profile_data
        )

        return user

# For User Profile
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['height', 'weight', 'gender', 'age']


class UserDetailSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'name', 'profile']

    def get_profile(self, obj):
        try:
            profile = obj.userprofile  # Access related UserProfile
        except UserProfile.DoesNotExist:
            raise NotFound(detail="User profile not found.")

        return UserProfileSerializer(profile).data

class UpdateUserProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name', required=False)

    class Meta:
        model = UserProfile
        fields = ['name', 'height', 'weight', 'gender', 'age']

    def update(self, instance, validated_data):
        # Extract and update user.name
        user_data = validated_data.pop('user', {})
        if 'name' in user_data:
            instance.user.name = user_data['name']
            instance.user.save()

        # Update profile fields
        return super().update(instance, validated_data)


# For Change Password
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value

class WheelchairTypeSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WheelchairType
        fields = ['id', 'name']

class WheelchairDriveTypeSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WheelchairDriveType
        fields = ['id', 'name']

class WheelchairTireMaterialSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WheelchairTireMaterial
        fields = ['id', 'name']

class WheelchairRelationSerializer(serializers.ModelSerializer):
    # Write-only fields for create/update
    wheelchair_type_id = serializers.PrimaryKeyRelatedField(
        source='wheelchair_type',
        queryset=WheelchairType.objects.all(),
        write_only=True
    )
    wheelchair_drive_type_id = serializers.PrimaryKeyRelatedField(
        source='wheelchair_drive_type',
        queryset=WheelchairDriveType.objects.all(),
        write_only=True
    )
    wheelchair_tire_material_id = serializers.PrimaryKeyRelatedField(
        source='wheelchair_tire_material',
        queryset=WheelchairTireMaterial.objects.all(),
        write_only=True
    )

    # Read-only nested fields
    wheelchair_type = WheelchairTypeSimpleSerializer(read_only=True)
    wheelchair_drive_type = WheelchairDriveTypeSimpleSerializer(read_only=True)
    wheelchair_tire_material = WheelchairTireMaterialSimpleSerializer(read_only=True)

    class Meta:
        model = WheelchairRelation
        fields = [
            'id', 'identifier', 'wheel_number',
            'wheelchair_type_id', 'wheelchair_drive_type_id', 'wheelchair_tire_material_id',  # for input
            'wheelchair_type', 'wheelchair_drive_type', 'wheelchair_tire_material',  # for output
            'height', 'width', 'status', 'is_default'
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        is_default = validated_data.get('is_default', False)

        # Set as default if user has no default yet
        has_default = WheelchairRelation.objects.filter(user=user, is_default=True).exists()
        if not has_default:
            validated_data['is_default'] = True
        elif is_default:
            WheelchairRelation.objects.filter(user=user, is_default=True).update(is_default=False)

        return WheelchairRelation.objects.create(**validated_data)  # Do not include `user=user`

    def update(self, instance, validated_data):
        user = self.context['request'].user
        new_is_default = validated_data.get('is_default', instance.is_default)

        if new_is_default and not instance.is_default:
            WheelchairRelation.objects.filter(user=user, is_default=True).exclude(id=instance.id).update(is_default=False)

        if not new_is_default and instance.is_default:
            has_other_default = WheelchairRelation.objects.filter(user=user, is_default=True).exclude(id=instance.id).exists()
            if not has_other_default:
                validated_data['is_default'] = True

        return super().update(instance, validated_data)

    def validate(self, attrs):
        user = self.context['request'].user
        identifier = attrs.get('identifier')

        # If this is an update, self.instance will be present
        instance = getattr(self, 'instance', None)

        qs = WheelchairRelation.objects.filter(user=user, identifier=identifier)
        if instance:
            qs = qs.exclude(pk=instance.pk)

        if qs.exists():
            raise serializers.ValidationError({
                "identifier": "You already have a wheelchair with this identifier."
            })

        return attrs
