# navigation/views.py
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.models import WheelchairRelation
from .models import Route, Place, Transit, TransitMarker, TransitMarkerTracking
from .serializers import RouteSerializer, TransitCreateSerializer, TransitCancelSerializer, \
    TransitCompleteSerializer, \
    TransitMarkerTrackingSerializer, MarkerCreateSerializer, MarkerSearchSerializer, \
    MarkerSearchInputSerializer, RouteResponseSerializer, TransitCreateResponseSerializer, TransitCancelResponseSerializer

from .utils import Utils  # Import your utility class
from navigation.utils import Utils

import requests
import logging
from geo.models import Place, Country, State, City
import os
from django.db.models import Q
logger = logging.getLogger(__name__)

from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
import re


# Define the constant at the top of the view file
WHEEL_CHAIR_SPEED = 1.2  # speed in appropriate units, e.g., meters per second

def get_place_details(lat, lon):
    """Function to reverse geocode latitude and longitude using Google Places API and return place details with structured address components."""
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "latlng": f"{lat},{lon}",
        "key": os.getenv('GOOGLE_MPA_KEY'),
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("results"):
            # Retrieve detailed place info from the first result
            place = data["results"][0]
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

def find_or_create_place(name, address, country, state, city, zip_code, lat, lng, radius=5):
    """
    Finds a Place instance based on proximity to a point and matching address components.
    If not found, creates a new Place instance.

    Parameters:
        name (str): Name of the place.
        address (str): Address of the place.
        country (Country): Country instance.
        state (State): State instance.
        city (City): City instance.
        zip_code (str): Zip code of the place.
        lat (float or Decimal): Latitude.
        lng (float or Decimal): Longitude.
        radius (float): Radius in meters to search nearby places.

    Returns:
        Place: The Place instance found or created.
    """
    user_point = Point(lng, lat, srid=4326)

    # Attempt to find a matching place nearby
    place = Place.objects.annotate(distance=Distance('location', user_point)).filter(
        location__distance_lte=(user_point, D(m=radius)),
        country=country,
        state=state,
        city=city,
        zip_code=zip_code
    ).order_by('distance').first()

    if not place:
        place = Place.objects.create(
            name=name,
            address=address,
            country=country,
            state=state,
            city=city,
            zip_code=zip_code,
            location=user_point
        )
        print("New Place created with ID:", place.id)

    return place

def find_place_by_coordinates(lat, lng, radius=5):  # radius in meters
    """
    Finds a Place instance based on proximity to given coordinates.

    Parameters:
        lat (float): Latitude of the place.
        lng (float): Longitude of the place.
        radius (float): Search radius in meters.

    Returns:
        Place: The Place instance if found, otherwise None.
    """
    try:
        user_location = Point(lng, lat, srid=4326)

        # Search within `radius` meters using PostGIS distance lookup
        place = (
            Place.objects.annotate(distance=Distance('location', user_location))
            .filter(location__distance_lte=(user_location, D(m=radius)))
            .order_by('distance')
            .first()
        )
        return place

    except Exception as e:
        logger.error(f"Error in finding place by coordinates: {e}")
        return None

def get_place(origin_lat, origin_lng):

    place_by_coordinates = find_place_by_coordinates(origin_lat, origin_lng)

    if not place_by_coordinates:
        place_details = get_place_details(origin_lat, origin_lng)
        name, origin_address, origin_full_address, origin_lat, origin_lng, origin_city, origin_state, origin_country, origin_zip = place_details
        # Process Place

        # print('name', name);
        # print('origin_address', origin_address);
        # print('origin_full_address', origin_full_address);
        # print('origin_lat', origin_lat);
        # print('origin_lng', origin_lng);
        # print('origin_city', origin_city);
        # print('origin_state', origin_state);
        # print('origin_country', origin_country);
        # print('origin_zip', origin_zip);


        country_model = find_country(origin_country)
        state_model = find_state(origin_state, country_code=country_model.iso2 if country_model else None)
        city_model = find_city(origin_city, state_code=state_model.state_code if state_model else None, country_code=country_model.iso2 if country_model else None)

        return find_or_create_place(
            name=name,
            address=origin_address,
            country=country_model,
            state=state_model,
            city=city_model,
            zip_code=origin_zip,
            lat=origin_lat,
            lng=origin_lng
        )

    return place_by_coordinates

class RouteAPI(generics.GenericAPIView):
    """
    API to retrieve a route, its segments, and segment points between an origin and a destination place.
    """
    serializer_class = RouteSerializer

    @staticmethod
    def decode_polyline(self, encoded):
        points = []
        index = 0
        lat = 0
        lng = 0

        while index < len(encoded):
            result = 1
            shift = 0
            while True:
                b = ord(encoded[index]) - 63 - 1
                index += 1
                result += b << shift
                shift += 5
                if b < 0x1f:
                    break
            lat += ~(result >> 1) if result & 1 else result >> 1

            result = 1
            shift = 0
            while True:
                b = ord(encoded[index]) - 63 - 1
                index += 1
                result += b << shift
                shift += 5
                if b < 0x1f:
                    break
            lng += ~(result >> 1) if result & 1 else result >> 1

            points.append((lat / 1e5, lng / 1e5))

        return points

    @staticmethod
    def formatted_duration(duration):
        # Convert total duration in seconds to minutes and seconds
        minutes = int(duration // 60)
        seconds = round(duration % 60)

        # Format based on whether minutes or seconds are zero
        if minutes == 0:
            return f"{seconds} secs"
        elif seconds == 0:
            return f"{minutes} mins"
        else:
            return f"{minutes} mins {seconds} secs"

    @staticmethod
    def formatted_distance(distance):
        # Convert to feet if distance is less than 150 feet (45.72 meters)
        if distance < 45.72:
            feet = round(distance * 3.28084, 2)
            return f"{feet} ft"
        # Convert to miles if distance exceeds 1000 meters
        elif distance >= 1000:
            miles = round(distance / 1609.34, 2)  # Convert meters to miles
            return f"{miles} miles"
        else:
            return f"{round(distance, 2)} meters"

    def formate_self_route(self, route, transitId):
        # Find segments associated with the route
        segments = Segments.objects.filter(route=route).order_by("segment_number")
        # Find all segment points associated with the segments of the route
        segment_points = SegmentPoints.objects.filter(route=route).order_by("segment__segment_number", "point_number")


        total_duration = 0;
        total_distance = 0;
        origin_location = {
            "lat": None,
            "lng": None
        }

        destination_location = {
            "lat": None,
            "lng": None
        }

        segment_response = []

        for segment in segments:
            points = []

            # Gather points for the current segment
            for segmentPoint in segment_points:
                if segment.id == segmentPoint.segment.id and route.id == segmentPoint.route.id:
                    points.append({"latitude": segmentPoint.lat, "longitude": segmentPoint.lng})

            if segment.segment_number == 1:
                origin_location = points[0]

            if segment.segment_number == len(segments):
                destination_location = points[-1]

            total_duration += segment.duration
            total_distance += segment.distance

            clean_instructions = re.sub(r'<[^>]+>', '', segment.instructions)

            # Prepare the segment data
            segment_data = {
                "segment_number": segment.segment_number,
                "surface": segment.surface,
                "distance": {
                    "text": f"{self.formatted_distance(segment.distance)}",
                    "type": "meter",
                    "value": round(segment.distance, 2)
                },
                "duration": {
                    "text": f"{self.formatted_duration(segment.duration)}",
                    "type": "second",
                    "value": round(segment.duration, 2)
                },
                "maneuver": segment.maneuver,
                "instructions": clean_instructions,
                "travel_mode": segment.travel_mode
            }

            # Check if points are available before setting start and end locations
            if points:
                segment_data["start_location"] = {"latitude": points[0]['latitude'], "longitude": points[0]['longitude']}
                segment_data["end_location"] = {"latitude": points[-1]['latitude'], "longitude": points[-1]['longitude']}
                segment_data["points"] = points
            else:
                # Default or omit start and end locations if no points are available
                segment_data["end_location"] = None
                segment_data["start_location"] = None
                segment_data["points"] = []

            segment_response.append(segment_data)

        # Wrap the response data with additional fields
        response_data = {
            "success": True,
            "source": "App",  # Replace "App" with "Google" or "Miami" as needed
            "transit_id": transitId,
            "origin_place": {
                "id": route.origin.id,
                "address": f"{route.origin.name}, {route.origin.address}, {route.origin.city.name}, {route.origin.state.state_code} {route.origin.zip_code}, {route.origin.country.iso3}"
            },
            "destination_place": {
                "id": route.destination.id,
                "address": f"{route.destination.name}, {route.destination.address}, {route.destination.city.name}, {route.destination.state.state_code} {route.destination.zip_code}, {route.destination.country.iso3}"
            },
            "start_location": {
                "latitude": origin_location['latitude'],
                "longitude": origin_location['longitude']
            },
            "end_location": {
                "latitude": destination_location['latitude'],
                "longitude": destination_location['longitude']
            },
            "distance": {
                "text": f"{self.formatted_distance(total_distance)}",
                "type": "meter",
                "value": round(total_distance, 2)
            },
            "duration": {
                "text": f"{self.formatted_duration(total_duration)}",
                "type": "second",
                "value": round(total_duration, 2)
            },
            "segments": segment_response
        }

        # Use RouteResponseSerializer to serialize the final response
        serializer = RouteResponseSerializer(response_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def formatedGoogleRoute(self, google_route, origin_place, destination_place, transitId):
        # Parse the Google Maps route data into the required response format

        total_distance = 0
        total_duration = 0
        origin_location = {
            "latitude": google_route["legs"][0]["start_location"]["lat"],
            "longitude": google_route["legs"][0]["start_location"]["lng"]
        }
        destination_location = {
            "latitude": google_route["legs"][0]["end_location"]["lat"],
            "longitude": google_route["legs"][0]["end_location"]["lng"]
        }

        segments = []
        for leg in google_route["legs"]:
            segment_number = 1
            for step in leg["steps"]:

                decoded_points = self.decode_polyline(self, step["polyline"]["points"])
                points_list = [{"latitude": lat, "longitude": lng, "elevation": None} for lat, lng in decoded_points]

                segment_distance = round(step["distance"]["value"])
                segment_duration = round(segment_distance/WHEEL_CHAIR_SPEED)

                total_distance += segment_distance
                total_duration += segment_duration

                clean_instructions = re.sub(r'<[^>]+>', '', step["html_instructions"])

                segments.append({
                    "segment_number": segment_number,  # Optionally set based on your logic
                    "surface": "Concrete",  # Google doesn't provide surface; set default or omit
                    "distance": {
                        "text": f"{self.formatted_distance(segment_distance)}",
                        "type": "meter",
                        "value": segment_distance
                    },
                    "duration": {
                        "text": f"{self.formatted_duration(segment_duration)}",
                        "type": "second",
                        "value": segment_duration
                    },
                    "maneuver": step.get("maneuver"),
                    "instructions": clean_instructions,
                    "travel_mode": 'Wheelchair',
                    "start_location": {
                        "latitude": step["start_location"]["lat"],
                        "longitude": step["start_location"]["lng"]
                    },
                    "end_location": {
                        "latitude": step["end_location"]["lat"],
                        "longitude": step["end_location"]["lng"]
                    },
                    "points": points_list,  # Google Directions API doesn't return detailed points per segment
                    "incline": 0.0  # Google doesn't provide incline; set default or omit
                })
                segment_number += 1

        response_data = {
            "success": True,
            "source": "Google Routes",
            "transit_id": transitId,
            "origin_place": {
                "id": origin_place.id,
                "address": f"{origin_place.name}, {origin_place.address}, {origin_place.city.name}, {origin_place.state.state_code} {origin_place.zip_code}, {origin_place.country.iso3}"
            },
            "destination_place": {
                "id": destination_place.id,
                "address": f"{destination_place.name}, {destination_place.address}, {destination_place.city.name}, {destination_place.state.state_code} {destination_place.zip_code}, {destination_place.country.iso3}"
            },
            "start_location": origin_location,
            "end_location": destination_location,
            "distance": {
                "text": f"{self.formatted_distance(total_distance)}",
                "type": "meter",
                "value": round(total_distance, 2)
            },
            "duration": {
                "text": f"{self.formatted_duration(total_duration)}",
                "type": "second",
                "value": round(total_duration, 2)
            },
            "segments": segments
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def formatedOsmRoute(self, osm_route, origin_place, destination_place, transitId):
        # Parse the Google Maps route data into the required response format

        total_distance = 0
        total_duration = 0

        route_points = osm_route["points"]

        origin_location = {
            "latitude": route_points[0]["start_location"]["latitude"],
            "longitude": route_points[0]["start_location"]["longitude"]
        }
        destination_location = {
            "latitude": route_points[-1]["end_location"]["latitude"],
            "longitude": route_points[-1]["end_location"]["longitude"]
        }

        segments = []
        segment_number = 1  # Initialize outside the loop

        for leg in route_points:
            formatted_points = []
            for point in leg["points"]:
                formatted_points.append({
                    "latitude": point["latitude"],
                    "longitude": point["longitude"],
                    "elevation": point["elevation"]
                })

            segment_distance = round((leg["distance"]["value"]*0.3048)) # Convert feet to meters
            segment_duration = round(segment_distance / WHEEL_CHAIR_SPEED)

            total_distance += segment_distance
            total_duration += segment_duration

            clean_instructions = re.sub(r'<[^>]+>', '', leg["maneuver"]) if leg["maneuver"] else ""

            segments.append({
                "segment_number": segment_number,
                "surface": leg.get("surface", "unknown"),
                "distance": {
                    "text": f"{self.formatted_distance(segment_distance)}",
                    "type": "meter",
                    "value": segment_distance
                },
                "duration": {
                    "text": f"{self.formatted_duration(segment_duration)}",
                    "type": "second",
                    "value": segment_duration
                },
                "maneuver": clean_instructions,
                "instructions": clean_instructions,
                "travel_mode": "Wheelchair",
                "start_location": {
                    "latitude": leg["start_location"]["latitude"],
                    "longitude": leg["start_location"]["longitude"]
                },
                "end_location": {
                    "latitude": leg["end_location"]["latitude"],
                    "longitude": leg["end_location"]["longitude"]
                },
                "points": formatted_points,
                "incline": leg["incline"]
            })

            segment_number += 1

        response_data = {
            "success": True,
            "source": "OSM Routes",
            "transit_id": transitId,
            "origin_place": {
                "id": origin_place.id,
                "address": f"{origin_place.name}, {origin_place.address}, {origin_place.city.name}, {origin_place.state.state_code} {origin_place.zip_code}, {origin_place.country.iso3}"
            },
            "destination_place": {
                "id": destination_place.id,
                "address": f"{destination_place.name}, {destination_place.address}, {destination_place.city.name}, {destination_place.state.state_code} {destination_place.zip_code}, {destination_place.country.iso3}"
            },
            "start_location": origin_location,
            "end_location": destination_location,
            "distance": {
                "text": f"{self.formatted_distance(total_distance)}",
                "type": "meter",
                "value": round(total_distance, 2)
            },
            "duration": {
                "text": f"{self.formatted_duration(total_duration)}",
                "type": "second",
                "value": round(total_duration, 2)
            },
            "segments": segments
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def find_self_route(self, origin_place, destination_place, transit):
        # Find the route between the origin and destination for the user
        route = Route.objects.filter(
            origin=origin_place,
            destination=destination_place,
            status='active'
        ).first()

        if not route:

            print("No active route found between the specified origin and destination.")
            print("Searching Google Map Api.")

            google_route = self.googleMapRoute(origin_place.lat, origin_place.lng, destination_place.lat, destination_place.lng)

            if google_route:
                transit.source = 'google'
                transit.save()
                return self.formatedGoogleRoute(google_route, origin_place, destination_place, transit.id)

            return Response(
                {"success": False, "error": "No active route found between the specified origin and destination."},
                status=status.HTTP_404_NOT_FOUND
            )

        transit.source = 'app'
        transit.save()

        return self.formate_self_route(route, transit.id)

    def googleMapRoute(self, origin_lat, origin_lng, destination_lat, destination_lng, mode="cycling"):
        """
        Fetches a route from Google Maps Directions API with walking mode as the default.

        Parameters:
            origin_lat (float): Latitude of the origin location.
            origin_lng (float): Longitude of the origin location.
            destination_lat (float): Latitude of the destination location.
            destination_lng (float): Longitude of the destination location.
            mode (str): The travel mode for the route. Default is "walking".

        Returns:
            dict: Route data if available, otherwise None.
        """

        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": f"{origin_lat},{origin_lng}",
            "destination": f"{destination_lat},{destination_lng}",
            "mode": mode,
            "key": os.getenv('GOOGLE_MPA_KEY')
        }
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            if data["status"] == "OK":
                return data["routes"][0]  # Return the first route
        return None

    def osmMapRoute(self, origin_lat, origin_lng, destination_lat, destination_lng, mode="cycling"):
        """
        Fetches a route from Google Maps Directions API with walking mode as the default.
        Parameters:
            origin_lat (float): Latitude of the origin location.
            origin_lng (float): Longitude of the origin location.
            destination_lat (float): Latitude of the destination location.
            destination_lng (float): Longitude of the destination location.
            mode (str): The travel mode for the route. Default is "walking".

        Returns:
            dict: Route data if available, otherwise None.
        """

        url = "http://127.0.0.1:8093/route/getSingleRoute"
        payload = {
            'srcLat': f"{origin_lat}",
            'srcLon': f"{origin_lng}",
            'destLat': f"{destination_lat}",
            'destLon': f"{destination_lng}",
        }

        headers = {
            'api_key': 'MYPATHg5rDJhV2ThPlHsbx1PUV6omQSHHno2YehXASoKoiSIrIh7Wz38ZUKLI9nGcHIHxIZgJQ20TwpOet7dpvnandXGenGzf9E7LGu8wLozshUrQcGYcq61g8bTL5Bi'
        }

        response = requests.get(url, headers=headers, params=payload)
        if response.status_code == 200:
            return response.json()
        return None

    def post(self, request, *args, **kwargs):
        origin_location = request.data.get("originLocation")
        destination_location = request.data.get("destinationLocation")

        if not origin_location or not destination_location:
            return Response(
                {"success": False, "error": "Could not retrieve origin or destination place."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            origin_lat, origin_lng = map(float, origin_location.split(','))
            destination_lat, destination_lng = map(float, destination_location.split(','))

            origin_place = get_place(origin_lat, origin_lng)
            destination_place = get_place(destination_lat, destination_lng)

            if not origin_place or not destination_place:
                return Response(
                    {"success": False, "error": "Invalid origin or destination location."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Try OSM route first
            osm_route = self.osmMapRoute(origin_lat, origin_lng, destination_lat, destination_lng, "cycling")
            if osm_route and osm_route.get("routes"):
                transit = Transit.objects.create(
                    user=request.user,
                    origin=origin_place,
                    destination=destination_place,
                    status='search',
                    source='osm'
                )
                return self.formatedOsmRoute(osm_route["routes"], origin_place, destination_place, transit.id)

            # Fallback to Google route
            google_route = self.googleMapRoute(origin_lat, origin_lng, destination_lat, destination_lng, "cycling")
            if google_route:
                transit = Transit.objects.create(
                    user=request.user,
                    origin=origin_place,
                    destination=destination_place,
                    status='search',
                    source='google'
                )
                return self.formatedGoogleRoute(google_route, origin_place, destination_place, transit.id)

            return Response(
                {"success": False, "error": "No route found via OSM or Google."},
                status=status.HTTP_404_NOT_FOUND
            )

        except ValueError:
            return Response(
                {"success": False, "error": "Invalid location format. Use 'lat,lng'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error("Unexpected error in RouteAPI: %s", e)
            return Response(
                {"success": False, "error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MarkerCreateAPI(generics.CreateAPIView):
    queryset = TransitMarker.objects.all()
    serializer_class = MarkerCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data.copy()

        try:
            marker_lat = float(data.pop("marker_lat"))
            marker_lng = float(data.pop("marker_lng"))
            data["location"] = Point(marker_lng, marker_lat, srid=4326)
        except (KeyError, ValueError) as e:
            return Response(
                {"success": False, "error": f"Invalid or missing coordinates: {e}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            marker = serializer.save(location=data["location"])
            print("Saved location:", marker.location)

            TransitMarkerTracking.objects.create(
                transit=marker.transit,
                marker=marker,
                user=request.user,
                status='detected'
            )

            transit = marker.transit
            if marker.marker_category == "Barrier":
                transit.barrier_report = True
            else:
                transit.facility_report = True
            transit.save()

            return Response({"success": True, **serializer.data}, status=status.HTTP_201_CREATED)

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class MarkerSearchAPI(generics.GenericAPIView):
    serializer_class = MarkerCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        marker_lat = request.data.get("marker_lat")
        marker_lng = request.data.get("marker_lng")

        if not marker_lat or not marker_lng:
            return Response(
                {"success": False, "error": "Both marker_lat and marker_lng are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            point = Point(float(marker_lng), float(marker_lat), srid=4326)
        except Exception as e:
            return Response(
                {"success": False, "error": f"Invalid coordinates: {e}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Optional: limit to 50 meters radius
        nearby_marker = TransitMarker.objects.filter(
            status='detected',
            location__distance_lte=(point, 100)  # 50 meters
        ).annotate(
            distance=Distance('location', point)
        ).order_by('distance').first()

        if not nearby_marker:
            return Response(
                {"success": False, "error": "No nearby marker found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(nearby_marker)
        return Response({"success": True, **serializer.data}, status=status.HTTP_200_OK)

class MarkerTrackerAPI(generics.CreateAPIView):
    queryset = TransitMarkerTracking.objects.all()
    serializer_class = TransitMarkerTrackingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically associate the current user with the resolution
        serializer.save(user=self.request.user)

class MarkerStatusUpdateAPI(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        marker_lat = request.data.get("marker_lat")
        marker_lng = request.data.get("marker_lng")
        new_status = request.data.get("status")

        if not all([marker_lat, marker_lng, new_status]):
            return Response(
                {"success": False, "error": "marker_lat, marker_lng, and status are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_status not in ['persistent', 'resolved']:
            return Response(
                {"success": False, "error": "Invalid status value. Use 'persistent' or 'resolved'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            point = Point(float(marker_lng), float(marker_lat), srid=4326)
        except Exception as e:
            return Response(
                {"success": False, "error": f"Invalid coordinates: {e}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find the nearest marker within 50 meters
        marker = TransitMarker.objects.filter(
            status='detected',
            location__distance_lte=(point, 50)
        ).annotate(
            distance=Distance('location', point)
        ).order_by('distance').first()

        if not marker:
            return Response(
                {"success": False, "error": "No nearby active marker found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if new_status == 'resolved':
            marker.status = new_status
            marker.save()

        # Create tracking record
        TransitMarkerTracking.objects.create(
            transit=marker.transit,
            marker=marker,
            user=request.user,
            status=new_status
        )

        return Response({
            "success": True,
            "message": f"Marker status updated to '{new_status}'.",
            "marker_id": str(marker.id),
            "transit_id": str(marker.transit.id)
        }, status=status.HTTP_200_OK)

class TransitCreateAPI(generics.CreateAPIView):
    queryset = Transit.objects.all()
    serializer_class = TransitCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Retrieve transit_id and wheel_chair from request data
        transit_id = request.data.get("transit_id")
        wheel_chair = request.data.get("wheel_chair")

        print(transit_id, wheel_chair)

        if not transit_id or not wheel_chair:
            return Response(
                {"success": False, "error": "Both transit_id and wheel_chair are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the wheel_chair ID exists in the Wheelchair table
        try:
            wheelchair_instance = WheelchairRelation.objects.get(id=wheel_chair)
        except wheelchair_instance.DoesNotExist:
            return Response(
                {"success": False, "error": "The specified wheelchair ID does not exist."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Fetch the existing Transit record based on transit_id
            transit = Transit.objects.get(id=transit_id)
            # Update the necessary fields
            transit.wheel_chair = wheelchair_instance
            transit.start_at = timezone.now()  # Set start_at to current time
            transit.status = 'in_progress'
            transit.save()

            # Prepare the response data
            response_data = {
                "success": True,
                "data": {
                    "status": transit.status,
                    "transit_id": transit.id,
                    "origin": transit.origin.id if transit.origin else None,
                    "destination": transit.destination.id if transit.destination else None,
                }
            }

            # Serialize and return the response data
            response_serializer = TransitCreateResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Transit.DoesNotExist:
            return Response(
                {"success": False, "error": "Transit record with the provided ID does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

class TransitCompleteAPI(generics.UpdateAPIView):
    queryset = Transit.objects.all()
    serializer_class = TransitCompleteSerializer
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get_queryset(self):
        # Filter the transits that belong to the logged-in user
        return Transit.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        transit_id = request.data.get("transit_id")
        distance = request.data.get("distance")
        duration = request.data.get("duration")

        if not transit_id or distance is None or duration is None:
            return Response(
                {"success": False, "error": "transit_id, distance, and duration are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            transit = self.get_queryset().get(id=transit_id)

            # Convert to float
            distance = float(distance)
            duration = float(duration)

            transit.distance = distance
            transit.duration = duration
            transit.average_speed = round(distance / duration, 2)
            transit.status = 'completed'
            transit.end_at = timezone.now()
            transit.save()

            response_data = {
                "success": True,
                "data": {
                    "transit_id": transit.id,
                    "status": transit.status,
                    "distance": transit.distance,
                    "duration": transit.duration,
                    "end_at": transit.end_at,
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Transit.DoesNotExist:
            return Response(
                {"success": False, "error": "Transit record with the provided ID does not exist or does not belong to the user."},
                status=status.HTTP_404_NOT_FOUND
            )

class TransitCancelAPI(generics.UpdateAPIView):
    queryset = Transit.objects.all()
    serializer_class = TransitCancelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transit.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        transit_id = request.data.get("transit_id")
        distance = request.data.get("distance")
        duration = request.data.get("duration")

        if not transit_id:
            return Response(
                {"success": False, "error": "transit_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            transit = self.get_queryset().get(id=transit_id)

            # If both distance and duration are provided, compute average speed
            if distance is not None and duration is not None:
                try:
                    distance = float(distance)
                    duration = float(duration)
                    transit.distance = distance
                    transit.duration = duration
                    transit.average_speed = round(distance / duration, 2)
                    transit.status = 'completed'
                except ValueError:
                    return Response(
                        {"success": False, "error": "distance and duration must be numeric."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                # Default to canceled if not enough data for completion
                transit.status = 'canceled'

            transit.end_at = timezone.now()
            transit.save()

            return Response(
                {
                    "success": True,
                    "data": {
                        "transit_id": str(transit.id),
                        "status": transit.status,
                        "distance": transit.distance,
                        "duration": transit.duration,
                        "average_speed": getattr(transit, 'average_speed', None)
                    }
                },
                status=status.HTTP_200_OK
            )

        except Transit.DoesNotExist:
            return Response(
                {"success": False, "error": "Transit record with the provided ID does not exist or does not belong to the user."},
                status=status.HTTP_404_NOT_FOUND
            )
