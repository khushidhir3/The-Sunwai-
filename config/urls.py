"""Root URL configuration for The Sunwai."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('accounts/', include('accounts.urls')),
    path('cases/', include('cases.urls')),
    path('scheduling/', include('scheduling.urls')),
    path('hearings/', include('hearings.urls')),
    path('directions/', include('directions.urls')),
    path('audit/', include('audit.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin site customization
admin.site.site_header = 'The Sunwai — Court Administration'
admin.site.site_title = 'The Sunwai Admin'
admin.site.index_title = 'Registry Administration'
