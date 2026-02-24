from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Yaskawa_app_bckend.urls')),
]

# Gestion des fichiers STATIC et MEDIA en mode DEBUG
if settings.DEBUG:
    # 1. Ajoute la gestion des fichiers statiques (JS de Jazzmin)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # 2. Ajoute la gestion des images (Media)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)