from django.urls import path
from django.views.decorators.cache import cache_page
from .views import *

urlpatterns = [
    path('regions/', cache_page(60 * 15)(RegionAPI.as_view()), name='regions'),
    path('subregions/<str:region_id>/', cache_page(60 * 15)(SubRegionAPI.as_view()), name='subregions'),
    path('countries/', cache_page(60 * 15)(CountryAPI.as_view()), name='countries'),
    path('country/<str:code>/', cache_page(60 * 15)(CountryByCodeAPI.as_view()), name='countryCode'),
    path('states/<str:country_code>/', cache_page(60 * 15)(StateAPI.as_view()), name='states'),
    path('cities/<str:state_code>/', cache_page(60 * 15)(CitiesAPI.as_view()), name='cities'),
    path('timezone/<str:country_code>/', cache_page(60 * 15)(TimeZoneAPI.as_view()), name='timezone'),
    path('places/', cache_page(60 * 15)(PlaceAPI.as_view()), name='search-places'),
]
