from rest_framework import generics
from .models import WheelchairType, WheelchairDriveType, WheelchairTireMaterial
from .serializers import (
    WheelchairTypeSerializer,
    WheelchairDriveTypeSerializer,
    WheelchairTireMaterialSerializer,
)

class WheelchairTypeListView(generics.ListAPIView):
    queryset = WheelchairType.objects.filter(status='active')
    serializer_class = WheelchairTypeSerializer


class WheelchairDriveTypeListView(generics.ListAPIView):
    queryset = WheelchairDriveType.objects.filter(status='active')
    serializer_class = WheelchairDriveTypeSerializer


class WheelchairTireMaterialListView(generics.ListAPIView):
    queryset = WheelchairTireMaterial.objects.filter(status='active')
    serializer_class = WheelchairTireMaterialSerializer

