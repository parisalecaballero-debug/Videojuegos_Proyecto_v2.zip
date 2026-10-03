import json
import os
import uuid
from django.conf import settings
from django.shortcuts import render, redirect

USUARIOS_PATH = os.path.join(settings.BASE_DIR, 'appVideojuegos', 'data', 'usuarios.json')
JUEGOS_PATH = os.path.join(settings.BASE_DIR, 'appVideojuegos', 'data', 'videojuegos.json')


def leer_json(ruta):
    with open(ruta, 'r', encoding='utf-8') as archivo:
        return json.load(archivo)


def escribir_json(ruta, datos):
    with open(ruta, 'w', encoding='utf-8') as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)


def esta_logueado(request):
    return request.session.get('usuario') is not None


def guardar_imagen(imagen_file):
    carpeta = os.path.join(settings.MEDIA_ROOT, 'videojuegos')
    os.makedirs(carpeta, exist_ok=True)
    extension = os.path.splitext(imagen_file.name)[1]
    nombre_archivo = f"{uuid.uuid4().hex}{extension}"
    ruta_completa = os.path.join(carpeta, nombre_archivo)
    with open(ruta_completa, 'wb+') as destino:
        for chunk in imagen_file.chunks():
            destino.write(chunk)
    return f"videojuegos/{nombre_archivo}"


def inicio(request):
    return render(request, 'appVideojuegos/inicio.html')


def login_view(request):
    error = None
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        contrasena = request.POST.get('contrasena')
        usuarios = leer_json(USUARIOS_PATH)
        for u in usuarios:
            if u['usuario'] == usuario and u['contrasena'] == contrasena:
                request.session['usuario'] = usuario
                return redirect('consultar')
        error = 'Usuario o contraseña incorrectos'
    return render(request, 'appVideojuegos/login.html', {'error': error})


def logout_view(request):
    request.session.flush()
    return redirect('inicio')


def consultar(request):
    if not esta_logueado(request):
        return redirect('login')
    juegos = leer_json(JUEGOS_PATH)
    return render(request, 'appVideojuegos/consultar.html', {'juegos': juegos})


def registrar(request):
    if not esta_logueado(request):
        return redirect('login')
    mensaje = None
    if request.method == 'POST':
        juegos = leer_json(JUEGOS_PATH)
        nuevo_id = max([j['id'] for j in juegos], default=0) + 1
        nuevo_juego = {
            'id': nuevo_id,
            'titulo': request.POST.get('titulo'),
            'genero': request.POST.get('genero'),
            'plataforma': request.POST.get('plataforma'),
            'anio': int(request.POST.get('anio')),
            'desarrollador': request.POST.get('desarrollador'),
            'calificacion': int(request.POST.get('calificacion')),
            'imagen': None,
            'progreso': 0,
        }
        if 'imagen' in request.FILES:
            nuevo_juego['imagen'] = guardar_imagen(request.FILES['imagen'])
        juegos.append(nuevo_juego)
        escribir_json(JUEGOS_PATH, juegos)
        mensaje = 'Videojuego registrado correctamente'
    return render(request, 'appVideojuegos/registrar.html', {'mensaje': mensaje})


def modificar(request, id):
    if not esta_logueado(request):
        return redirect('login')
    juegos = leer_json(JUEGOS_PATH)
    juego = next((j for j in juegos if j['id'] == id), None)
    if juego is None:
        return redirect('consultar')
    if request.method == 'POST':
        juego['titulo'] = request.POST.get('titulo')
        juego['genero'] = request.POST.get('genero')
        juego['plataforma'] = request.POST.get('plataforma')
        juego['anio'] = int(request.POST.get('anio'))
        juego['desarrollador'] = request.POST.get('desarrollador')
        juego['calificacion'] = int(request.POST.get('calificacion'))
        if 'imagen' in request.FILES:
            juego['imagen'] = guardar_imagen(request.FILES['imagen'])
        escribir_json(JUEGOS_PATH, juegos)
        return redirect('consultar')
    return render(request, 'appVideojuegos/modificar.html', {'juego': juego})


def acerca(request):
    return render(request, 'appVideojuegos/acerca.html')


def mi_progreso(request):
    if not esta_logueado(request):
        return redirect('login')
    juegos = leer_json(JUEGOS_PATH)
    if request.method == 'POST':
        id_juego = int(request.POST.get('id'))
        nuevo_progreso = int(request.POST.get('progreso', 0))
        for j in juegos:
            if j['id'] == id_juego:
                j['progreso'] = nuevo_progreso
        escribir_json(JUEGOS_PATH, juegos)
    juegos_ordenados = sorted(juegos, key=lambda j: j.get('progreso', 0))
    return render(request, 'appVideojuegos/mi_progreso.html', {'juegos': juegos_ordenados})
