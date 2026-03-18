from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count
from django.http import JsonResponse
from .models import Cliente, Radicacion, Lead, PerfilAsesor, Recordatorio, NotaPersonalAsesor
from django.core.mail import send_mail


# --- 1. VISTAS PÚBLICAS (SITIO WEB) ---
def home(request):
    return render(request, 'web_opcifin/index.html')

# --- Función de Captura (Web) ---
def capturar_lead(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        telefono = request.POST.get('telefono')
        ciudad = request.POST.get('ciudad')  # Sincronizado con el name del HTML
        monto = request.POST.get('monto_interes')
        ingresos = request.POST.get('ingresos')

        Lead.objects.create(
            nombre_completo=nombre,
            telefono=telefono,
            ciudad=ciudad if ciudad else "No registra",
            monto_solicitado=monto if monto else 0,
            ingreso_mensual=ingresos if ingresos else 0,
            nicho='INDEPENDIENTE',
            fuente='WEB'
        )

        try:
             send_mail(
                 'Nuevo Lead desde la Web',
                 f'El cliente {nombre} ha solicitado un crédito de {monto}.',
                 'tu-correo@gmail.com',
                 ['correo-donde-recibes@gmail.com'],
                 fail_silently=False,
             )
        except:
             pass

        messages.success(request, "Recibimos tu solicitud, pronto nos contactaremos.")
        return redirect('home')
    return render(request, 'web_opcifin/index.html')

def registro_cliente(request):
    return render(request, 'web_opcifin/registro.html')

# --- 2. AUTENTICACIÓN ---
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_moderno')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard_moderno')
    else:
        form = AuthenticationForm()
    return render(request, 'dashboard/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

# --- 3. DASHBOARD ---
@login_required
def dashboard_moderno(request):
    leads = Lead.objects.all()
    radicaciones = Radicacion.objects.all()
    nicho_qs = leads.values('nicho').annotate(total=Count('id'))

    context = {
        'total_leads': leads.count(),
        'en_estudio': radicaciones.filter(estado_proceso='ESTUDIO').count(),
        'aprobados': radicaciones.filter(estado_proceso='APROBADO').count(),
        'nicho_labels': [item['nicho'] for item in nicho_qs],
        'nicho_values': [item['total'] for item in nicho_qs],
    }
    return render(request, 'dashboard/main.html', context)

# --- 4. GESTIÓN DE LEADS ---
@login_required
def leads_list(request):
    leads = Lead.objects.all().order_by('-fecha_creacion')

    # Capturamos los filtros de la URL
    search = request.GET.get('search')
    estado = request.GET.get('estado')
    nicho = request.GET.get('nicho')
    fuente = request.GET.get('fuente')
    # Nota: No filtramos por asesor aún para no complicar, pero enviamos la lista

    if search:
        leads = leads.filter(nombre_completo__icontains=search) | leads.filter(cedula__icontains=search)
    if estado:
        leads = leads.filter(estado=estado)
    if nicho:
        leads = leads.filter(nicho=nicho)
    if fuente:
        leads = leads.filter(fuente=fuente)

    context = {
        'leads': leads,
        'estados': Lead.ESTADOS,
        'nichos': Lead.NICHOS,
        'fuentes': Lead.FUENTES,
        'asesores': User.objects.filter(is_active=True),
    }
    return render(request, 'dashboard/leads_list.html', context)

@login_required
def registro_manual(request):
    if request.method == 'POST':
        Lead.objects.create(
            nombre_completo=request.POST.get('nombre_completo'),
            telefono=request.POST.get('telefono'),
            cedula=request.POST.get('cedula'),
            email=request.POST.get('email'),
            nicho=request.POST.get('nicho', 'INDEPENDIENTE'),
            fuente=request.POST.get('fuente', 'LLAMADA'),
            ingreso_mensual=request.POST.get('ingreso_mensual') or 0,
            monto_solicitado=request.POST.get('monto_solicitado') or 0,
            asesor=request.user
        )
        return redirect('leads_list')
    return render(request, 'dashboard/registro_manual.html')

@login_required
def eliminar_lead(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    lead.delete()
    messages.success(request, "Lead eliminado correctamente.")
    return redirect('leads_list')

# --- Función para el Dashboard (JSON) ---
@login_required
def detalle_lead_json(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    # Creamos el paquete de datos para el Dashboard
    data = {
        'nombre': lead.nombre_completo,
        'cedula': lead.cedula if lead.cedula else "No registra", # <-- ESTA LÍNEA FALTABA
        'telefono': lead.telefono,
        'ciudad': lead.ciudad if lead.ciudad else "No registra",
        'estado': lead.get_estado_display(),
        'ingresos': float(lead.ingreso_mensual or 0),
        'monto': float(lead.monto_solicitado or 0),
    }
    return JsonResponse(data)

# --- 5. OPERACIONES ---
@login_required
def convertir_a_radicacion(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    # Validamos cedula segun tu modelo Cliente
    cliente, _ = Cliente.objects.get_or_create(
        documento_identidad=lead.cedula if lead.cedula else f"TEMP-{lead.id}",
        defaults={'nombre': lead.nombre_completo, 'telefono': lead.telefono}
    )
    Radicacion.objects.create(
        cliente=cliente,
        monto_solicitado=lead.monto_solicitado,
        estado_proceso='ESTUDIO',
        asesor_asignado=request.user
    )
    lead.estado = 'RADICADO'
    lead.save()
    messages.success(request, "Lead convertido a radicación exitosamente.")
    return redirect('radicaciones_list')

@login_required
def radicaciones_list(request):
    rads = Radicacion.objects.all().order_by('-fecha_inicio')
    return render(request, 'dashboard/radicaciones_list.html', {'radicaciones': rads})

@login_required
def asesores_list(request):
    return render(request, 'dashboard/asesores_list.html', {'equipo': PerfilAsesor.objects.all()})

@login_required
def recordatorios_view(request):
    recs = Recordatorio.objects.filter(usuario=request.user)
    nota_obj, _ = NotaPersonalAsesor.objects.get_or_create(usuario=request.user)
    return render(request, 'dashboard/recordatorios.html', {'recordatorios': recs, 'nota_personal': nota_obj.contenido})

@login_required
def crear_actividad(request, lead_id):
    return JsonResponse({'status': 'success', 'message': 'Actividad registrada'})

# --- 6. VISTAS WEB Y SERVICIOS ---
def nosotros(request): return render(request, 'web_opcifin/nosotros.html')
def atencion_cliente(request): return render(request, 'web_opcifin/atencion_cliente.html')
def hub_creditos(request): return render(request, 'web_opcifin/hub_creditos.html')
def hub_servicios(request): return render(request, 'web_opcifin/hub_servicios.html')
def libranza(request): return render(request, 'web_opcifin/servicios/lineas/libranza.html')
def hipotecario(request): return render(request, 'web_opcifin/servicios/lineas/hipotecario.html')
def prestamos_personales(request): return render(request, 'web_opcifin/servicios/lineas/prestamos_personales.html')
def compra_cartera(request): return render(request, 'web_opcifin/servicios/gestion/compra_cartera.html')
def hipotecas(request): return render(request, 'web_opcifin/servicios/gestion/hipotecas.html')
def eliminacion_reportes(request): return render(request, 'web_opcifin/servicios/gestion/eliminacion_reportes.html')
def retanqueos(request): return render(request, 'web_opcifin/servicios/gestion/retanqueos.html')
def convenios(request): return render(request, 'web_opcifin/servicios/convenios.html')
def guardar_resena(request): return JsonResponse({'status': 'ok'})