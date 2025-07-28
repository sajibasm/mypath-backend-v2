import os
import pandas as pd
import requests
from django import forms
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.contrib import admin, messages

from django.urls import path
from django.db.models import Q
from geo.models import Country, State, City, Place
from math import radians, sin, cos, sqrt, atan2

from .models import (
    Route, SurfaceType, TravelType, Transit, TransitMarker, TransitMarkerTracking
)


class UploadExcelForm(forms.Form):
    excel_file = forms.FileField(label="Select the Excel file to upload")

@admin.register(SurfaceType)
class SurfaceTypeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']

@admin.register(TravelType)
class TravelTypeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']

def get_place_details(location_name):
    """Function to search Google Places API and return place details with structured address components."""
    url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": location_name,
        "inputtype": "textquery",
        "fields": "formatted_address,geometry,place_id",
        "key": os.getenv('GOOGLE_MPA_KEY'),
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("candidates"):
            place_id = data["candidates"][0]["place_id"]

            # Retrieve detailed place info, including address components
            details_url = f"https://maps.googleapis.com/maps/api/place/details/json"
            details_params = {
                "place_id": place_id,
                "fields": "address_component,formatted_address,geometry",
                "key": os.getenv('GOOGLE_MPA_KEY'),
            }
            details_response = requests.get(details_url, params=details_params)
            if details_response.status_code == 200:
                details_data = details_response.json()
                if details_data.get("result"):
                    place = details_data["result"]
                    full_address = place["formatted_address"]
                    location = place["geometry"]["location"]

                    # Parse full address into name and address parts
                    parts = full_address.split(",")
                    name = parts[0].strip() if len(parts) > 0 else ""
                    address = parts[1].strip() if len(parts) > 1 else ""

                    # Extract city, state, country, and zip code from address components
                    city, state, country, zip_code = None, None, None, None
                    for component in place["address_components"]:
                        if "locality" in component["types"]:
                            city = component["long_name"]
                        elif "administrative_area_level_1" in component["types"]:
                            state = component["long_name"]
                        elif "country" in component["types"]:
                            country = component["long_name"]
                        elif "postal_code" in component["types"]:
                            zip_code = component["long_name"]

                    return name, address, full_address, location["lat"], location["lng"], city, state, country, zip_code
    return None, None, None, None, None, None, None, None, None

def find_country(country_value):
    """
    Finds a Country instance based on country name, ISO2, or ISO3 code.

    Parameters:
        country_value (str): The name, ISO2, or ISO3 code of the country.

    Returns:
        Country: A Country instance if found, otherwise None.
    """
    try:
        # Try to find by name, ISO2, or ISO3
        return Country.objects.filter(
            Q(name__iexact=country_value) |
            Q(iso2__iexact=country_value) |
            Q(iso3__iexact=country_value)
        ).first()
    except Country.DoesNotExist:
        return None

def find_state(state_value, country_code=None):
    """
    Finds a State instance based on the state name or state_code and optional country_code.

    Parameters:
        state_value (str): The name or code of the state.
        country_code (str): Optional ISO2 country code for additional filtering.

    Returns:
        State: A State instance if found, otherwise None.
    """
    try:
        query = State.objects.filter(
            Q(name__iexact=state_value) | Q(state_code__iexact=state_value)
        )
        if country_code:
            query = query.filter(country_code__iexact=country_code)

        return query.first()
    except State.DoesNotExist:
        return None

def find_city(city_value, state_code=None, country_code=None):
    """
    Finds a City instance based on city name, and optionally state_code and country_code.

    Parameters:
        city_value (str): The name of the city.
        state_code (str): Optional state code for additional filtering.
        country_code (str): Optional ISO2 country code for additional filtering.

    Returns:
        City: A City instance if found, otherwise None.
    """
    try:
        query = City.objects.filter(name__iexact=city_value)

        if state_code:
            query = query.filter(state_code__iexact=state_code)
        if country_code:
            query = query.filter(country_code__iexact=country_code)

        return query.first()
    except City.DoesNotExist:
        return None

def find_or_create_place(name, address, country, state, city, zip_code, lat, lng):
    """
    Finds a Place instance based on name, address, country, state, city, and zip_code.
    If not found, creates a new Place instance.

    Parameters:
        name (str): Name of the place.
        address (str): Address of the place.
        country (Country): Country instance.
        state (State): State instance.
        city (City): City instance.
        zip_code (str): Zip code of the place.
        lat (Decimal): Latitude of the place.
        lng (Decimal): Longitude of the place.

    Returns:
        Place: The Place instance found or created.
    """
    print(lat, lng, country, state, city, zip_code)
    place = Place.objects.filter(
        lat=lat,
        lng=lng,
        country=country,
        state=state,
        city=city,
        zip_code=zip_code
    ).first()

    # If place is not found, create a new one
    if not place:
        print("No Place Found:")
        place = Place.objects.create(
            name=name,
            address=address,
            country=country,
            state=state,
            city=city,
            zip_code=zip_code,
            lat=lat,
            lng=lng
        )
        print("New Place created with ID:", place.name)

    return place

def get_or_create_surface_type(name):
    """
    Retrieve the SurfaceType by name. If it doesn't exist, create a new one.

    Parameters:
        name (str): The name of the SurfaceType.

    Returns:
        SurfaceType: The existing or newly created SurfaceType instance.
    """
    surface_type, created = SurfaceType.objects.get_or_create(name=name)

    if created:
        print(f"Created new SurfaceType with ID: {surface_type.id} and Name: {surface_type.name}")
    else:
        print(f"Found existing SurfaceType with ID: {surface_type.id} and Name: {surface_type.name}")

    return surface_type.id

def haversine(lat1, lng1, lat2, lng2):
    # Radius of Earth in meters
    R = 6371000

    # Convert latitude and longitude from degrees to radians
    lat1 = radians(lat1)
    lng1 = radians(lng1)
    lat2 = radians(lat2)
    lng2 = radians(lng2)

    # Compute differences in coordinates
    dlat = lat2 - lat1
    dlng = lng2 - lng1

    # Haversine formula
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Distance in meters
    distance = R * c
    return distance

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['origin', 'destination', 'created_at', 'user', 'status', 'number_of_segments']
    search_fields = ['origin__name', 'destination__name']
    list_filter = ['status', 'created_at']
    ordering = ['created_at']
    fields = ['origin', 'destination', 'status']
    exclude = ['route', 'user', 'updated_by']


    def number_of_segments(self, obj):
        return obj.segments.count()
    number_of_segments.short_description = 'Number of Segments'

    # Use a custom change list template
    change_list_template = "admin/navigation/route_change_list.html"

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    # Define the custom URL for Excel upload
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-excel/', self.admin_site.admin_view(self.upload_excel), name="route-upload-excel"),
        ]
        return custom_urls + urls

    # Define the view to handle the Excel file upload
    def upload_excel(self, request):
        if request.method == "POST":
            form = UploadExcelForm(request.POST, request.FILES)
            if form.is_valid():
                excel_file = form.cleaned_data['excel_file']
                try:
                    # Load the Excel file and iterate over each sheet
                    xls = pd.ExcelFile(excel_file)

                    for sheet_name in xls.sheet_names:
                        df = xls.parse(sheet_name)

                        # Strip whitespace from the beginning and end of all string columns in the DataFrame
                        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

                        # Ensure 'Location' column exists and has at least two rows for origin and destination
                        if 'Location' in df.columns and len(df) >= 2:
                            # Set origin as the first row in 'Location' and destination as the last row
                            origin_name = df['Location'].iloc[0]  # First row as origin
                            destination_name = df['Location'].iloc[-1]  # Last row as destination

                            # Search Google Places API for origin and destination
                            origin_details = get_place_details(origin_name)
                            destination_details = get_place_details(destination_name)

                            print(f"Origin Details (Sheet: {sheet_name}):", origin_details)
                            print(f"Destination Details (Sheet: {sheet_name}):", destination_details)

                            # Unpack origin and destination details
                            if origin_details and destination_details:

                                origin_name, origin_address, origin_full_address, origin_lat, origin_lng, origin_city, origin_state, origin_country, origin_zip = origin_details

                                destination_name, destination_address, destination_full_address, destination_lat, destination_lng, destination_city, destination_state, destination_country, destination_zip = destination_details

                                # Process origin
                                origin_country_model = find_country(origin_country)
                                origin_state_model = find_state(origin_state,
                                                                country_code=origin_country_model.iso2 if origin_country_model else None)
                                origin_city_model = find_city(origin_city,
                                                              state_code=origin_state_model.state_code if origin_state_model else None,
                                                              country_code=origin_country_model.iso2 if origin_country_model else None)

                                origin_place = find_or_create_place(
                                    name=origin_name,
                                    address=origin_address,
                                    country=origin_country_model,
                                    state=origin_state_model,
                                    city=origin_city_model,
                                    zip_code=origin_zip,
                                    lat=origin_lat,
                                    lng=origin_lng
                                )

                                print(f"Origin Place ID (Sheet: {sheet_name}):", origin_place)

                                # Process destination
                                destination_country_model = find_country(destination_country)
                                destination_state_model = find_state(destination_state,
                                                                     country_code=destination_country_model.iso2 if destination_country_model else None)
                                destination_city_model = find_city(destination_city,
                                                                   state_code=destination_state_model.state_code if destination_state_model else None,
                                                                   country_code=destination_country_model.iso2 if destination_country_model else None)

                                destination_place = find_or_create_place(
                                    name=destination_name,
                                    address=destination_address,
                                    country=destination_country_model,
                                    state=destination_state_model,
                                    city=destination_city_model,
                                    zip_code=destination_zip,
                                    lat=destination_lat,
                                    lng=destination_lng
                                )

                                print(f"Destination Place ID (Sheet: {sheet_name}):", destination_place)

                                # Create a new Route instance
                                if Route.route_exists(origin_id=origin_place.id, destination_id=destination_place.id):
                                    print("Route already exists.")
                                else:
                                    print("Route does not exist and can be created.")

                                    new_route = Route(
                                        status='active',  # Set to either 'active' or 'inactive'
                                        origin=origin_place,
                                        destination=destination_place,
                                        route=[],  # JSON data for the route field
                                        user=request.user  # The user creating the route
                                    )

                                    new_route.save()

                                    # Initialize the mapSegment dictionary to store data by segment number
                                    mapSegment = {}

                                    # Loop through each row to read additional segment information
                                    for index, row in df.iterrows():

                                        start_location = row.get("StartLocation")

                                        # Split start_location by comma to get lat and lng
                                        if start_location:
                                            try:
                                                lat_str, lng_str = start_location.split(",",
                                                                                        1)  # Split into two parts only
                                                lat = float(
                                                    lat_str.strip())  # Convert to float and remove any whitespace
                                                lng = float(
                                                    lng_str.strip())  # Convert to float and remove any whitespace
                                            except ValueError:
                                                # Handle cases where start_location format is incorrect
                                                lat, lng = None, None
                                                print(
                                                    f"Invalid start_location format in row {index + 1}: {start_location}")
                                        else:
                                            lat, lng = None, None

                                        segment = row.get("Segment Number")
                                        surface = row.get("Surface")

                                        travel_mode = row.get("TravelMode")
                                        maneuver = row.get("Maneuver")
                                        instructions = row.get("Instructions")

                                        # Create a dictionary for the current row data
                                        segment_data = {
                                            "lat": lat,
                                            "lng": lng,
                                            "segment": segment,
                                            "surface": surface,
                                            "travel_mode": travel_mode,
                                            "maneuver": maneuver,
                                            "instructions": instructions
                                        }

                                        # Add the current row data to the appropriate segment in mapSegment
                                        segment_key = segment  # Assuming segment is an integer representing segment number
                                        if segment_key not in mapSegment:
                                            mapSegment[segment_key] = []  # Initialize a list for each new segment key

                                        mapSegment[segment_key].append(segment_data)

                                    wheelchair_speed_mps = 1.2  # Average speed in meters per second

                                    # Iterate over each segment in mapSegment
                                    from .models import SegmentPoints

                                    for segment_number, segment_data_list in mapSegment.items():
                                        print(f"Segment Number: {segment_number}")

                                        # Check if there is at least one data point in the list
                                        if segment_data_list:
                                            # Access initial data for this segment
                                            surface = segment_data_list[0].get("surface")
                                            surface_id = get_or_create_surface_type(surface)
                                            instructions = segment_data_list[0].get("instructions")
                                            maneuver = segment_data_list[0].get("maneuver")

                                            # Initialize total distance and duration for the segment
                                            segment_distance = 0
                                            previous_lat, previous_lng = None, None

                                            # Create the Segments instance
                                            new_segment = Segments(
                                                route=new_route,
                                                segment_number=segment_number,
                                                surface_id=surface_id,
                                                travel_mode_id=1,  # Replace with the correct travel mode ID
                                                maneuver=maneuver,
                                                instructions=instructions,
                                                duration=0,  # Calculated later
                                                distance=0,  # Calculated later
                                                user=request.user
                                            )

                                            new_segment.save()

                                            # Iterate over each row (dictionary) within the current segment and create SegmentPoints
                                            for i, data in enumerate(segment_data_list):
                                                lat = data.get("lat")
                                                lng = data.get("lng")

                                                # Calculate distance from the previous point, if applicable
                                                if previous_lat is not None and previous_lng is not None:
                                                    distance = haversine(previous_lat, previous_lng, lat,lng)  # Distance in meters
                                                    segment_distance += distance

                                                # Create the SegmentPoints instance
                                                segment_point = SegmentPoints(
                                                    segment=new_segment,
                                                    route=new_route,
                                                    user=request.user,
                                                    updated_by=request.user,
                                                    lat=lat,
                                                    lng=lng,
                                                    point_number=i + 1,  # Point number starts from 1
                                                )
                                                segment_point.save()
                                                print(f"SegmentPoint created with ID: {segment_point.id} at (lat: {lat}, lng: {lng})")

                                                # Update the previous point coordinates for the next iteration
                                                previous_lat, previous_lng = lat, lng

                                            if (segment_number + 1) in mapSegment:
                                                next_segment_data_list = mapSegment[segment_number + 1]
                                                next_lat = next_segment_data_list[0].get("lat")
                                                next_lng = next_segment_data_list[0].get("lng")

                                                # Calculate distance from the previous point, if applicable
                                                if previous_lat is not None and previous_lng is not None:
                                                    distance = haversine(previous_lat, previous_lng, next_lat,next_lng)  # Distance in meters
                                                    segment_distance += distance

                                                segment_point = SegmentPoints(
                                                    segment=new_segment,
                                                    route=new_route,
                                                    user=request.user,
                                                    updated_by=request.user,
                                                    lat=next_lat,
                                                    lng=next_lng,
                                                    point_number=len(segment_data_list) + 1,  # Point number starts from 1
                                                )
                                                segment_point.save()


                                            # Update the segment with the calculated total distance and duration
                                            new_segment.distance = segment_distance
                                            new_segment.duration = round(segment_distance / wheelchair_speed_mps)  # Duration in seconds
                                            new_segment.number_of_point = len(segment_data_list)+1
                                            new_segment.save()
                                            print(f"Total distance for segment {segment_number}: {segment_distance:.2f} meters")

                                    new_route.number_of_segments = len(mapSegment)
                                    new_route.save()

                            # Here, you could create Segment instances or perform additional processing as needed

                        else:
                            messages.warning(request,f"Sheet '{sheet_name}' does not contain a valid 'Location' column or has insufficient rows.")

                    messages.success(request, "Excel file processed successfully.")
                    return redirect("..")  # Redirect to Route admin change list
                except Exception as e:
                    messages.error(request, f"Error processing Excel file: {e}")
        else:
            form = UploadExcelForm()

        return TemplateResponse(request, "admin/upload_excel.html", {"form": form})

@admin.register(Transit)
class TransitAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'origin',
        'destination',
        'distance',
        'duration',
        'average_speed',
        'barrier_report',
        'facility_report',
        'status',
        'source',
        'start_at',
        'end_at',
        'created_at'
    ]
    search_fields = ['origin__name', 'destination__name', 'user__username']
    # list_filter = ['status', 'start_at', 'end_at']
    ordering = ['start_at']

@admin.register(TransitMarker)
class TransitMarkerAdmin(admin.ModelAdmin):
    list_display = ['id', 'marker_type', 'get_lat', 'get_lng', 'segment_number', 'status', 'created_at']
    search_fields = ['marker_type']
    list_filter = ['marker_category', 'marker_type', 'status']
    ordering = ['created_at']

    def get_lat(self, obj):
        return obj.location.y if obj.location else None
    get_lat.short_description = 'Latitude'

    def get_lng(self, obj):
        return obj.location.x if obj.location else None
    get_lng.short_description = 'Longitude'

    # Optional: make this read-only in the admin
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TransitMarkerTracking)
class TransitMarkerTrackingAdmin(admin.ModelAdmin):
    list_display = ['id', 'transit', 'marker', 'user', 'status', 'created_at']
    search_fields = ['transit__user__username', 'marker__id']
    list_filter = ['status']
    ordering = ['created_at']
    # Disable Add, Update, and Delete options
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False