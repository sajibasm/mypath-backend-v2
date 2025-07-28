
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, LoginView,
    UserProfileView, ChangePasswordView,
    WheelchairRelationViewSet,
    SendResetCodeView,
    VerifyResetCodeView,
    ResetPasswordWithCodeView,
    VerifyEmailView, CustomTokenRefreshView, UpdateUserProfileView
)

router = DefaultRouter()
router.register(r'wheelchair', WheelchairRelationViewSet, basename='wheelchair')

urlpatterns = [
    # Auth and profile routes
    path('register/', RegisterView.as_view(), name='register'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),

    path("verify-email/<uidb64>/<token>/", VerifyEmailView.as_view(), name="verify-email"),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/update/', UpdateUserProfileView.as_view(), name='profile-update'),

    path('change-password/', ChangePasswordView.as_view(), name='change-password'),

    path('reset-password/send-code/', SendResetCodeView.as_view()),
    path('reset-password/verify-code/', VerifyResetCodeView.as_view()),
    path('reset-password/confirm/', ResetPasswordWithCodeView.as_view()),
    # Wheelchair RESTful routes via router
    path('', include(router.urls)),
]

# urlpatterns = [
#     # # Sensor and Session Data
#     # path('sensor-data/', UserSensorDataView.as_view(), name='sensor_data'),
#     # path('session-data/', UserSessionDataView.as_view(), name='session_data'),
# ]
