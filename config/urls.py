from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin


api_patterns = [
    url(r'^', include('fighters.api.urls')),
    url(r'^', include('events.api.urls')),
]


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(api_patterns, namespace='api')),
    url(r'subscription/', include('subscriptions.urls')),
    url(r'', include('fighters.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + urlpatterns
