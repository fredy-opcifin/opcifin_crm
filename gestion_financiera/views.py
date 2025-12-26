from django.shortcuts import render
from .models import ContenidoMultimedia

def home(request):
    # Traemos todos los elementos que marcaste como activos en el Admin
    # Asegúrate de que el nombre de la variable sea 'multimedia'
    multimedia = ContenidoMultimedia.objects.filter(activo=True)
    
    # Enviamos la variable al diccionario de contexto
    return render(request, 'web_opcifin/index.html', {'multimedia': multimedia})