from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import (
    Cliente, Radicacion, EntidadConvenio, Lead,
    PerfilAsesor, Recordatorio, Resena, ArchivoAdjunto
)

# 1. PERSONALIZACIÓN DEL ENCABEZADO
admin.site.site_header = "OPCIFIN - Administración"
admin.site.site_title = "OPCIFIN Admin"
admin.site.index_title = "Gestión de Radicaciones"

# --- 2. CLASES AUXILIARES Y FILTROS ---

class FiltroPorAsesorAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name='Auxiliar').exists():
            return qs
        # Cambiado de agente_asignado a asesor/asesor_asignado según el modelo
        if hasattr(self.model, 'asesor'):
            return qs.filter(asesor=request.user)
        if hasattr(self.model, 'asesor_asignado'):
            return qs.filter(asesor_asignado=request.user)
        return qs

    def save_model(self, request, obj, form, change):
        # Asignación automática del usuario logueado
        if hasattr(obj, 'asesor') and not obj.asesor:
            obj.asesor = request.user
        elif hasattr(obj, 'asesor_asignado') and not obj.asesor_asignado:
            obj.asesor_asignado = request.user
        super().save_model(request, obj, form, change)

# --- 3. INLINES ---

class RadicacionInline(admin.TabularInline):
    model = Radicacion
    extra = 0
    fields = ('fecha_inicio', 'monto_solicitado', 'estado_proceso')
    readonly_fields = ('fecha_inicio',)

# --- 4. CONFIGURACIÓN DE MODELOS ---

@admin.register(PerfilAsesor)
class PerfilAsesorAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'cargo', 'estatus', 'meta_mensual_unidades')
    list_editable = ('estatus', 'cargo')
    list_filter = ('estatus', 'cargo')

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin): # Nota: Cliente usa 'agente_asignado' según tu models
    list_display = ('nombre', 'perfil_laboral', 'telefono', 'ver_reporte', 'agente_asignado')
    search_fields = ('nombre', 'documento_identidad', 'telefono')
    list_filter = ('perfil_laboral', 'tiene_reportes_negativos', 'agente_asignado')
    inlines = [RadicacionInline]

    def ver_reporte(self, obj):
        if obj.tiene_reportes_negativos:
            return format_html('<span style="color: #d9534f; font-weight: bold;">🔴 Reportado</span>')
        return format_html('<span style="color: #5cb85c; font-weight: bold;">🟢 Al día</span>')
    ver_reporte.short_description = 'Centrales'

@admin.register(Lead)
class LeadAdmin(FiltroPorAsesorAdmin):
    # Ajustado a los nombres del nuevo models.py
    list_display = ('codigo_gestion', 'nombre_completo', 'ciudad', 'monto_solicitado', 'estado', 'asesor')
    list_editable = ('estado',)
    list_filter = ('estado', 'fuente', 'nicho', 'prioridad', 'asesor')
    search_fields = ('nombre_completo', 'cedula', 'telefono', 'codigo_gestion')

    fieldsets = (
        ('Información del Lead', {
            'fields': ('codigo_gestion', 'nombre_completo', 'cedula', 'telefono', 'email', 'ciudad', 'departamento')
        }),
        ('Detalles del Crédito', {
            'fields': ('nicho', 'monto_solicitado', 'ingreso_mensual', 'fuente', 'prioridad', 'empleador')
        }),
        ('Gestión de Oficina', {
            'fields': ('asesor', 'estado', 'notas')
        }),
    )
    readonly_fields = ('codigo_gestion',)

@admin.register(Radicacion)
class RadicacionAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'entidad', 'monto_solicitado', 'estado_proceso', 'fecha_inicio', 'fecha_desembolso')
    list_editable = ('estado_proceso', 'fecha_desembolso')
    list_filter = ('estado_proceso', 'entidad', 'asesor_asignado')

@admin.register(Recordatorio)
class RecordatorioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'fecha', 'completado')
    list_filter = ('completado', 'fecha', 'usuario')
    search_fields = ('titulo', 'usuario__username')

@admin.register(EntidadConvenio)
class EntidadConvenioAdmin(admin.ModelAdmin):
    list_display = ('nombre_entidad', 'tipo_entidad', 'activo')
    list_editable = ('activo',)

@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ('autor', 'puntuacion', 'fecha_creacion')
    list_filter = ('puntuacion', 'fecha_creacion')
    readonly_fields = ('fecha_creacion',)

@admin.register(ArchivoAdjunto)
class ArchivoAdjuntoAdmin(admin.ModelAdmin):
    list_display = ('lead', 'archivo', 'fecha_subida')