# geo/serializers.py
from rest_framework import serializers
from .models import Place, Country, Region, SubRegion, State, City, Timezone



class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        # Include the fields you want to serialize
        fields = ['id', 'name']


class SubregionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubRegion
        fields = ['id', 'name']  # Include the fields you want to expose


class CountrySerializer(serializers.ModelSerializer):
    region = RegionSerializer(read_only=True)
    subregion = SubregionSerializer(read_only=True)
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = [
            'id', 'name', 'iso2', 'iso3', 'numeric_code', 'phone_code', 'capital',
            'currency', 'currency_name', 'currency_symbol', 'tld', 'native', 'nationality',
            'latitude', 'longitude',  # ✅ Add these instead of raw WKT `location`
            'emoji', 'emojiU', 'region', 'subregion'
        ]

    def get_latitude(self, obj):
        return obj.location.y if obj.location else None

    def get_longitude(self, obj):
        return obj.location.x if obj.location else None


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        # Include the fields you want to serialize
        fields = ['id', 'name', 'state_code', 'country_code']

    def get_latitude(self, obj):
        return obj.location.y if obj.location else None

    def get_longitude(self, obj):
        return obj.location.x if obj.location else None

class CitySerializer(serializers.ModelSerializer):
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = ['id', 'name', 'country_code', 'state_code', 'wikiDataId', 'latitude', 'longitude']
        # 👆 Add 'latitude' and 'longitude' to the list

    def get_latitude(self, obj):
        return obj.location.y if obj.location else None

    def get_longitude(self, obj):
        return obj.location.x if obj.location else None

class TimeZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timezone
        # Include the fields you want to serialize
        fields = ['id', 'country_code', 'tz_name', 'zone_name','gmt_offset', 'abbreviation', 'gmt_offset_name']


class PlaceSerializer(serializers.ModelSerializer):
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    city_name = serializers.CharField(source='city.name', read_only=True)
    state_name = serializers.CharField(source='state.name', read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)

    class Meta:
        model = Place
        fields = ['id', 'name', 'address', 'zip_code', 'latitude', 'longitude',
                  'city', 'state', 'country', 'city_name', 'state_name', 'country_name']

    def get_latitude(self, obj):
        return obj.location.y if obj.location else None

    def get_longitude(self, obj):
        return obj.location.x if obj.location else None