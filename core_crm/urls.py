from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from web_opcifin import views # Importamos las vistas de una forma más limpia

urlpatterns = [
    # CORRECCIÓN: Cambiamos .path por .urls
    path('admin/', admin.site.urls),
    
    # Rutas de tu página
    path('', views.home, name='home'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('registro/', views.registro_cliente, name='registro'),
    path('servicios/', views.servicios, name='servicios'),
]

# Configuración para que las imágenes (MEDIA) y estilos (STATIC) se vean en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)