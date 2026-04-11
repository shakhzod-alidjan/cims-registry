from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('', include('apps.core.urls')),

    # App pages
    path('licenses/', include('apps.licenses.urls')),
    path('internet/',  include('apps.internet.urls')),
    path('dns/',       include('apps.dns.urls')),
    path('cloud/',     include('apps.cloud.urls')),

    # REST API
    path('api/', include([
        path('', include('apps.core.api_urls')),
        path('licenses/', include('apps.licenses.api_urls')),
        path('internet/', include('apps.internet.api_urls')),
        path('dns/',      include('apps.dns.api_urls')),
        path('cloud/',    include('apps.cloud.api_urls')),
    ])),

    # API docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/',   SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
