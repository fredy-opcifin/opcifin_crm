from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

# --- 1. ENTIDADES Y CONVENIOS ---
class EntidadConvenio(models.Model):
    TIPO_CHOICES = [('BANCO', 'Banco'), ('COOPERATIVA', 'Cooperativa'), ('FINANCIERA', 'Financiera')]
    nombre_entidad = models.CharField(max_length=100)
    tipo_entidad = models.CharField(max_length=20, choices=TIPO_CHOICES)
    activo = models.BooleanField(default=True)
    politica_credito_resumen = models.TextField(blank=True)

    def __str__(self):
        return self.nombre_entidad

# --- 2. PERFIL DE ASESOR ---

class PerfilAsesor(models.Model):
    ESTATUS_CHOICES = [('Activo', 'Activo'), ('Inactivo', 'Inactivo'), ('Vacaciones', 'Vacaciones')]
    CARGO_CHOICES = [('Asesor', 'Asesor'), ('Auxiliar', 'Auxiliar de Radicación'), ('Coordinador', 'Coordinador')]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    cargo = models.CharField(max_length=20, choices=CARGO_CHOICES, default='Asesor')
    estatus = models.CharField(max_length=20, choices=ESTATUS_CHOICES, default='Activo')
    meta_mensual_unidades = models.IntegerField(default=10, help_text="Meta de radicaciones al mes")
    telefono = models.CharField(max_length=20, blank=True)

    def __str__(self):

        return f"{self.usuario.get_full_name()} - {self.cargo}"

# --- 3. CLIENTES ---

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
    agente_asignado = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='clientes_gestion')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return f"{self.nombre} ({self.documento_identidad})"

# --- 4. LEADS (CONSOLIDADOS) ---

class Lead(models.Model):
    NICHOS = [
        ('DOCENTE', 'Docente'), ('PENSIONADO', 'Pensionado'),
        ('SERVIDOR_PUBLICO', 'Servidor Público'), ('FUERZAS_ARMADAS', 'Fuerzas Armadas'),
        ('INDEPENDIENTE', 'Independiente'),
    ]

    ESTADOS = [
        ('NUEVO', 'Nuevo'), ('CONTACTADO', 'Contactado'), ('EN_PROCESO', 'En Proceso'),
        ('DOCUMENTACION', 'Documentación'), ('RADICADO', 'Radicado'),
        ('APROBADO', 'Aprobado'), ('DESEMBOLSADO', 'Desembolsado'), ('RECHAZADO', 'Rechazado'),
    ]

    FUENTES = [
        ('WHATSAPP', 'WhatsApp'), ('FACEBOOK', 'Facebook'), ('INSTAGRAM', 'Instagram'),
        ('TIKTOK', 'TikTok'), ('WEB', 'Sitio Web'), ('REFERIDO', 'Referido'), ('LLAMADA', 'Llamada'),
    ]

    PRIORIDADES = [('BAJA', 'Baja'), ('MEDIA', 'Media'), ('ALTA', 'Alta'), ('URGENTE', 'Urgente')]

    codigo_gestion = models.CharField(max_length=50, unique=True, blank=True)
    nombre_completo = models.CharField(max_length=200)
    cedula = models.CharField(max_length=20, blank=True, null=True)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    nicho = models.CharField(max_length=50, choices=NICHOS)
    fuente = models.CharField(max_length=50, choices=FUENTES)
    ciudad = models.CharField(max_length=100, blank=True)
    departamento = models.CharField(max_length=100, blank=True)
    empleador = models.CharField(max_length=200, blank=True)
    ingreso_mensual = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monto_solicitado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    prioridad = models.CharField(max_length=20, choices=PRIORIDADES, default='MEDIA')
    estado = models.CharField(max_length=50, choices=ESTADOS, default='NUEVO')
    asesor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='leads_asignados')
    notas = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        if not self.codigo_gestion:

            self.codigo_gestion = f"OPC-{timezone.now().year}-{str(uuid.uuid4())[:4].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):

        return f"{self.codigo_gestion} - {self.nombre_completo}"

# --- 5. RADICACIONES ---

class Radicacion(models.Model):
    ESTADO_PROCESO_CHOICES = [
        ('DOCUMENTACION', 'Documentación'),
        ('RADICADO', 'Radicado'),
        ('ESTUDIO', 'En Estudio'),
        ('APROBADO', 'Aprobado'),
        ('DESEMBOLSADO', 'Desembolsado'),
        ('RECHAZADO', 'Rechazado'),
        ('DEVUELTO', 'Devuelto'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='radicaciones')
    entidad = models.ForeignKey(EntidadConvenio, on_delete=models.SET_NULL, null=True, blank=True)
    monto_solicitado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monto_desembolsado = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    asesor_asignado = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='radicaciones_gestion')
    estado_proceso = models.CharField(max_length=20, choices=ESTADO_PROCESO_CHOICES, default='DOCUMENTACION')
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_desembolso = models.DateField(null=True, blank=True)
    diagnostico_riesgo = models.TextField(blank=True)

    def __str__(self):

        return f"Rad. {self.id} - {self.cliente.nombre}"

# --- 6. RECORDATORIOS Y NOTAS ---

class Recordatorio(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recordatorios')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha = models.DateTimeField()
    completado = models.BooleanField(default=False)
    cliente_vinculado = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return f"{self.titulo} - {self.usuario.username}"

class NotaPersonalAsesor(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    ultima_modificacion = models.DateTimeField(auto_now=True)

class ArchivoAdjunto(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='archivos', null=True, blank=True)
    archivo = models.FileField(upload_to='adjuntos_leads/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

class Resena(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='resenas_lead', null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='resenas_cliente', null=True, blank=True)
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    comentario = models.TextField()
    puntuacion = models.IntegerField(default=5)
    fecha_creacion = models.DateTimeField(auto_now_add=True)