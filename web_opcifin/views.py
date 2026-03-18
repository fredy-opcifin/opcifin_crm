from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.http import JsonResponse
from .models import Cliente, Radicacion, Lead, PerfilAsesor, Recordatorio, NotaPersonalAsesor

# --- 1. VISTAS DE NAVEGACIÓN BÁSICA ---
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard_moderno')
    return render(request, 'web_opcifin/index.html') # O tu landing page

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard_moderno')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

# --- 2. DASHBOARD Y GESTIÓN INTERNA ---
@login_required
def dashboard_moderno(request):
    radicaciones = Radicacion.objects.all()
    context = {
        'total_leads': Lead.objects.count(),
        'total_clientes': Cliente.objects.count(),
        'radicaciones_estudio_count': radicaciones.filter(estado_proceso='ESTUDIO').count(),
        'radicaciones_aprobadas_count': radicaciones.filter(estado_proceso='APROBADO').count(),
        'monto_total': radicaciones.aggregate(Sum('monto_solicitado'))['monto_solicitado__sum'] or 0,
        'ultimos_leads': Lead.objects.all().order_by('-fecha_creacion')[:5],
    }
    return render(request, 'dashboard/main.html', context)

@login_required
def leads_list(request):
    leads = Lead.objects.all().order_by('-fecha_creacion')
    return render(request, 'dashboard/leads_list.html', {'leads': leads})

@login_required
def radicaciones_list(request):
    radicaciones = Radicacion.objects.all().order_by('-fecha_inicio')
    return render(request, 'dashboard/radicaciones_list.html', {'radicaciones': radicaciones})

@login_required
def asesores_list(request):
    perfiles = PerfilAsesor.objects.all()
    return render(request, 'dashboard/asesores_list.html', {'equipo': perfiles})

@login_required
def recordatorios_view(request):
    recordatorios = Recordatorio.objects.filter(usuario=request.user)
    nota_obj, _ = NotaPersonalAsesor.objects.get_or_create(usuario=request.user)
    return render(request, 'dashboard/recordatorios.html', {'recordatorios': recordatorios, 'nota_personal': nota_obj.contenido})

@login_required
def convertir_a_radicacion(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    cliente, _ = Cliente.objects.get_or_create(
        documento_identidad=lead.cedula,
        defaults={'nombre': lead.nombre, 'telefono': lead.telefono, 'agente_asignado': request.user}
    )
    Radicacion.objects.create(cliente=cliente, monto_solicitado=lead.monto_solicitado, asesor_asignado=request.user)
    lead.estado = 'RADICADO'
    lead.save()
    messages.success(request, "Lead convertido a radicación.")
    return redirect('radicaciones_list')

# --- 3. CAPTACIÓN WEB Y SERVICIOS ---
def capturar_lead(request):
    if request.method == 'POST':
        Lead.objects.create(
            nombre=request.POST.get('nombre'),
            cedula=request.POST.get('cedula'),
            telefono=request.POST.get('telefono'),
            email=request.POST.get('email'),
            fuente_captacion='WEB'
        )
        messages.success(request, "¡Gracias! Pronto nos contactaremos contigo.")
        return redirect('home')
    return render(request, 'web_opcifin/registro.html')

def registro_cliente(request): return render(request, 'web_opcifin/registro.html')
def nosotros(request): return render(request, 'web_opcifin/nosotros.html')
def atencion_cliente(request): return render(request, 'web_opcifin/atencion_cliente.html')
def guardar_resena(request): return JsonResponse({'status': 'ok'})
def convenios(request): return render(request, 'web_opcifin/servicios/convenios.html')
def hub_creditos(request): return render(request, 'web_opcifin/hub_creditos.html')
def hub_servicios(request): return render(request, 'web_opcifin/hub_servicios.html')
def libranza(request): return render(request, 'web_opcifin/servicios/lineas/libranza.html')
def hipotecario(request): return render(request, 'web_opcifin/servicios/lineas/hipotecario.html')
def prestamos_personales(request): return render(request, 'web_opcifin/servicios/lineas/prestamos_personales.html')
def compra_cartera(request): return render(request, 'web_opcifin/servicios/gestion/compra_cartera.html')
def hipotecas(request): return render(request, 'web_opcifin/servicios/gestion/hipotecas.html')
def eliminacion_reportes(request): return render(request, 'web_opcifin/servicios/gestion/eliminacion_reportes.html')
def retanqueos(request): return render(request, 'web_opcifin/servicios/gestion/retanqueos.html')