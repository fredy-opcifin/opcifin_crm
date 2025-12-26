from django.db import models
from django.contrib.auth.models import User

class EntidadConvenio(models.Model):
    TIPO_CHOICES = [('BANCO', 'Banco'), ('COOPERATIVA', 'Cooperativa'), ('FINANCIERA', 'Financiera')]
    nombre_entidad = models.CharField(max_length=100)
    tipo_entidad = models.CharField(max_length=20, choices=TIPO_CHOICES)
    activo = models.BooleanField(default=True)
    politica_credito_resumen = models.TextField(blank=True)

    def __str__(self):
        return self.nombre_entidad

class Cliente(models.Model):
    PERFIL_CHOICES = [('PENSIONADO', 'Pensionado'), ('PUBLICO', 'Empleado Público'), ('PRIVADO', 'Empleado Privado')]
    nombre = models.CharField(max_length=200)
    documento_identidad = models.CharField(max_length=20, unique=True)
    perfil_laboral = models.CharField(max_length=20, choices=PERFIL_CHOICES)
    score_datacredito = models.IntegerField(default=0)
    tiene_embargos = models.BooleanField(default=False)
    tiene_reportes_negativos = models.BooleanField(default=False)
    agente_asignado = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.documento_identidad})"

    def consultar_viabilidad(self):
        from .models import MatrizPerfilamiento
        viables = MatrizPerfilamiento.objects.filter(
            segmento_cliente=self.perfil_laboral,
            score_minimo__lte=self.score_datacredito,
            acepta_embargo__gte=self.tiene_embargos,
            acepta_reporte_negativo__gte=self.tiene_reportes_negativos,
            entidad__activo=True
        )
        return viables

class NotaSeguimiento(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='notas')
    comentario = models.TextField(verbose_name="Observación")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

class MatrizPerfilamiento(models.Model):
    entidad = models.ForeignKey(EntidadConvenio, on_delete=models.CASCADE)
    segmento_cliente = models.CharField(max_length=20, choices=Cliente.PERFIL_CHOICES)
    score_minimo = models.IntegerField()
    antiguedad_minima_meses = models.IntegerField(default=6)
    acepta_embargo = models.BooleanField(default=False)
    acepta_reporte_negativo = models.BooleanField(default=False)

    def __str__(self):
        return f"Regla {self.entidad} - {self.segmento_cliente}"

class Radicacion(models.Model):
    ESTADO_CHOICES = [
        ('01_INGRESADO', 'Lead Ingresado'),
        ('02_DOC_PENDIENTE', 'Pendiente Documentos'),
        ('03_ESTUDIO', 'En Estudio Bancario'),
        ('04_APROBADO', '✅ Aprobado'),
        ('05_RECHAZADO', '❌ Rechazado'),
        ('06_DESEMBOLSADO', '💰 Desembolsado'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='radicaciones')
    entidad = models.ForeignKey(EntidadConvenio, on_delete=models.SET_NULL, null=True, verbose_name="Banco/Entidad")
    monto_solicitado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado_proceso = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='01_INGRESADO')
    diagnostico_riesgo = models.TextField(blank=True, help_text="Notas internas del analista")
    fecha_radicacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rad. {self.id} - {self.cliente.nombre}"

class ArchivoAdjunto(models.Model):
    TIPO_DOC = [('CEDULA', 'Cédula'), ('LABORAL', 'Certificado Laboral'), ('PAGO', 'Desprendibles'), ('OTROS', 'Otros')]
    radicacion = models.ForeignKey(Radicacion, on_delete=models.CASCADE, related_name='archivos')
    tipo_documento = models.CharField(max_length=20, choices=TIPO_DOC, default='OTROS')
    archivo = models.FileField(upload_to='radicaciones/%Y/%m/%d/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

class ContenidoMultimedia(models.Model):
    TITULOS_SECCION = [
        ('INICIO', 'Banner Principal'),
        ('NOSOTROS', 'Sección Nosotros'),
        ('VIDEO', 'Video Corporativo'),
    ]
    seccion = models.CharField(max_length=20, choices=TITULOS_SECCION)
    titulo = models.CharField(max_length=200)
    imagen = models.ImageField(upload_to='multimedia/', null=True, blank=True)
    video_url = models.URLField(help_text="Enlace de YouTube o Vimeo", null=True, blank=True)
    activo = models.BooleanField(default=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):  # Cambiado de __clase__ a __str__ para que funcione en el Admin
        return f"{self.seccion} - {self.titulo}"
