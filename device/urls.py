from django.urls import path
from .views import SessionAPIView, SensorUploadAPIView, SessionSummaryReportAPIView, MonthlySessionSummaryAPIView

urlpatterns = [
    path('session/', SessionAPIView.as_view(), name='create-session'),
    path("session/summary/daily/", SessionSummaryReportAPIView.as_view(), name="session-summary"),
    path("session/summary/monthly/", MonthlySessionSummaryAPIView.as_view(), name="monthly-session-summary"),

    path('sensor/', SensorUploadAPIView.as_view(), name='sensor-bulk-upload'),
]
