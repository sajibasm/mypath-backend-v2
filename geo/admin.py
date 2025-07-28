from django.contrib import admin
from .models import Region, SubRegion, Country, State, City, Timezone, Place

admin.site.site_header = "MyPath Admin"
admin.site.site_title = "MyPath Admin Title"
admin.site.index_title = "Welcome to MyPath Admin Portal"

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'wikiDataId')
    search_fields = ('name', 'wikiDataId')

@admin.register(SubRegion)
class SubRegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'wikiDataId')
    search_fields = ('name', 'wikiDataId')
    # list_filter = ('region',)

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'iso2', 'iso3', 'phone_code', 'capital', 'currency', 'native')
    search_fields = ('name', 'iso2', 'iso3', 'phone_code', 'capital', 'currency', 'native')
    # list_filter = ('region', 'subregion')
    ordering = ('name',)

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'country_code', 'state_code', 'type')
    search_fields = ('name', 'country_code', 'state_code')
    # list_filter = ('country_code',)

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country_code', 'state_code', 'get_lat', 'get_lng')
    search_fields = ('name', 'country_code', 'state_code')
    # list_filter = ('country_code', 'state_code')

    def get_lat(self, obj):
        return obj.location.y if obj.location else None
    get_lat.short_description = 'Latitude'

    def get_lng(self, obj):
        return obj.location.x if obj.location else None
    get_lng.short_description = 'Longitude'

@admin.register(Timezone)
class TimezoneAdmin(admin.ModelAdmin):
    list_display = ('tz_name', 'zone_name', 'gmt_offset', 'abbreviation', 'gmt_offset_name')
    search_fields = ('tz_name', 'zone_name', 'abbreviation')
    ordering = ('tz_name',)

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'country', 'state', 'city', 'zip_code', 'get_lat', 'get_lng')
    search_fields = ('name', 'address', 'zip_code')
    # list_filter = ('country', 'state', 'city')
    ordering = ('name',)

    def get_lat(self, obj):
        return obj.location.y if obj.location else None
    get_lat.short_description = 'Latitude'

    def get_lng(self, obj):
        return obj.location.x if obj.location else None
    get_lng.short_description = 'Longitude'
