# account/views.py
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenRefreshView

from .models import WheelchairRelation, UserProfile
from .serializers import WheelchairRelationSerializer, CustomTokenRefreshSerializer, UpdateUserProfileSerializer

from account.models import User

from django.utils import timezone
from django.conf import settings
from datetime import datetime

User = get_user_model()

from .tasks import (
    send_welcome_email,
    send_email_verification_link
)

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserDetailSerializer,
    ChangePasswordSerializer
)

from .utils.reset_code import (
    generate_code,
    store_code,
    can_send_new_code,
    get_stored_code,
    delete_code
)

from .utils.code import (
    generate_email_verification_token,
)

from account.tasks import (
    send_password_reset_otp_email,
    password_reset_successful
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_email_verified = False
            user.save()

            send_welcome_email.delay(user.name, user.email)

            uid, token = generate_email_verification_token(user)
            send_email_verification_link.delay(user.name, user.email, uid, token)

            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            # Calculate expiration times
            access_token_exp = datetime.utcnow() + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
            refresh_token_exp = datetime.utcnow() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']

            return Response({
                'user': {
                    'email': user.email,
                    'name': user.name,
                    'role': user.role,
                },
                'access_token': str(access_token),
                'refresh_token': str(refresh),
                'access_token_expires_at': access_token_exp.isoformat() + 'Z',
                'refresh_token_expires_at': refresh_token_exp.isoformat() + 'Z',
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({"detail": "Invalid verification link."}, status=400)

        if default_token_generator.check_token(user, token):
            user.is_email_verified = True
            user.save()
            return redirect("http://mypathweb.csi.miamioh.edu/?status=success")
        else:
            return redirect("http://mypathweb.csi.miamioh.edu/?status=success")

class CustomTokenRefreshView(APIView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            print("Errors:", serializer.errors)
            return Response({'detail': 'Refresh token is invalid or expired.'}, status=status.HTTP_401_UNAUTHORIZED)

        validated = serializer.validated_data
        new_access_token = validated["access"]
        new_refresh_token = validated["refresh"]

        access_token_exp = datetime.utcnow() + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
        refresh_token_exp = datetime.utcnow() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']

        return Response({
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "access_token_expires_at": access_token_exp.isoformat() + "Z",
            "refresh_token_expires_at": refresh_token_exp.isoformat() + "Z"
        }, status=status.HTTP_200_OK)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])

            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            access_token_exp = datetime.utcnow() + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
            refresh_token_exp = datetime.utcnow() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']

            return Response({
                "user": {
                    "email": user.email,
                    "name": user.name,
                    "role": user.role,
                },
                "access_token": str(access_token),
                "refresh_token": str(refresh),
                "access_token_expires_at": access_token_exp.isoformat() + 'Z',
                "refresh_token_expires_at": refresh_token_exp.isoformat() + 'Z',
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        data = serializer.data
        response_data = {
            "email": data["email"],
            "name": data["name"],
            **data["profile"]  # Unpack profile fields
        }
        return Response(response_data)

# account/views.py
class UpdateUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UpdateUserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": True,
                "detail": "Profile updated successfully.",
                "profile": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({"status": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"detail": "Password changed successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SendResetCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({'status': False,"detail": "Email is required."}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'status': False,"detail": "Email not found."}, status=404)

        if not can_send_new_code(email):
            return Response({'status': False,"detail": "Please wait before requesting a new code."}, status=429)

        code = generate_code()
        store_code(email, code)

        send_password_reset_otp_email.delay(user.name, user.email, code)
        return Response({'status': True,"detail": "Reset code sent to email."}, status=200)

class VerifyResetCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        submitted_code = request.data.get('code')

        if not email or not submitted_code:
            return Response({'status': False, 'detail': 'Email and code are required.'}, status=400)

        stored_code = get_stored_code(email)

        if stored_code is None:
            return Response({'status': False, 'detail': 'Code expired or not found.'}, status=400)

        if submitted_code != stored_code:
            return Response({'status': False,'detail': 'Invalid code.'}, status=400)

        return Response({'status': True,'detail': 'Code is valid.'}, status=200)

class ResetPasswordWithCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")
        new_password = request.data.get("new_password")

        stored_code = get_stored_code(email)
        if stored_code != code:
            return Response({'status': False, "detail": "Invalid or expired code."}, status=400)

        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        delete_code(email)

        password_reset_successful.delay(user.name, user.email)
        return Response({'status': True,"detail": "Password reset successful."}, status=200)

class WheelchairRelationViewSet(viewsets.ModelViewSet):
    serializer_class = WheelchairRelationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            WheelchairRelation.objects
            .filter(user=self.request.user)
            .order_by('-is_default', 'identifier')  # ✅ ordering: default first, then name
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Prevent deletion if it's the only default
        if instance.is_default:
            has_other_default = WheelchairRelation.objects.filter(
                user=request.user,
                is_default=True
            ).exclude(id=instance.id).exists()

            if not has_other_default:
                return Response(
                    {"detail": "You must set another wheelchair as default before deleting this one."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        self.perform_destroy(instance)
        return Response({"detail": "Wheelchair deleted successfully."}, status=status.HTTP_200_OK)
