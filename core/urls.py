from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/materias/', include('courses.urls')),
    path('api/v1/pagos/', include('payments.urls')),
    path('api/v1/communication/', include('communication.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
