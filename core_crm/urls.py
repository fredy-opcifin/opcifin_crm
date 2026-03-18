from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from gestion_financiera import views

urlpatterns = [

    path('admin/', admin.site.urls),
    # Web Principal (Home es la prioridad)
    path('', views.home, name='home'),
    # Acceso
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard (Ruta protegida)
    path('dashboard/', views.dashboard_moderno, name='dashboard_moderno'),
    path('dashboard/leads/', views.leads_list, name='leads_list'),
    path('dashboard/radicaciones/', views.radicaciones_list, name='radicaciones_list'),
    path('dashboard/asesores/', views.asesores_list, name='asesores_list'),
    path('dashboard/registro_manual/', views.registro_manual, name='registro_manual'),

    # IMPORTANTE: El nombre debe ser 'recordatorios' para que coincida con el HTML
    path('dashboard/recordatorios/', views.recordatorios_view, name='recordatorios'),
    path('convertir-lead/<int:lead_id>/', views.convertir_a_radicacion, name='convertir_a_radicacion'),
    path('lead/json/<int:lead_id>/', views.detalle_lead_json, name='lead_json'),
    path('lead/eliminar/<int:lead_id>/', views.eliminar_lead, name='eliminar_lead'),
    path('lead/actividad/<int:lead_id>/', views.crear_actividad, name='crear_actividad'),

    # Rutas del Sitio Web
    path('registro/', views.registro_cliente, name='registro'),
    path('contactanos/', views.capturar_lead, name='contactanos'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('atencion-cliente/', views.atencion_cliente, name='atencion_cliente'),
    path('guardar-resena/', views.guardar_resena, name='guardar_resena'),
    path('convenios/', views.convenios, name='convenios'),
    path('creditos/', views.hub_creditos, name='hub_creditos'),
    path('servicios-financieros/', views.hub_servicios, name='hub_servicios'),

    # Líneas de Producto
    path('servicios/libranza/', views.libranza, name='libranza'),
    path('servicios/hipotecario/', views.hipotecario, name='hipotecario'),
    path('servicios/prestamos-personales/', views.prestamos_personales, name='prestamos_personales'),
    path('servicios/compra-cartera/', views.compra_cartera, name='compra_cartera'),
    path('servicios/gestion/hipotecas/', views.hipotecas, name='hipotecas'),
    path('servicios/eliminacion-reportes/', views.eliminacion_reportes, name='eliminacion_reportes'),
    path('servicios/retanqueos/', views.retanqueos, name='retanqueos'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)