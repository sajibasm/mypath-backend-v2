from rest_framework import serializers
from .models import WheelchairType, WheelchairDriveType, WheelchairTireMaterial

class WheelchairTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WheelchairType
        fields = ['id', 'name', 'status']

class WheelchairDriveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WheelchairDriveType
        fields = ['id', 'name', 'status']

class WheelchairTireMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = WheelchairTireMaterial
        fields = ['id', 'name', 'status']
