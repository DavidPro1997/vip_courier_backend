from flask import Flask, request, jsonify
from app.services import Usuario, Direccion, Paquete, Correo
from flask_cors import CORS
import logging
import os



log_file_path = '/var/log/gunicorn/app.log'

if os.name == 'posix':  # Ubuntu o cualquier sistema UNIX
    # Configuración para logs en la salida estándar y en un archivo
    handler = StreamHandler()  # Log en la salida estándar (stdout)
    handler.setLevel(logging.INFO)  # O el nivel que necesites, como DEBUG
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))  # Formato de los logs

    # Archivo de log
    file_handler = FileHandler(log_file_path)  # Log en archivo
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # Agregar ambos handlers
    app.logger.addHandler(handler)  # Para la salida estándar
    app.logger.addHandler(file_handler)  # Para el archivo

    # También configuramos el logging básico
    logging.basicConfig(
        level=logging.DEBUG,  # El nivel de log, puedes cambiarlo según lo necesites
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            handler,  # Manejador para la salida estándar
            file_handler  # Manejador para el archivo
        ]
    )

else:
    # Configuración para otros sistemas operativos si es necesario
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Configuración de CORS específica con encabezados y métodos permitidos
CORS(app, resources={r"/*": {"origins": ["http://dev.vipcourier_v2.com","https://vipcourier.com.ec","http://vipcourier.com.ec"]}}, 
     supports_credentials=True, 
     allow_headers=["Content-Type", "Authorization"],
     methods=["POST", "OPTIONS", "GET", "DELETE"])

@app.route('/')
def index():
    return "¡Bienvenido al backend de VIP Courier!"


######################################### CORREO ###########################################
@app.route('/enviarCorreoVerificacion', methods=['POST'])
def enviarCorreo():
    data = request.json
    respuesta = Correo.verificar_correo(data)
    return jsonify(respuesta)



########################################## SESION ###########################################

@app.route('/verificarSesion', methods=['GET'])
def token():
    auth_header = request.headers.get('Authorization')
    respuesta = Usuario.verificarToken(auth_header)
    return jsonify(respuesta)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    respuesta = Usuario.iniciarSesion(data.get('correo'), data.get('password'))
    return jsonify(respuesta)


######################################### USUARIOS ###################################


@app.route('/registrarUsuario', methods=['POST'])
def registrarUsuario():
    data = request.json
    respuesta = Usuario.anadir(data)
    return jsonify(respuesta)

@app.route('/datosPersonales', methods=['GET'])
def datos():
    auth_header = request.headers.get('Authorization')
    respuesta = Usuario.datosPersonales(auth_header)
    return jsonify(respuesta)

@app.route('/editarFotografia', methods=['POST'])
def editarFoto():
    auth_header = request.headers.get('Authorization')
    data = request.json
    respuesta = Usuario.editarFotografia(auth_header, data)
    return jsonify(respuesta)

@app.route('/editarDatosPersonales', methods=['POST'])
def editarDatos():
    auth_header = request.headers.get('Authorization')
    data = request.json
    respuesta = Usuario.editarDatosPersonales(auth_header, data)
    return jsonify(respuesta)

@app.route('/editarPassword', methods=['POST'])
def editarPassword():
    auth_header = request.headers.get('Authorization')
    data = request.json
    respuesta = Usuario.editarPassword(auth_header, data)
    return jsonify(respuesta)


@app.route('/restablecerPassword', methods=['POST'])
def restablecerPassword():
    data = request.json
    respuesta = Usuario.restablecerPassword(data["correo"])
    return jsonify(respuesta)


##################################### DIRECCIONES #######################################


@app.route('/agregarDireccion', methods=['POST'])
def addDireccion():
    auth_header = request.headers.get('Authorization')
    data = request.json
    respuesta = Direccion.agregar_direccion(auth_header, data)
    return jsonify(respuesta)

@app.route('/obtenerDirecciones', methods=['GET'])
def direcciones():
    auth_header = request.headers.get('Authorization')
    respuesta = Direccion.obtener_direccion(auth_header)
    return jsonify(respuesta)

@app.route('/eliminarDirecciones/<int:id>', methods=['DELETE'])
def eliminarDirecciones(id):
    auth_header = request.headers.get('Authorization')
    respuesta = Direccion.elimnar_direccion(auth_header, id)
    return jsonify(respuesta)

@app.route('/obtenerDireccion/<int:id>', methods=['GET'])
def direccion(id):
    auth_header = request.headers.get('Authorization')
    respuesta = Direccion.obtener_direccion_unica(auth_header, id)
    return jsonify(respuesta)

@app.route('/editarDireccion/<int:id>', methods=['POST'])
def editDireccion(id):
    auth_header = request.headers.get('Authorization')
    data = request.json
    respuesta = Direccion.editar_direccion(auth_header, data, id)
    return jsonify(respuesta)

@app.route('/principalDireccion/<int:id>', methods=['GET'])
def principalDireccion(id):
    auth_header = request.headers.get('Authorization')
    respuesta = Direccion.setear_principal(auth_header, id)
    return jsonify(respuesta)

@app.route('/ingresoPaquete', methods=['POST'])
def ingresoPaquete():
    auth_header = request.headers.get('Authorization')
    data = request.json
    respuesta = Paquete.agregar_paquete(auth_header, data)
    return jsonify(respuesta)

@app.route('/obtenerPaquetes', methods=['GET'])
def verPaquetes():
    auth_header = request.headers.get('Authorization')
    respuesta = Paquete.obtenerPaquetes(auth_header)
    return jsonify(respuesta)

@app.route('/obtenerPaquetesCompletos', methods=['POST'])
def verPaquetes_completo():
    auth_header = request.headers.get('Authorization')
    data = request.json
    respuesta = Paquete.obtenerPaquetes_completos(auth_header, data["buscador"])
    return jsonify(respuesta)

@app.route('/validarTracking/<int:tracking>', methods=['GET'])
def validarTracking(tracking):
    auth_header = request.headers.get('Authorization')
    respuesta = Paquete.validar_tracking(auth_header, tracking)
    return jsonify(respuesta)

@app.route('/descargarVoucherTracking/<int:idTracking>', methods=['GET'])
def descargarVoucher(idTracking):
    auth_header = request.headers.get('Authorization')
    respuesta = Paquete.descargar_tracking(auth_header, idTracking)
    return jsonify(respuesta)









@app.route('/ejemploTOken', methods=['GET'])
def token5():
    auth_header = request.headers.get('Authorization')
    respuesta = Usuario.obtenerToken(auth_header)
    return jsonify(respuesta)





@app.route('/ejemplo', methods=['POST'])
def ejmeplo():
    data = request.json
    auth_header = request.headers.get('Authorization')
    respuesta = Usuario.verificarSesion(data.get('correo'), data.get('password'), auth_header)
    return jsonify(respuesta)