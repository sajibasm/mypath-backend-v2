from django.urls import path
from .views import (
    WheelchairTypeListView,
    WheelchairDriveTypeListView,
    WheelchairTireMaterialListView,
)

urlpatterns = [
    path('types/', WheelchairTypeListView.as_view(), name='wheelchair-type-list'),
    path('drive-types/', WheelchairDriveTypeListView.as_view(), name='wheelchair-drive-type-list'),
    path('tire-materials/', WheelchairTireMaterialListView.as_view(), name='wheelchair-tire-material-list'),
]
