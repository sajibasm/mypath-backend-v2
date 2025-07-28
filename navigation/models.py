from collections import OrderedDict
from account.models import User  # Import the User model from the account app
from django.contrib.gis.db import models as gis_models

from django.db import models
from geo.models import Place

from account.models import WheelchairRelation  # Import the Wheelchair model from account app
import json
import uuid

class Route(models.Model):
    STATUS_CHOICES = [
        ('inactive', 'Inactive'),
        ('active', 'Active')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    origin = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='routes_from')
    destination = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='routes_to')
    route = models.JSONField( null=True, blank=True)  # Store route data as JSON
    number_of_segments = models.IntegerField(default=1, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='navigationRoutes')

    # Distinct related_name for the updated_by field
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='updated_routes')


    def save(self, *args, **kwargs):
        if isinstance(self.route, dict):
            self.route = json.loads(json.dumps(self.route, sort_keys=False), object_pairs_hook=OrderedDict)
        super().save(*args, **kwargs)

    @classmethod
    def route_exists(cls, origin_id, destination_id):
        """
        Check if a route exists based on origin and destination place IDs.

        Parameters:
            origin_id (UUID): The ID of the origin place.
            destination_id (UUID): The ID of the destination place.

        Returns:
            bool: True if the route exists, False otherwise.
        """
        return cls.objects.filter(origin_id=origin_id, destination_id=destination_id).exists()


    class Meta:
        db_table = 'navigation_route'
        verbose_name_plural = 'Routes'

    def __str__(self):
        return f"{self.origin} -- {self.destination}"

class SurfaceType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'navigation_surface_type'
        verbose_name_plural = 'Surface'
        ordering = ['name']

class TravelType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'navigation_travel_type'
        verbose_name_plural = 'Travel Type'
        ordering = ['name']

class Transit(models.Model):
    # Define status choices
    STATUS_CHOICES = [
        ('search', 'Search'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]

    SOURCE_CHOICES = [
        ('app', 'App'),
        ('google', 'Google'),
        ('osm', 'OSM')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='navigationTransits')

    # Foreign keys to the Place model for origin and destination addresses
    origin = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='origin_transits')
    destination = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='destination_transits')

    # Timestamps for when the trip starts and ends
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)

    # Navigation metrics
    average_speed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    distance = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    duration = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    # Boolean flags for Barrier and Facility reports during navigation
    barrier_report = models.BooleanField(default=False, db_index=True)
    facility_report = models.BooleanField(default=False, db_index=True)

    # ForeignKey to Wheelchair model
    wheel_chair = models.ForeignKey(WheelchairRelation, on_delete=models.SET_NULL, null=True, blank=True, related_name='userWheelchairRelation')

    # Status of the transit
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='app', db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'navigation_transit'
        verbose_name_plural = 'Transits'  # Admin panel name

    def __str__(self):
        return f'{self.user.username}: {self.origin.name} to {self.destination.name}'

class TransitMarker(models.Model):

    STATUS_CHOICES = [
        ('detected', 'Detected'),
        ('resolved', 'Resolved')
    ]

    MARKER_CATEGORIES = [
        ('Barrier', 'Barrier'),
        ('Facility', 'Facility'),
    ]

    MARKER_TYPES = [
        # Barrier types
        ('Stairs', 'Stairs'),
        ('Steep Slope', 'Steep Slope'),
        ('Snow Pile', 'Snow Pile'),
        ('Construction', 'Construction'),
        ('Tree', 'Tree'),
        ('SideWalk', 'SideWalk'),
        ('No Curb Ramp', 'No Curb Ramp'),
        # Facility types
        ('Elevator', 'Elevator'),
        ('Curb Ramp', 'Curb Ramp'),
        ('Crosswalk', 'Crosswalk'),
        ('Sidewalk', 'Sidewalk'),
        ('Others', 'Others'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Foreign keys to the Place model for origin and destination addresses
    transit = models.ForeignKey(Transit, on_delete=models.CASCADE, related_name='transit_markers', null=True)
    # Field to store the MD5 hash
    segment_number = models.IntegerField(default=1, db_index=False)

    marker_category = models.CharField(max_length=50, choices=MARKER_CATEGORIES, db_index=True)
    marker_type = models.CharField(max_length=100, choices=MARKER_TYPES, db_index=True)
    location = gis_models.PointField(null=True, blank=True, srid=4326)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='detected', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Use only auto_now_add=True

    class Meta:
        db_table = 'navigation_transit_marker'  # Custom table name with the prefix 'navigation_transit'
        verbose_name_plural = 'Marker'  # Change the admin menu name to 'User Marker'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        if self.location:
            return f"{self.marker_category} - {self.marker_type} at ({self.location.y}, {self.location.x})"
        return f"{self.marker_category} - {self.marker_type} [No Location]"


class TransitMarkerTracking(models.Model):
    STATUS_CHOICES = [
        ('detected', 'Detected'),
        ('persistent', 'Persistent'),
        ('resolved', 'Resolved'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Foreign keys to the marker, user models
    transit = models.ForeignKey(Transit, on_delete=models.CASCADE, related_name='markers')
    marker = models.ForeignKey(TransitMarker, on_delete=models.CASCADE, related_name='resolutions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resolved_markers')

    # New generic status field to store 'exist' or 'resolved'
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='detected', db_index=True, help_text="Status of the marker resolution")
    created_at = models.DateTimeField(auto_now_add=True)  # Use only auto_now_add=True

    class Meta:
        db_table = 'navigation_transit_marker_tracking'  # Custom table name
        verbose_name_plural = 'Marker Tracking'  # Admin panel name

    def __str__(self):
        return f"Resolution by {self.user.username} for Marker {self.marker.id} - Status: {self.get_status_display()}"
