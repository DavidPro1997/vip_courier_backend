from app.models import UsuarioBase, DireccionesBase, TrackingBase
import jwt
import base64, re, glob
import os
import bcrypt
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime, timedelta, timezone
import random
import string
import mimetypes

SECRET_KEY = 'play4652+'
from_email = "davidayd20@gmail.com"  # Remitente
password = "pwtk onyz vxtk xovl"  # Contraseña o App Password si usas Gmail con verificación en dos pasos
smtp_server = "smtp.gmail.com"  # Servidor SMTP de Gmail
smtp_port = 587  # Puerto SMTP

class Usuario:
    @staticmethod
    def datosPersonales(auth):
        if auth:
            validacionToken = Usuario.verificarToken(auth)
            if validacionToken["estado"] == True:
                usuario = UsuarioBase.obtener_usuario(validacionToken["datos"]["id"])
                if usuario["imagen"] is not None:
                    imagen = Imagen.convertir_imagen_a_base64(usuario["imagen"])
                    usuario["imgBase64"] = imagen
                else : 
                    usuario["imgBase64"] = None
                return {"estado":True, "mensaje": "Se ha encontrado usuario", "datos": usuario}
            else:
                return {"estado":False, "mensaje": "No tiene autorización"}
        else:
            return {"estado":False, "mensaje": "No tiene autorización"}
        

    @staticmethod
    def editarDatosPersonales(auth, datos):
        if auth:
            validacionToken = Usuario.verificarToken(auth)
            if validacionToken["estado"] == True:
                log_editar = UsuarioBase.editar_usuario(validacionToken["datos"]["id"], datos.get("telefono"))
                datos = {
                    'id': validacionToken["datos"]["id"],
                    'correo' : validacionToken["datos"]["correo"],
                    'nombre': datos.get("nombres"),
                    'apellido': datos.get("apellidos"),
                    'rol': validacionToken["datos"]["rol"]
                    }
                nuevo_token = Usuario.crearToken(datos)
                log_editar["nuevo_token"] = nuevo_token
                return log_editar
            else:
                return {"estado":False, "mensaje": "No tiene autorización"}
        else:
            return {"estado":False, "mensaje": "No tiene autorización"}
        

    @staticmethod
    def restablecerPassword(correo):
        usu = UsuarioBase.verificar_correo(correo)
        if usu:
            password = Correo.generar_codigo_aleatorio(10)
            encrypted_pasword = Password.encriptar_password(password)
            log_password = UsuarioBase.editar_password(usu[0], encrypted_pasword)
            if log_password["estado"]:
                datos = Correo.armar_correo_restablecer(password)
                log_correo = Correo.enviar_correo(correo,datos["asunto"], datos["cuerpo"])
                if log_correo:
                    return {"estado":True, "mensaje": "Nueva contraseña enviada a su correo"} 
                else:
                    return {"estado":False, "mensaje": "No se ha logrado enviar correo"} 
            return log_password 
        else:
            return {"estado":False, "mensaje": "Correo no existe"}                
            


    @staticmethod
    def editarPassword(auth, datos):
        if auth:
            validacionToken = Usuario.verificarToken(auth)
            if validacionToken["estado"] == True:
                password_actual = UsuarioBase.verificar_password(validacionToken["datos"]["id"])
                if Password.verificar_password_encrip(datos.get("antigua"),password_actual["password"]):
                    if datos.get("nueva") == datos.get("nueva2"):
                        encrypted_pasword = Password.encriptar_password(datos.get("nueva"))
                        log_password = UsuarioBase.editar_password(validacionToken["datos"]["id"], encrypted_pasword)
                        return log_password
                    else:
                        return {"estado":False, "mensaje": "Las nuevas contraseñas no son iguales"}
                else:
                    return {"estado":False, "mensaje": "Contraseña incorrecta"}                
            else:
                return {"estado":False, "mensaje": "No tiene autorización"}
        else:
            return {"estado":False, "mensaje": "No tiene autorización"}

    
    @staticmethod
    def editarFotografia(auth, datos):
        if auth:
            validacionToken = Usuario.verificarToken(auth)
            if validacionToken["estado"] == True:
                if datos.get("imagen") is not None:
                    ruta = Imagen.guardar_imagen_base64(datos.get("imagen"),validacionToken["datos"]["nombre"],validacionToken["datos"]["id"])
                    if ruta:
                        log_imagen = UsuarioBase.insertar_imagen(validacionToken["datos"]["id"], ruta)
                        return log_imagen
                return {"estado":False, "mensaje": "Hubo un error con la imagem"}
            else:
                return {"estado":False, "mensaje": "No tiene autorización"}
        else:
            return {"estado":False, "mensaje": "No tiene autorización"}
             

    @staticmethod
    def iniciarSesion(correo, password):
        if not correo or not password:
            return {"estado":False, "mensaje": "Faltan campos requeridos"}
        else:
            password_encr = UsuarioBase.obteneder_password(correo)
            print(password_encr)
            if password_encr["password"] is not None:
                if Password.verificar_password_encrip(password, password_encr["password"]):
                    usuario = UsuarioBase.usuario_login(correo, password_encr["password"])
                    if usuario: 
                        token = Usuario.crearToken(usuario)
                        usuario["token"] = token
                        return {"estado":True, "mensaje": "Usuario encontrado", "datos":usuario}
                    else:
                        return {"estado":False, "mensaje": "Hubo un error"}      
                else:
                    return {"estado":False, "mensaje": "Password incorrecto"}
            else:
                return {"estado":False, "mensaje": "Email no existe"}
 

    @staticmethod
    def crearToken(datos):
        #se caduca en 30 segundos (pruebas)
        # expiracion = datetime.utcnow() + timedelta(seconds=30)
        #Se caduca en 1 dia 
        expiracion = datetime.now(timezone.utc) + timedelta(days=1)
        payload = {
            'id': datos["id"],
            'correo' : datos["correo"],
            'primerNombre': datos["primerNombre"],
            'primerApellido': datos["primerApellido"],
            'rol': datos["rol"],
            'exp': expiracion.timestamp()
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return token
    

    @staticmethod
    def verificarToken(tokenRecibido):
        try:
            tokenDecodificado = jwt.decode(tokenRecibido, SECRET_KEY, algorithms=['HS256'])
            data = {
                'correo': tokenDecodificado['correo'],
                'id': tokenDecodificado['id'],
                'rol': tokenDecodificado['rol'],
                'primerNombre': tokenDecodificado['primerNombre'],
                'primerApellido': tokenDecodificado['primerApellido'],
                'token': tokenRecibido
                }
            return {"estado":True, "mensaje": "Token válido", "datos":data} # Devuelve el usuario
        except jwt.ExpiredSignatureError:
            print("El token ha expirado")
            return {"estado":False, "mensaje": "El token ha expirado"}
        except jwt.InvalidTokenError:
            print("Token inválido")
            return {"estado":False, "mensaje": "Token inválido"}
        

    @staticmethod
    def anadir(data):
        if Correo.verificarCodigo(data["codigo"], data["correo"]):
            if Usuario.verificarInformacion(data):
                if data.get('password1') == data.get('password2'):
                    if not UsuarioBase.verificar_correo(data.get('correo')):
                        password_encr = Password.encriptar_password(data.get("password1"))
                        usuarioCreado = UsuarioBase.insertar_usuario(data,password_encr)
                        return usuarioCreado
                    else:
                        return {"estado":False, "mensaje": "Usuario ya registrado", "datos":""} # Devuelve el usuario
                else:
                    return {"estado":False, "mensaje": "Contraseñas no coinciden", "datos":""} # Devuelve el usuario
            else:
                return {"estado":False, "mensaje": "Faltan datos"}
        else:
            return {"estado":False, "mensaje": "Codigo de verificacion no coincide o ha caducado"}
      

    @staticmethod
    def verificarInformacion(data):
        if any(valor for valor in data.values()):
            return True 
        return True

class Imagen:
    @staticmethod
    def guardar_imagen_base64(imagen_base64, nombre, id_usuario):
        if imagen_base64.startswith("data:image"):
            imagen_base64 = imagen_base64.split(",")[1]
        # Decodifica el string base64
        try:
            imagen_bytes = base64.b64decode(imagen_base64)
        except base64.binascii.Error as e:
            print("Error al decodificar la imagen:", e)
            return None

        # Obtiene la extensión de la imagen (por defecto será .jpg si no se puede identificar)
        extension = 'jpg'
        if imagen_base64.startswith('/9j/'):  # Detecta si es un JPEG (esto es solo un ejemplo)
            extension = 'jpg'
        elif imagen_base64.startswith('iVBORw0KGgo='):  # Detecta si es un PNG
            extension = 'png'

        ruta_base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'img'))
        
        # Asegúrate de que la carpeta 'img' exista
        os.makedirs(ruta_base, exist_ok=True)

        # Define el nombre del archivo en el formato [id]_[nombre].ext
        nombre_archivo = f"{id_usuario}_{nombre}.{extension}"
        ruta_completa = os.path.join(ruta_base, nombre_archivo)

        # Guarda la imagen en el disco
        try:
            with open(ruta_completa, 'wb') as imagen_file:
                imagen_file.write(imagen_bytes)
            print(f"Imagen guardada exitosamente en: {ruta_completa}")
            ruta_relativa = os.path.join('img', nombre_archivo)  # Cambiar 'img/' según tu estructura
            return ruta_relativa
        except IOError as e:
            print("Error al guardar la imagen:", e)
            return None
        

    @staticmethod
    def convertir_imagen_a_base64(ruta_relativa):
        # Obtén la ruta absoluta de la imagen
        ruta_absoluta = os.path.abspath(ruta_relativa)
        
        try:
            with open(ruta_absoluta, 'rb') as imagen_file:
                # Lee la imagen y codifícala en base64
                imagen_bytes = imagen_file.read()
                imagen_base64 = base64.b64encode(imagen_bytes).decode('utf-8')
                return imagen_base64
        except FileNotFoundError:
            print(f"La imagen no se encuentra en la ruta: {ruta_absoluta}")
            return None
        except Exception as e:
            print(f"Ocurrió un error: {e}")
            return None
        
class Password:
    @staticmethod
    def encriptar_password(password):
        password_bytes = password.encode('utf-8')
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        return hashed.decode('utf-8')  
    

    @staticmethod
    def verificar_password_encrip(password_plano, password_encriptado):
        password_bytes = password_plano.encode('utf-8')
        if isinstance(password_encriptado, str):
            hashed_bytes = password_encriptado.encode('utf-8')
        else:
            hashed_bytes = password_encriptado
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    
class Direccion:
    @staticmethod
    def agregar_direccion(auth, datos):
        if auth:
            validacionToken = Usuario.verificarToken(auth)
            if validacionToken["estado"] == True:
                log_addDirecciones = DireccionesBase.insertar_direccion(validacionToken["datos"]["id"], datos)
                return log_addDirecciones
            else:
                return {"estado":False, "mensaje": "No tiene autorización"}
        else:
            return {"estado":False, "mensaje": "No tiene autorización"} 
        
    @staticmethod
    def obtener_direccion(auth):
        if auth:
            validacionToken = Usuario.verificarToken(auth)
            if validacionToken["estado"] == True:
                direcciones = DireccionesBase.ver_direcciones(validacionToken["datos"]["id"])
                if direcciones is not None:
                    return {"estado":True, "mensaje": "Consulta completada", "datos": direcciones}
                else:
                    return {"estado":False, "mensaje": "No tiene direcciones"}           
            else:
                return {"estado":False, "mensaje": "No tiene autorización"}
        else:
            return {"estado":False, "mensaje": "No tiene autorización"} 
    
    @staticmethod
    def elimnar_direccion(auth, id):
        if auth:
            validacionToken = Usuario.verificarToken(auth)
            if validacionToken["estado"] == True:
                log_eliminar = DireccionesBase.eliminar_direcciones(validacionToken["datos"]["id"], id)
                return log_eliminar         
            else:
                return {"estado":False, "mensaje": "No tiene autorización"}
        else:
            return {"estado":False, "mensaje": "No tiene autorización"} 


    @staticmethod
    def obtener_direccion_unica(auth, id):
        if auth:
            validacionToken = Usuario.verificarToken(auth)
            if validacionToken["estado"] == True:
                direcciones = DireccionesBase.ver_direccion_unica(validacionToken["datos"]["id"], id)
                if direcciones is not None:
                    return {"estado":True, "mensaje": "Consulta completada", "datos": direcciones}
                else:
                    return {"estado":False, "mensaje": "No tiene direcciones"}           
            else:
                return {"estado":False, "mensaje": "No tiene autorización"}
        else:
            return {"estado":False, "mensaje": "No tiene autorización"}
        

    @staticmethod
    def editar_direccion(auth, datos, id):
        if auth:
            validacionToken = Usuario.verificarToken(auth)
            if validacionToken["estado"] == True:
                log_editDirecciones = DireccionesBase.editar_direccion(validacionToken["datos"]["id"], datos, id)
                return log_editDirecciones
            else:
                return {"estado":False, "mensaje": "No tiene autorización"}
        else:
            return {"estado":False, "mensaje": "No tiene autorización"} 
        
    @staticmethod
    def setear_principal(auth, id):
        if auth:
            validacionToken = Usuario.verificarToken(auth)
            if validacionToken["estado"] == True:
                log_secundaria = DireccionesBase.set_direcciones_secundarias(validacionToken["datos"]["id"])
                if log_secundaria["estado"]== True:
                    log_principal = DireccionesBase.set_direccion_principal(validacionToken["datos"]["id"], id)
                    return log_principal  
                else:
                    return log_secundaria         
            else:
                return {"estado":False, "mensaje": "No tiene autorización"}
        else:
            return {"estado":False, "mensaje": "No tiene autorización"}
        
class Paquete:
    @staticmethod
    def agregar_paquete(auth, datos):
        if auth:
            validacionToken = Usuario.verificarToken(auth)
            if validacionToken["estado"] == True:
                log_verificar_tracking = TrackingBase.verificar_tracking(datos["tracking"], validacionToken["datos"]["id"])
                if not log_verificar_tracking:
                    nombre_archivo = f"{validacionToken['datos']['id']}_{datos['tracking']}"
                    log_guardar_archivo = Paquete.guardar_archivo_base64(datos["archivo"],nombre_archivo)
                    if log_guardar_archivo["estado"] == True:
                        direccion_destino = DireccionesBase.ver_direccion_principal(validacionToken["datos"]["id"])
                        if direccion_destino is None:
                            direccion_destino = {}
                            direccion_destino["idDireccion"] = None 
                        log_guardar_base = TrackingBase.insertar_tracking(datos["tracking"],validacionToken["datos"]["id"],0,0,log_guardar_archivo["ruta"],direccion_destino["idDireccion"])
                        if log_guardar_base:
                            #  pparedes@vipcourier.com.ec
                            nombre = f"{validacionToken['datos']['primerNombre']} {validacionToken['datos']['primerApellido']}"
                            datos = Correo.armar_correo_notificacion(nombre,datos["tracking"])
                            log_correo = Correo.enviar_correo("pparedes@vipcourier.com.ec",datos["asunto"], datos["cuerpo"])
                            if log_correo:
                               return {"estado":True, "mensaje": "Se ha ingresado el nuevo TRACKING ID correctamente"} 
                            else:
                               return {"estado":True, "mensaje": "Se ha ingresado el nuevo tracking pero no se ha podido notificar"} 
                        else:
                            return {"estado":False, "mensaje": "No se ha posido ingresar el nuevo tracking"}
                    else:    
                        return log_guardar_archivo
                else:
                    return {"estado":False, "mensaje": "El numero de tracking ya existe"}
            else:
                return {"estado":False, "mensaje": "No tiene autorización"}
        else:
            return {"estado":False, "mensaje": "No tiene autorización"} 
    
    @staticmethod
    def obtenerPaquetes(auth):
        if auth:
            validacionToken = Usuario.verificarToken(auth)
            if validacionToken["estado"] == True:
                trackins = TrackingBase.obtener_trackings(validacionToken["datos"]["id"])
                return {"estado":True, "mensaje": "Se ha encontrado paquetes", "datos": trackins}
            else:
                return {"estado":False, "mensaje": "No tiene autorización"}
        else:
            return {"estado":False, "mensaje": "No tiene autorización"}
        

    @staticmethod
    def descargar_tracking(auth, idTracking):
        if auth:
            validacionToken = Usuario.verificarToken(auth)
            if validacionToken["estado"] == True:
                resultado = TrackingBase.obtener_trackings_completos(idTracking,"")
                trackins = resultado[0]
                if trackins:
                    base64 = Paquete.archivo_a_base64(trackins["rutaImagen"])
                    return {"estado":True, "mensaje": "Se ha encontrado paquetes", "datos": base64}
                return {"estado":False, "mensaje": f"No existe tracking {idTracking}"}
            else:
                return {"estado":False, "mensaje": "No tiene autorización"}
        else:
            return {"estado":False, "mensaje": "No tiene autorización"}

    
        
    @staticmethod
    def obtenerPaquetes_completos(auth, buscador):
        if auth:
            validacionToken = Usuario.verificarToken(auth)
            if validacionToken["estado"] == True:
                trackins = TrackingBase.obtener_trackings_completos(None, buscador)
                for datos in trackins:
                    if datos["ciudad"] is None:
                        datos["provincia"] = "Pichincha"
                        datos["ciudad"] = "Quito"
                        datos["sector"] = "Iñaquito"
                        datos["calle_principal"] = "Andrade Marin"
                        datos["calle_secundaria"] = "Eloy Alfaro"
                        datos["numeracion"] = "E6-24"
                        datos["referencia"] = "Edificio Carolina Milenium"
                return {"estado":True, "mensaje": "Se ha encontrado paquetes", "datos": trackins}
            else:
                return {"estado":False, "mensaje": "No tiene autorización"}
        else:
            return {"estado":False, "mensaje": "No tiene autorización"}
    

    @staticmethod
    def consultar_api(trackingID):
        url1 = "http://jdlogistics.helgasys.com/api/consulta-estado/"
        url2 = "/jdldbafe0e3b3623592801417cda22a76f8dfb48e34f833ddbca15bca534182305e"
        url = f"{url1}{trackingID}{url2}"
        headers = {
            'Origin': "https://www.digitalpaymentnow.com",
        }
        try:
            # Realizar la solicitud GET con los encabezados
            response = requests.get(url, headers=headers)

            # Verificar si la solicitud fue exitosa (código 200)
            if response.status_code == 200:
                return response.json()  # Devuelve la respuesta en formato JSON
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error en la solicitud: {str(e)}")
            return None
        
    
    @staticmethod
    def guardar_archivo_base64(base64_data, nombre_archivo):
        try:
            # Extraer la extensión del archivo desde el encabezado base64, si existe
            coincidencia = re.match(r"data:(.*?)/(.*?);base64,(.*)", base64_data)
            if coincidencia:
                tipo = coincidencia.group(1)        # Ejemplo: "image" o "application"
                extension = coincidencia.group(2)   # Ejemplo: "png" o "pdf"
                base64_data = coincidencia.group(3) # Los datos base64 reales sin el encabezado
            else:
                print("La cadena base64 no contiene información del tipo de archivo.")
                return {"estado": False, "mensaje": "No se encuentra el encabezado del archivo a guardar"}
                
            # Decodificar el archivo base64
            archivo_decodificado = base64.b64decode(base64_data)
            
            # Obtener la ruta de la carpeta 'recibos' ubicada un nivel más arriba
            ruta_carpeta_recibos = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'recibos')
            
            # Crear la carpeta 'recibos' si no existe
            os.makedirs(ruta_carpeta_recibos, exist_ok=True)

            nombre_base = f"{nombre_archivo}"
            ruta_base_archivo = os.path.join(ruta_carpeta_recibos, nombre_base)

            # Eliminar cualquier archivo existente con el mismo nombre base (independiente de la extensión)
            for archivo_existente in glob.glob(f"{ruta_base_archivo}.*"):
                os.remove(archivo_existente)

            ruta_archivo = f"{ruta_base_archivo}.{extension}"
            
            # Guardar el archivo
            with open(ruta_archivo, 'wb') as archivo:
                archivo.write(archivo_decodificado)

            nombre = f"{nombre_archivo}.{extension}"
            ruta_relativa = os.path.join('recibos', nombre)
            return {"estado": True, "ruta": ruta_relativa}
        
        except Exception as e:
            # En caso de error, retornar estado False y el mensaje de error
            return {"estado": False, "mensaje": str(e)}


    def archivo_a_base64(ruta_archivo):
        """
        Convierte un archivo a base64.

        Args:
            ruta_archivo (str): La ruta del archivo a convertir.

        Returns:
            str: El contenido del archivo en formato base64.
        """
        try:
            # Obtener el tipo MIME del archivo
            tipo_mime, _ = mimetypes.guess_type(ruta_archivo)
            
            # Si no se puede adivinar el tipo MIME, asignar un tipo por defecto
            if tipo_mime is None:
                tipo_mime = 'application/octet-stream'
            
            # Leer el archivo en modo binario
            with open(ruta_archivo, "rb") as archivo:
                contenido = archivo.read()
                contenido_base64 = base64.b64encode(contenido).decode('utf-8')

                # Formar la cabecera base64 con el tipo MIME
                return f"data:{tipo_mime};base64,{contenido_base64}"
        
        except FileNotFoundError:
            return "Error: Archivo no encontrado."
        except Exception as e:
            return f"Error: {str(e)}"


    @staticmethod
    def validar_tracking(auth, tracking):
        if auth:
            validacionToken = Usuario.verificarToken(auth)
            if validacionToken["estado"] == True:
                log_tracking = Paquete.consultar_api(tracking)
                if log_tracking is not None:
                    return {"estado":True, "mensaje": "Tracking encontrado", "datos": log_tracking["datos"]}
                else:
                    return {"estado":True, "mensaje": "No hay datos de "+str(tracking), "datos": ""}
            else:
                return {"estado":False, "mensaje": "No tiene autorización"}
        else:
            return {"estado":False, "mensaje": "No tiene autorización"} 



class Correo:
    @staticmethod
    def verificar_correo(data):
        if data["password1"] == data["password2"]:
            codigo = Correo.generar_codigo_aleatorio(8)
            if not UsuarioBase.verificar_correo(data["correo"]):
                datos = Correo.armar_correo_verificacion(codigo)
                log_correo = Correo.enviar_correo(data["correo"],datos["asunto"] ,datos["cuerpo"])
                if log_correo:
                    log = UsuarioBase.insertar_codigo_temporal(data["correo"], codigo)
                    if log:
                        return {"estado":True, "mensaje": "Codigo enviado con exito al correo registrado"}
                    else:
                        return {"estado":False, "mensaje": "No se pudo crear codigo"}
                else:
                    return {"estado":False, "mensaje": "Error al enviar correo"}
            else:
                return {"estado":False, "mensaje": "El correo ya esta registrado"}
        return {"estado":False, "mensaje": "Contraseñas no coinciden"}
    

    @staticmethod
    def armar_correo_verificacion(codigo):
        subject = "Verificación de Correo Electrónico"
        ruta = os.path.abspath("img/logo.png")
        try:
            with open(ruta, 'rb') as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error al leer la imagen: {e}")
            return False  
        body = f"""
            <p style="text-align: center;">
                <img src="data:image/png;base64,{encoded_image}" style="width: 200px;">
            </p>
            <p style="text-align: center;">VERIFICACIÓN DE CORREO ELECTRÓNICO</p>
            <p style="text-align: justify;">
                Esta es tu clave temporal para acceder al sistema de forma segura. Por motivos de seguridad, recuerda que esta clave tiene una duración limitada de 5 minutos. 
                Una vez transcurrido este tiempo, la clave caducará y no podrá ser utilizada. Si necesitas una nueva clave, puedes solicitarla nuevamente. ¡Asegúrate de usarla dentro del tiempo permitido!
            </p>
            <p style="text-align: center;">
                <br>
            </p>
            <p style="text-align: center;">{codigo}</p>
        """
        return {"asunto": subject, "cuerpo": body}
    

    @staticmethod
    def armar_correo_notificacion(nombre, tracking):
        subject = "Notificacion de ingreso de nuevo tracking"
        ruta = os.path.abspath("img/logo.png")
        try:
            with open(ruta, 'rb') as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error al leer la imagen: {e}")
            return False  
        body = f"""
            <p style="text-align: center;">
                <img src="data:image/png;base64,{encoded_image}" style="width: 200px;">
            </p>
            <p style="text-align: center;">NOTIFICACIÓN DE INGRESO DE NUEVO TRACKING</p>
            <p style="text-align: justify;">
                Hola Paola, se te informa que el cliente {nombre} acaba de ingresar un nuevo TRACKING con el ID {tracking} por favor, revisarlo en la pagina https://vipcourier.com.ec, en la sección "clientes" y realiza la gestión correspondiente.
            </p>
            <p style="text-align: center;">
                <br>
            </p>
            <p>Departamento de TI</p>
        """
        return {"asunto": subject, "cuerpo": body}
    

    @staticmethod
    def armar_correo_restablecer(password):
        subject = "Restablecer contraseña Vip Courier"
        ruta = os.path.abspath("img/logo.png")
        try:
            with open(ruta, 'rb') as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error al leer la imagen: {e}")
            return False  
        body = f"""
            <p style="text-align: center;">
                <img src="data:image/png;base64,{encoded_image}" style="width: 200px;">
            </p>
            <p style="text-align: center;">RESTABLECER CONTRASEÑA</p>
            <p style="text-align: justify;">
                Hola, Vip Courier te informa que tu contraseña temporal es: {password}. Cambiala una vez hayas ingresado a tu cuenta.
            </p>
            <p style="text-align: center;">
                <br>
            </p>
            <p>Departamento de TI</p>
        """
        return {"asunto": subject, "cuerpo": body}


    @staticmethod
    def enviar_correo(to_email, subject, body):
        
        # Crear el mensaje MIME
        message = MIMEMultipart()
        message['From'] = from_email
        message['To'] = to_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'html'))

        # Enviar el correo
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # Iniciar una conexión segura
            server.login(from_email, password)  # Iniciar sesión en el servidor SMTP
            server.sendmail(from_email, to_email, message.as_string())
            print("Correo enviado exitosamente!")
            return True
        except Exception as e:
            print(f"Error al enviar correo: {e}")
            return False
        finally:
            server.quit()



    @staticmethod
    def generar_codigo_aleatorio(longitud=5):
        caracteres = string.ascii_uppercase + string.digits 
        codigo = ''.join(random.choices(caracteres, k=longitud))
        return codigo
    

    @staticmethod
    def verificarCodigo(codigo, correo):
        codigo = UsuarioBase.verificar_codigo_temporal(correo,codigo)
        if codigo:
            fecha_actual = datetime.now()
            if codigo["expiracion"] < fecha_actual:
                return True
        return False
