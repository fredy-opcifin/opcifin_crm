from django.db import models
from django.contrib.auth.models import User

# --- ENTIDADES ---
class EntidadConvenio(models.Model):
    TIPO_CHOICES = [('BANCO', 'Banco'), ('COOPERATIVA', 'Cooperativa'), ('FINANCIERA', 'Financiera')]
    nombre_entidad = models.CharField(max_length=100)
    tipo_entidad = models.CharField(max_length=20, choices=TIPO_CHOICES)
    activo = models.BooleanField(default=True)
    politica_credito_resumen = models.TextField(blank=True)

    def __str__(self):
        return self.nombre_entidad

# --- CLIENTES ---
class Cliente(models.Model):
    PERFIL_CHOICES = [
        ('PENSIONADO', 'Pensionado'), 
        ('DOCENTE', 'Docente'), 
        ('FUERZA_PUBLICA', 'Fuerza Pública'),
        ('PUBLICO', 'Empleado Público'), 
        ('PRIVADO', 'Empleado Privado'),
        ('OTRO', 'Otro / Independiente')
    ]
    nombre = models.CharField(max_length=200)
    documento_identidad = models.CharField(max_length=50, unique=True)
    email = models.EmailField(verbose_name="Correo Electrónico", null=True, blank=True)
    telefono = models.CharField(max_length=15, verbose_name="Número de Teléfono", null=True, blank=False)
    perfil_laboral = models.CharField(max_length=20, choices=PERFIL_CHOICES)
    score_datacredito = models.IntegerField(default=0)
    tiene_embargos = models.BooleanField(default=False)
    tiene_reportes_negativos = models.BooleanField(default=False)
    agente_asignado = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.documento_identidad})"

# --- RADICACIONES ---
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
    entidad = models.ForeignKey(EntidadConvenio, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Banco/Entidad")
    monto_solicitado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado_proceso = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='01_INGRESADO')
    diagnostico_riesgo = models.TextField(blank=True, help_text="Notas internas del analista")
    fecha_radicacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rad. {self.id} - {self.cliente.nombre}"

# --- OTROS MODELOS ---
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

class ArchivoAdjunto(models.Model):
    radicacion = models.ForeignKey(Radicacion, on_delete=models.CASCADE, related_name='archivos')
    archivo = models.FileField(upload_to='radicaciones/%Y/%m/%d/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

class ContenidoMultimedia(models.Model):
    seccion = models.CharField(max_length=20)
    titulo = models.CharField(max_length=200)
    activo = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.seccion} - {self.titulo}"