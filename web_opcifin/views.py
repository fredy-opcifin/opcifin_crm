from django.shortcuts import render
# Añadimos 'ContenidoMultimedia' a la importación
from gestion_financiera.models import Cliente, ArchivoAdjunto, Radicacion, ContenidoMultimedia
import uuid 
from datetime import datetime

def home(request):
    # 1. Traemos las 9 imágenes activas de la base de datos
    multimedia = ContenidoMultimedia.objects.filter(activo=True)
    
    # 2. Imprimimos en la terminal para confirmar la conexión
    print(f"DEBUG: Se encontraron {multimedia.count()} imágenes activas para el carrusel")
    
    # 3. PASO CLAVE: Le entregamos la variable 'multimedia' al HTML
    return render(request, 'web_opcifin/index.html', {'multimedia': multimedia})

def registro_cliente(request):
    ahora = datetime.now().hour
    # Solo permitir de 8-12 y 14-17 (2pm a 5pm)
    if (8 <= ahora < 17):
        # ... procesar la radicación ...
        return render(request, 'registro.html')
    else:
        return render(request, 'fuera_de_horario.html')    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        codigo_temporal = f"WEB-{str(uuid.uuid4())[:8]}"
        nuevo_cliente = Cliente.objects.create(
            nombre=nombre,
            documento_identidad=codigo_temporal,
            perfil_laboral="PENDIENTE"
        )
        radicacion = Radicacion.objects.create(
            cliente=nuevo_cliente,
            estado_proceso='RADICADO'
        )
        archivos = request.FILES
        for nombre_campo, archivo in archivos.items():
            ArchivoAdjunto.objects.create(
                radicacion=radicacion,
                tipo_documento=nombre_campo.upper(),
                archivo=archivo
            )
        return render(request, 'web_opcifin/exito.html', {'nombre': nombre})
    return render(request, 'web_opcifin/registro.html')

def nosotros(request):
    return render(request, 'web_opcifin/nosotros.html')

def servicios(request):
    multimedia = ContenidoMultimedia.objects.filter(activo=True)
    return render(request, 'web_opcifin/servicios.html', {'multimedia': multimedia})