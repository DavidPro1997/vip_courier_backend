from flask import Flask, request, jsonify
from app.services import ObtenerUsuario, Direccion, Paquete
from flask_cors import CORS

app = Flask(__name__)

# Configuración de CORS específica con encabezados y métodos permitidos
CORS(app, resources={r"/*": {"origins": ["http://dev.vipcourier_v2.com","https://app.vipcourier.com.ec"]}}, 
     supports_credentials=True, 
     allow_headers=["Content-Type", "Authorization"],
     methods=["POST", "OPTIONS", "GET", "DELETE"])

@app.route('/')
def index():
    return "¡Bienvenido a VIP Courier!"

@app.route('/verificarSesion', methods=['GET'])
def token():
    auth_header = request.headers.get('Authorization')
    respuesta = ObtenerUsuario.verificarToken(auth_header)
    return jsonify(respuesta)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    respuesta = ObtenerUsuario.iniciarSesion(data.get('correo'), data.get('password'))
    return jsonify(respuesta)

@app.route('/registrarUsuario', methods=['POST'])
def registrarUsuario():
    data = request.json
    respuesta = ObtenerUsuario.anadir(data)
    return jsonify(respuesta)

@app.route('/datosPersonales', methods=['GET'])
def datos():
    auth_header = request.headers.get('Authorization')
    respuesta = ObtenerUsuario.datosPersonales(auth_header)
    return jsonify(respuesta)

@app.route('/editarFotografia', methods=['POST'])
def editarFoto():
    auth_header = request.headers.get('Authorization')
    data = request.json
    respuesta = ObtenerUsuario.editarFotografia(auth_header, data)
    return jsonify(respuesta)

@app.route('/editarDatosPersonales', methods=['POST'])
def editarDatos():
    auth_header = request.headers.get('Authorization')
    data = request.json
    respuesta = ObtenerUsuario.editarDatosPersonales(auth_header, data)
    return jsonify(respuesta)

@app.route('/editarPassword', methods=['POST'])
def editarPassword():
    auth_header = request.headers.get('Authorization')
    data = request.json
    respuesta = ObtenerUsuario.editarPassword(auth_header, data)
    return jsonify(respuesta)

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

@app.route('/validarTracking/<int:tracking>', methods=['GET'])
def validarTracking(tracking):
    auth_header = request.headers.get('Authorization')
    respuesta = Paquete.validar_tracking(auth_header, tracking)
    return jsonify(respuesta)







@app.route('/ejemploTOken', methods=['GET'])
def token5():
    auth_header = request.headers.get('Authorization')
    respuesta = ObtenerUsuario.obtenerToken(auth_header)
    return jsonify(respuesta)





@app.route('/ejemplo', methods=['POST'])
def ejmeplo():
    data = request.json
    auth_header = request.headers.get('Authorization')
    respuesta = ObtenerUsuario.verificarSesion(data.get('correo'), data.get('password'), auth_header)
    return jsonify(respuesta)