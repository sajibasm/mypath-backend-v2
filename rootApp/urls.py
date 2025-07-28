from django.conf import settings
from django.contrib import admin
from django.urls import path, include
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('account.urls')),
    path('api/wheelchair/', include('wheelchair.urls')),
    path('api/geo/', include('geo.urls')),
    path('api/navigation/', include('navigation.urls')),
    path('api/device/', include('device.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
