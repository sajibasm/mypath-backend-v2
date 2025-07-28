
from django.urls import path
from django.views.decorators.cache import cache_page

from navigation.views import RouteAPI, TransitCreateAPI, TransitCancelAPI, TransitCompleteAPI, \
    MarkerCreateAPI, MarkerSearchAPI, MarkerStatusUpdateAPI

urlpatterns = [
    path('route/', cache_page(60 * 15)(RouteAPI.as_view()), name='route'),

    path('transits/create/', TransitCreateAPI.as_view(), name='create-navigation-transit'),
    path('transits/complete/', TransitCompleteAPI.as_view(), name='complete-navigation-transit'),
    path('transits/cancel/', TransitCancelAPI.as_view(), name='cancel-navigation-transit'),

    path('markers/create/', MarkerCreateAPI.as_view(), name='create-marker'),
    path('markers/search/', MarkerSearchAPI.as_view(), name='marker-search'),
    path('markers/update/', MarkerStatusUpdateAPI.as_view(), name='marker-update'),

]
