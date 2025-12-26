from django.contrib import admin
from django.utils.html import format_html
# AQUÍ ESTÁ EL TRUCO: Agregué ContenidoMultimedia al final de la lista de importación
from .models import Cliente, Radicacion, MatrizPerfilamiento, EntidadConvenio, NotaSeguimiento, ArchivoAdjunto, ContenidoMultimedia

# 1. IDENTIDAD VISUAL DE OPCIFIN
admin.site.site_header = "OPCIFIN - Administración"
admin.site.site_title = "OPCIFIN Admin"
admin.site.index_title = "Gestión de Radicaciones"

# --- BLOQUE DE INLINES ---
class NotaSeguimientoInline(admin.TabularInline):
    model = NotaSeguimiento
    extra = 1
    fields = ('comentario', 'fecha_creacion')
    readonly_fields = ('fecha_creacion',)

class RadicacionInline(admin.StackedInline):
    model = Radicacion
    extra = 0
    show_change_link = True

# --- CONFIGURACIÓN DEL MODELO CLIENTE ---
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('documento_identidad', 'nombre', 'perfil_laboral', 'score_datacredito', 'agente_asignado', 'tipo_origen')
    search_fields = ('nombre', 'documento_identidad')
    list_filter = ('perfil_laboral', 'agente_asignado')
    inlines = [NotaSeguimientoInline, RadicacionInline]

    def tipo_origen(self, obj):
        if obj.documento_identidad and str(obj.documento_identidad).startswith('WEB-'):
            return "🌐 WEB"
        return "👤 MANUAL"
    
    tipo_origen.short_description = 'Origen'

    fieldsets = (
        ('Datos del Cliente', {'fields': ('nombre', 'documento_identidad')}),
        ('Perfil Laboral y Crédito', {'fields': ('perfil_laboral', 'score_datacredito', 'agente_asignado')}),
        ('Estado de Riesgos', {'fields': ('tiene_embargos', 'tiene_reportes_negativos')}),
    )

# --- CONFIGURACIÓN DE LOS DEMÁS MODELOS ---

@admin.register(Radicacion)
class RadicacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'entidad', 'monto_solicitado', 'estado_proceso', 'fecha_radicacion')
    list_editable = ('estado_proceso',)
    list_filter = ('estado_proceso', 'entidad')

@admin.register(MatrizPerfilamiento)
class MatrizPerfilamientoAdmin(admin.ModelAdmin):
    list_display = ('entidad', 'segmento_cliente', 'score_minimo')

@admin.register(EntidadConvenio)
class EntidadConvenioAdmin(admin.ModelAdmin):
    list_display = ('nombre_entidad', 'tipo_entidad', 'activo')
    list_editable = ('activo',)

@admin.register(NotaSeguimiento)
class NotaSeguimientoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'comentario', 'fecha_creacion')

@admin.register(ArchivoAdjunto)
class ArchivoAdjuntoAdmin(admin.ModelAdmin):
    list_display = ('radicacion', 'tipo_documento', 'archivo', 'fecha_subida')

# --- NUEVA SECCIÓN MULTIMEDIA PARA LLENAR LA WEB ---
@admin.register(ContenidoMultimedia)
class ContenidoMultimediaAdmin(admin.ModelAdmin):
    list_display = ('seccion', 'titulo', 'activo')
    list_filter = ('seccion', 'activo')