from flask import Flask, render_template, request, send_file
from datetime import date
from PIL import Image, ImageDraw, ImageFont
import os
import requests
from io import BytesIO
import uuid

app = Flask(__name__)

# Lista de materias con sus respectivos profesores
materias = [
    ("Aplicaciones Moviles", "Claudio Espiricueta Diana Patricia"),
    ("Ética, Sustentabilidad y Responsabilidad Social", "Cuellar Berlanga Juan Antonio"),
    ("Formación de Emprendedores", "Gonzalez Solis Mariana De Jesus"),
    ("La Vida en México: Política, Economía e Historia", "Gomez Macias Edith"),
    ("Literatura", "Rángel García César Alejandro"),
    ("Modelo Vista Controlador", "Ramos Martinez Miriam Alejandra"),
    ("Programación Orientada a Objetos", "Claudio Espiricueta Diana Patricia"),
    ("Proyecto de Vida", "Vargas Martinez Ramiro Emmanuel"),
    ("Proyectos Administrativos Web", "Martinez Castillo Julian De Jesus")
]

# URLs para los logos
logo_uanl_url = "https://uanl.mx/wp-content/uploads/2020/06/uanl.png"
logo_prepa_url = "https://preparatoria8.uanl.mx/imagenes/logo_prepa.png"

os.makedirs('static/images', exist_ok=True)

def descargar_imagen(url, verificar_ssl=True):
    try:
        response = requests.get(url, verify=verificar_ssl)
        return Image.open(BytesIO(response.content))
    except Exception as e:
        print(f"Error al descargar imagen de {url}: {e}")
        img = Image.new('RGBA', (200, 200), color=(255, 255, 255, 0))
        d = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        texto = "Prepa 8" if "prepa" in url.lower() else "UANL"
        d.text((100, 100), texto, fill=(0, 0, 0), font=font, anchor="mm")
        return img

def crear_portada_imagen(nombre_alumno, grupo, semestre, materia, profesor, actividad):
    ancho, alto = 850, 1100
    imagen = Image.new('RGB', (ancho, alto), color=(255, 255, 255))
    dibujo = ImageDraw.Draw(imagen)
    
    try:
        fuente_titulo = ImageFont.truetype("arialbd.ttf", 36)
        fuente_subtitulo = ImageFont.truetype("arial.ttf", 26)
        fuente_datos = ImageFont.truetype("arial.ttf", 24)
    except:
        fuente_titulo = fuente_subtitulo = fuente_datos = ImageFont.load_default()

    logo_uanl = descargar_imagen(logo_uanl_url)
    logo_prepa = descargar_imagen(logo_prepa_url, verificar_ssl=False)
    
    logo_uanl.thumbnail((160, 160), Image.LANCZOS)
    logo_prepa.thumbnail((130, 130), Image.LANCZOS)
    
    imagen.paste(logo_uanl, (60, 60), logo_uanl if logo_uanl.mode == 'RGBA' else None)
    imagen.paste(logo_prepa, (ancho - 190, 70), logo_prepa if logo_prepa.mode == 'RGBA' else None)
    
    # Línea divisoria
    dibujo.line([(50, 250), (ancho - 50, 250)], fill=(0, 43, 121), width=3)

    # Títulos
    dibujo.text((ancho // 2, 280), "Universidad Autónoma de Nuevo León", fill=(0, 43, 121), font=fuente_titulo, anchor="mm")
    dibujo.text((ancho // 2, 330), "Preparatoria 8", fill=(0, 43, 121), font=fuente_subtitulo, anchor="mm")

    y_inicio = 440
    espacio = 60
    datos = [
        f"Materia: {materia}",
        f"Grupo: {grupo}",
        f"Semestre: {semestre}",
        f"Alumno: {nombre_alumno}",
        f"Profesor: {profesor}",
        f"Actividad: {actividad}",
        f"Fecha: {date.today().strftime('%d/%m/%Y')}"
    ]

    for dato in datos:
        dibujo.text((ancho // 2, y_inicio), dato, fill=(0, 0, 0), font=fuente_datos, anchor="mm")
        y_inicio += espacio

    unique_id = uuid.uuid4().hex[:8]
    nombre_archivo = f"static/images/Portada_{materia.replace(' ', '_')}_{unique_id}.png"
    imagen.save(nombre_archivo)
    return nombre_archivo

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nombre_alumno = request.form['nombre']
        grupo = request.form['grupo']
        semestre = request.form['semestre']
        materia_nombre = request.form['materia']  # Ahora recibe el nombre directamente
        actividad = request.form['actividad']
        
        # Buscar la materia seleccionada por nombre
        selected_materia = next((m for m in materias if m[0] == materia_nombre), None)
        
        if selected_materia:
            materia, profesor = selected_materia
            imagen_portada = crear_portada_imagen(nombre_alumno, grupo, semestre, materia, profesor, actividad)
            
            fecha_actual = date.today().strftime('%d/%m/%Y')
            
            return render_template('resultado.html', 
                                materia=materia,
                                nombre_alumno=nombre_alumno,
                                grupo=grupo,
                                semestre=semestre,
                                profesor=profesor,
                                actividad=actividad,
                                imagen_portada=imagen_portada.replace('static/', ''),
                                fecha=fecha_actual)
        else:
            return "Materia no encontrada", 400
    
    # Para GET requests, pasar la lista original de materias
    return render_template('index.html', materias=materias)

if __name__ == '__main__':
    app.run(debug=True)