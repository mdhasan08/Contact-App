from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('registration/', include('registration.urls')),
    path('', include('contacts.urls')),
    path('import/', include('import.urls')),
    # path('export/', include('export.urls')),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)