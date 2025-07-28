from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from django.db.models.functions import Lower  # Import Lower for case-insensitive ordering
from geo.models import State, City, SubRegion, Country, Region, Timezone
from rest_framework import generics
from geo.serializers import CountrySerializer, PlaceSerializer, RegionSerializer, SubregionSerializer, StateSerializer, \
    CitySerializer, TimeZoneSerializer
from .models import Place
from django.db.models import Q


class RegionAPI(APIView):
    permission_classes = [IsAuthenticated]  # Allow public access

    def get(self, request, *args, **kwargs):
        try:
            # Fetch the states, ordered by name in ascending order (case-insensitive)
            regions = Region.objects.order_by('name').values('id', 'name')

            if not regions:
                return Response({"error": "Region not found."}, status=404)

            # Serialize the single country object
            country_serializer = RegionSerializer(regions, many=True)  # No need for many=True here
            return Response(country_serializer.data, status=200)

        except State.DoesNotExist:
            return Response({"error": "Region not found."}, status=404)

class SubRegionAPI(APIView):
    permission_classes = [IsAuthenticated]  # Allow public access

    def get(self, request, region_id, *args, **kwargs):

        try:
            # Fetch the states, ordered by name in ascending order (case-insensitive)
            subregions = SubRegion.objects.filter(region_id=region_id).order_by('name').values('id', 'name')

            if not subregions:
                return Response({"error": "No subregions found for this region."}, status=404)

            # Serialize the subregions
            subregion_serializer = SubregionSerializer(subregions, many=True)
            return Response(subregion_serializer.data, status=200)

        except State.DoesNotExist:
            return Response({"error": "Subregion not found."}, status=404)

class CountryAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            # Fetch the countries and serialize them
            countries = Country.objects.order_by('name').all()
            if not countries:
                return Response({"error": "Country not found."}, status=404)

            country_serializer = CountrySerializer(countries, many=True)
            return Response(country_serializer.data, status=200)

        except Country.DoesNotExist:
            return Response({"error": "Country not found."}, status=404)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

class CountryByCodeAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, code, *args, **kwargs):
        # Get the logged-in user if authenticated
        if not code:
            return Response({"error": "Country code is required."}, status=400)

        try:
            # Fetch the country by iso2 code
            country = Country.objects.get(iso2=code)

            if not country:
                return Response({"error": "No country found for this country code."}, status=404)

            # Serialize the single country object
            country_serializer = CountrySerializer(country)  # No need for many=True here
            return Response(country_serializer.data, status=200)

        except Country.DoesNotExist:
            return Response({"error": "Country not found."}, status=404)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

class StateAPI(APIView):
    permission_classes = [IsAuthenticated]  # Allow public access

    def get(self, request, country_code, *args, **kwargs):
        try:
            # Fetch the states, ordered by name in ascending order (case-insensitive)
            states = State.objects.filter(country_code=country_code).order_by(Lower('name'))

            if not states:
                return Response({"error": "States not found for the given country."}, status=404)

            # Serialize the single country object
            state_serializer = StateSerializer(states, many=True)  # No need for many=True here
            return Response(state_serializer.data, status=200)

        except State.DoesNotExist:
            return Response({"error": "Country not found."}, status=404)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

class CitiesAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, state_code, *args, **kwargs):
        try:
            cities = City.objects.filter(state_code=state_code).order_by('name')
            if not cities:
                return Response({"error": "Cities not found for the given state."}, status=404)

            serializer = CitySerializer(cities, many=True)
            return Response(serializer.data, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

class TimeZoneAPI(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, country_code, *args, **kwargs):
        try:
            # Fetch the timezones, ordered by gmt_offset in ascending order
            timezones = Timezone.objects.filter(country_code=country_code).order_by('tz_name')

            if not timezones:
                return Response({"error": "No timezones found."}, status=404)

            # Serialize the timezone objects (many=True is necessary here)
            timezone_serializer = TimeZoneSerializer(timezones, many=True)
            return Response(timezone_serializer.data, status=200)

        except Timezone.DoesNotExist:
            return Response({"error": "No timezones found."}, status=404)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

class PlaceAPI(generics.ListAPIView):
    serializer_class = PlaceSerializer

    def get_queryset(self):
        """
        Search for places by name, address, city, state, or country name.
        """
        search_term = self.request.query_params.get('name', None)

        try:
            if search_term:
                queryset = Place.objects.filter(
                    Q(name__icontains=search_term) |
                    Q(address__icontains=search_term) |
                    Q(city__name__icontains=search_term) |
                    Q(state__name__icontains=search_term) |
                    Q(country__name__icontains=search_term)
                ).distinct()
            else:
                queryset = Place.objects.all()

            return queryset

        except Exception as e:
            print(f"Error fetching queryset: {str(e)}")
            return Place.objects.none()

    def list(self, request, *args, **kwargs):
        """
        Override the list method to handle exceptions and provide custom error responses.
        """
        try:
            # Attempt to get the queryset and serialize it
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)

            # Return the successful response
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            # If there's an error, return a custom error response
            return Response(
                {"error": "An error occurred while fetching places.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


