from django.db import models
from django.contrib.gis.db import models as gis_models

import uuid

# Region Model
class Region(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    wikiDataId = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

# SubRegion Model
class SubRegion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='subregions')
    wikiDataId = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "Sub Region"
        verbose_name_plural = "Sub Regions"

    def __str__(self):
        return self.name

# Country Model
class Country(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    iso3 = models.CharField(max_length=3, null=True, blank=True, unique=True)
    iso2 = models.CharField(max_length=5, null=True, blank=True, unique=True)
    numeric_code = models.CharField(max_length=10, null=True, blank=True)
    phone_code = models.CharField(max_length=20, null=True, blank=True)
    capital = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=50, null=True, blank=True)
    currency_name = models.CharField(max_length=50, null=True, blank=True)
    currency_symbol = models.CharField(max_length=10, null=True, blank=True)
    tld = models.CharField(max_length=10, null=True, blank=True)
    native = models.CharField(max_length=255, null=True, blank=True)
    nationality = models.CharField(max_length=255, null=True, blank=True)
    location = gis_models.PointField(null=True, blank=True, srid=4326)

    emoji = models.CharField(max_length=10, null=True, blank=True)
    emojiU = models.CharField(max_length=255, null=True, blank=True)

    region = models.ForeignKey('Region', on_delete=models.CASCADE, related_name='region_countries', null=True, blank=True)
    subregion = models.ForeignKey('SubRegion', on_delete=models.CASCADE, related_name='subregion_countries', null=True, blank=True)

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Country"
        ordering = ['name']
        indexes = [
            models.Index(fields=['iso2']),
            models.Index(fields=['iso3']),
        ]

    def __str__(self):
        return self.name

# State Model
class State(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    country_code = models.CharField(max_length=5, null=True, blank=True, db_index=True)
    state_code = models.CharField(max_length=10, unique=True, null=True, blank=True, db_index=True)
    type = models.CharField(max_length=50, null=True, blank=True)
    location = gis_models.PointField(null=True, blank=True, srid=4326)

    class Meta:
        verbose_name = "State"
        verbose_name_plural = "States"
        ordering = ['name']

    def __str__(self):
        return self.name

# City Model
class City(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    country_code = models.CharField(max_length=3, null=True, blank=True, db_index=True)
    state_code = models.CharField(max_length=10, null=True, blank=True, db_index=True)
    location = gis_models.PointField(null=True, blank=True, srid=4326)
    wikiDataId = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"

    def __str__(self):
        return self.name

# Timezone Model
class Timezone(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country_code = models.CharField(max_length=3, null=True, blank=True, db_index=True)  # Foreign key-like behavior
    tz_name = models.CharField(max_length=50)  # Time zone name, e.g., "Hawaii–Aleutian Standard Time"
    zone_name = models.CharField(max_length=30)  # Region or city, e.g., "America/Adak"
    gmt_offset = models.IntegerField()  # Offset from UTC in seconds, e.g., -36000
    abbreviation = models.CharField(max_length=10)  # Time zone abbreviation, e.g., "HST"
    gmt_offset_name = models.CharField(max_length=10)  # Offset from UTC in human-readable format, e.g., "UTC-10:00"

    class Meta:
        verbose_name = "Timezone"
        verbose_name_plural = "Timezones"
        ordering = ['tz_name']

    def __str__(self):
        return f"{self.tz_name} ({self.zone_name})"

class Place(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=10, db_index=True)
    location = gis_models.PointField(null=True, blank=True, srid=4326)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='city_places')
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='country_places')
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='state_places')

    class Meta:
        unique_together = ('country', 'state', 'city', 'zip_code', 'location')

    def __str__(self):
        return self.name
