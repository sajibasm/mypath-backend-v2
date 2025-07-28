# navigation/serializers.py
from rest_framework import serializers
from django.utils import timezone

from geo.serializers import PlaceSerializer
from .models import Route, Transit, TransitMarker, TransitMarkerTracking, SurfaceType
from django.contrib.gis.geos import Point

class MarkerSearchSerializer(serializers.Serializer):
    segment_start_lat = serializers.DecimalField(max_digits=9, decimal_places=6)
    segment_start_lng = serializers.DecimalField(max_digits=9, decimal_places=6)
    segment_end_lat = serializers.DecimalField(max_digits=9, decimal_places=6)
    segment_end_lng = serializers.DecimalField(max_digits=9, decimal_places=6)


class MarkerCreateSerializer(serializers.ModelSerializer):
    transit_id = serializers.PrimaryKeyRelatedField(
        queryset=Transit.objects.all(),
        source='transit',
        write_only=True
    )

    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    class Meta:
        model = TransitMarker
        fields = [
            'transit_id',
            'segment_number',
            'marker_category',
            'marker_type',
            'status',
            'latitude',
            'longitude',
            'created_at'
        ]
        read_only_fields = ['created_at']

    def get_latitude(self, obj):
        return obj.location.y if obj.location else None

    def get_longitude(self, obj):
        return obj.location.x if obj.location else None


class MarkerSearchInputSerializer(serializers.Serializer):
    segment_start_lat = serializers.DecimalField(max_digits=10, decimal_places=7)
    segment_start_lng = serializers.DecimalField(max_digits=10, decimal_places=7)
    segment_end_lat = serializers.DecimalField(max_digits=10, decimal_places=7)
    segment_end_lng = serializers.DecimalField(max_digits=10, decimal_places=7)


class TransitCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transit  # Assuming you want to serialize this model
        fields = ['id', 'start_at', 'end_at',]
        # read_only_fields = ['id', 'status']  # 'id' is auto-generated, 'status' is set automatically
    def create(self, validated_data):
        # Set the default status to 'in_progress' or handle logic as needed
        validated_data['status'] = 'in_progress'
        return super().create(validated_data)

class TransitCompleteSerializer(serializers.ModelSerializer):
    end_lat = serializers.DecimalField(max_digits=10, decimal_places=6)
    end_lng = serializers.DecimalField(max_digits=10, decimal_places=6)
    average_speed = serializers.DecimalField(max_digits=5, decimal_places=2)
    distance = serializers.DecimalField(max_digits=6, decimal_places=2)
    time = serializers.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        model = Transit
        fields = ['id', 'origin', 'destination',
                  'end_lat', 'end_lng', 'end_at',
                  'average_speed', 'distance', 'time',
                  'wheel_chair', 'status']
        # read_only_fields = ['end_at', 'status']  # 'status' and 'end_at' are set automatically

    def update(self, instance, validated_data):
        # Set end_at to current time and status to 'Completed'
        instance.end_at = timezone.now()
        instance.status ='completed'
        instance.end_lat = validated_data.get('end_lat', instance.end_lat)
        instance.end_lng = validated_data.get('end_lng', instance.end_lng)
        instance.average_speed = validated_data.get('average_speed', instance.average_speed)
        instance.distance = validated_data.get('distance', instance.distance)
        instance.time = validated_data.get('time', instance.time)
        instance.save()
        return instance

class TransitCancelSerializer(serializers.ModelSerializer):
    transit_id = serializers.UUIDField(write_only=True)
    distance = serializers.CharField(required=False)
    duration = serializers.IntegerField(required=False)

    class Meta:
        model = Transit
        fields = ['transit_id', 'end_at', 'status', 'distance', 'duration']  # Use `transit_id` instead of `id`
        read_only_fields = ['end_at', 'status']  # `end_at` and `status` are set automatically

    def update(self, instance, validated_data):
        # Set `end_at` to the current time and `status` to 'canceled'
        instance.end_at = timezone.now()
        instance.status = 'canceled'
        instance.end_lat = validated_data.get('end_lat', instance.end_lat)
        instance.end_lng = validated_data.get('end_lng', instance.end_lng)
        instance.save()
        return instance

class TransitMarkerTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransitMarkerTracking
        fields = ['id', 'marker', 'user', 'status', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']

# serializers.py
class RouteSerializer(serializers.ModelSerializer):
    origin = PlaceSerializer(read_only=True)  # Nested PlaceSerializer for origin
    destination = PlaceSerializer(read_only=True)  # Nested PlaceSerializer for destination

    class Meta:
        model = Route
        fields = [ 'id', 'origin', 'destination']

class SurfaceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurfaceType
        fields = ['name']  # Assuming 'name' is a field in SurfaceType representing the surface type name

class LocationSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=10, decimal_places=7, allow_null=True)
    longitude = serializers.DecimalField(max_digits=10, decimal_places=7, allow_null=True)

class DistanceDurationSerializer(serializers.Serializer):
    text = serializers.CharField()
    type = serializers.CharField()
    value = serializers.FloatField()

class AddressSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    address = serializers.CharField()

class RouteResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    source = serializers.CharField()
    transit_id = serializers.UUIDField()
    origin_place = AddressSerializer()
    destination_place = AddressSerializer()
    distance = DistanceDurationSerializer()
    duration = DistanceDurationSerializer()
    start_location = LocationSerializer(allow_null=True)
    end_location = LocationSerializer(allow_null=True)

class TransitCancelResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    data = TransitCancelSerializer(required=False)  # Only present if success is True
    error = serializers.CharField(required=False)  # Only present if success is False

class TransitDataSerializer(serializers.Serializer):
    transit_id = serializers.UUIDField()
    status = serializers.CharField()
    origin = serializers.UUIDField()
    destination = serializers.UUIDField()

class TransitCreateResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    data = TransitDataSerializer()