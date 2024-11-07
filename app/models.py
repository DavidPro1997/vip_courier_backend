import mysql.connector
from app.config import Config 

class Database:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        self.cursor = self.connection.cursor(buffered=True)

    def close(self):
        self.cursor.close()
        self.connection.close()

class Usuario:

    @classmethod
    def usuario_login(cls, correo, password):
        db = Database()
        query = "SELECT * FROM usuarios WHERE correo = %s AND password = %s"
        db.cursor.execute(query, (correo, password))
        resultado = db.cursor.fetchone()
        db.close()
        if resultado:
            return {
                "id": resultado[0],         # Ajusta el índice según la estructura de tu tabla
                "nombre": resultado[1],     # Ajusta el índice según la estructura de tu tabla
                "apellido": resultado[2],   # Ajusta el índice según la estructura de tu tabla
                "correo": resultado[3],     # Ajusta el índice según la estructura de tu tabla
                "rol": resultado[5],        # Ajusta el índice según la estructura de tu tabla
            }
        return None
    
    @classmethod
    def obtener_usuario(cls, id):
        db = Database()
        query = "SELECT * FROM datos_usuario WHERE id = %s"
        db.cursor.execute(query, (id,))
        resultado = db.cursor.fetchone()
        db.close()
        if resultado:
            return {
                "id": resultado[0],         # Ajusta el índice según la estructura de tu tabla
                "nombre": resultado[1],     # Ajusta el índice según la estructura de tu tabla
                "apellido": resultado[2],   # Ajusta el índice según la estructura de tu tabla
                "correo": resultado[3],     # Ajusta el índice según la estructura de tu tabla
                "rol": resultado[4],        # Ajusta el índice según la estructura de tu tabla
                "telefono": resultado[5],      
                "imagen": resultado[6],        
            }
        return None
    

    @classmethod
    def editar_usuario(cls, id, nombres, apellidos, telefono):
        db = Database()
        query = "UPDATE usuarios SET nombre = %s, apellido = %s,telefono = %s WHERE id = %s"
        try:
            db.cursor.execute(query, (nombres,apellidos,telefono,id))
            db.connection.commit()  # Confirma la transacción
            resultado = {"estado":True, "mensaje": "Datos actualizados correctamente"}
        except Exception as e:
            db.connection.rollback()  # Revertir si hay un error
            resultado = {"estado":False, "mensaje": "Hubo un error al modificar los datos"}
        finally:
            db.close()
            return resultado
        

    @classmethod
    def verificar_password(cls, id):
        db = Database()
        query = "SELECT `password` FROM usuarios WHERE id = %s"
        db.cursor.execute(query, (id,))
        resultado = db.cursor.fetchone()
        db.close()
        if resultado:
            return {
                "password": resultado[0]        # Ajusta el índice según la estructura de tu tabla
            }
        return None
    

    @classmethod
    def obteneder_password(cls, correo):
        db = Database()
        query = "SELECT `password` FROM usuarios WHERE correo = %s"
        db.cursor.execute(query, (correo,))
        resultado = db.cursor.fetchone()
        db.close()
        if resultado:
            return {
                "password": resultado[0]        # Ajusta el índice según la estructura de tu tabla
            }
        return None


    
    @classmethod
    def editar_password(cls, id, password):
        db = Database()
        query = "UPDATE usuarios SET password = %s WHERE id = %s"
        try:
            db.cursor.execute(query, (password,id,))
            db.connection.commit()  # Confirma la transacción
            resultado = {"estado":True, "mensaje": "Contrasela actualizada correctamente"}
        except Exception as e:
            db.connection.rollback()  # Revertir si hay un error
            resultado = {"estado":False, "mensaje": "Hubo un error al modificar contraseña"}
        finally:
            db.close()
            return resultado
        
    
    @classmethod
    def verificar_correo(cls, correo):
        db = Database()  # Crea una instancia de la clase Database
        query = "SELECT * FROM usuarios WHERE correo = %s LIMIT 1"  # Agrega LIMIT 1
        cursor = db.connection.cursor()
        try:
            cursor.execute(query, (correo,))
            resultado = cursor.fetchone()  # Obtiene un solo resultado
            return resultado is not None  # Retorna True si hay un resultado
        finally:
            cursor.close()  # Cierra el cursor aquí
            db.close()  # Cierra la conexión aquí
    

    @classmethod
    def insertar_usuario(cls, nombre, apellido, correo, password):
        db = Database()
        query = "INSERT INTO usuarios (nombre, apellido, correo, password, rol_id) VALUES (%s, %s,%s, %s,2)"
        try:
            db.cursor.execute(query, (nombre,apellido,correo,password))
            db.connection.commit()  # Confirma la transacción
            resultado = {"estado":True, "mensaje": "Usuario insertado correctamente"}
        except Exception as e:
            db.connection.rollback()  # Revertir si hay un error
            resultado = {"estado":False, "mensaje": "Hubo un error al insertar"}
        finally:
            db.close()
            return resultado
        
    @classmethod
    def insertar_imagen(cls, id, ruta):
        db = Database()
        query = "UPDATE usuarios SET imagen = %s WHERE id = %s"
        try:
            db.cursor.execute(query, (ruta,id))
            db.connection.commit()  # Confirma la transacción
            resultado = {"estado":True, "mensaje": "Fotografía insertado correctamente"}
        except Exception as e:
            db.connection.rollback()  # Revertir si hay un error
            resultado = {"estado":False, "mensaje": "Hubo un error al insertar"}
        finally:
            db.close()
            return resultado

class Direcciones:
    @classmethod
    def insertar_direccion(cls, id,datos):
        db = Database()
        query = """
            INSERT INTO direcciones (usuario_id, provincia, ciudad, sector, calle_principal, calle_secundaria, numeracion, referencia, alias) 
            VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s) 
            """
        try:
            db.cursor.execute(query, (
                id,
                datos["provincia"],
                datos["ciudad"],
                datos["sector"],
                datos["calle_principal"],
                datos["calle_secundaria"],
                datos["numeracion"],
                datos["referencia"],
                datos["alias"]
            ))
            db.connection.commit()  # Confirma la transacción
            resultado = {"estado":True, "mensaje": "Dirección insertada correctamente"}
        except Exception as e:
            db.connection.rollback()  # Revertir si hay un error
            resultado = {"estado":False, "mensaje": "Hubo un error al insertar datos"}
        finally:
            db.close()
            return resultado
 
    @classmethod
    def ver_direcciones(cls, id):
        db = Database()
        query = "SELECT * FROM direcciones WHERE usuario_id = %s"
        db.cursor.execute(query, (id,))
        resultados = db.cursor.fetchall()
        db.close()
        direcciones = []
        for resultado in resultados:
            direccion = {
                "id": resultado[0],         # Ajusta el índice según la estructura de tu tabla
                "provincia": resultado[2],     # Ajusta el índice según la estructura de tu tabla
                "ciudad": resultado[3],   # Ajusta el índice según la estructura de tu tabla
                "sector": resultado[4],     # Ajusta el índice según la estructura de tu tabla
                "calle_principal": resultado[5],
                "calle_secundaria": resultado[6],
                "numeracion": resultado[7],
                "referencia": resultado[8],
                "principal": resultado[9],
                "alias": resultado[10],
            }
            direcciones.append(direccion)
        return direcciones if direcciones else None
    
    @classmethod
    def eliminar_direcciones(cls, idUsuario, idDireccion):
        db = Database()
        query = "DELETE FROM direcciones WHERE usuario_id = %s AND id = %s"
        try:
            db.cursor.execute(query, (idUsuario,idDireccion))
            db.connection.commit()  # Confirma la transacción
            resultado = {"estado":True, "mensaje": "Dirección eliminada correctamente"}
        except Exception as e:
            db.connection.rollback()  # Revertir si hay un error
            resultado = {"estado":False, "mensaje": f"Hubo un error al eliminar los datos: {str(e)}"}
        finally:
            db.close()
            return resultado
        
    @classmethod
    def ver_direccion_unica(cls, idUsuario, idDireccion):
        db = Database()
        query = "SELECT * FROM direcciones WHERE usuario_id = %s AND id = %s"
        db.cursor.execute(query, (idUsuario, idDireccion))
        resultados = db.cursor.fetchall()
        db.close()
        direcciones = []
        for resultado in resultados:
            direccion = {
                "id": resultado[0],         # Ajusta el índice según la estructura de tu tabla
                "provincia": resultado[2],     # Ajusta el índice según la estructura de tu tabla
                "ciudad": resultado[3],   # Ajusta el índice según la estructura de tu tabla
                "sector": resultado[4],     # Ajusta el índice según la estructura de tu tabla
                "calle_principal": resultado[5],
                "calle_secundaria": resultado[6],
                "numeracion": resultado[7],
                "referencia": resultado[8],
                "principal": resultado[9],
                "alias": resultado[10],
            }
            direcciones.append(direccion)
        return direcciones if direcciones else None

    @classmethod
    def editar_direccion(cls,idUsuario,datos,idDireccion):
        db = Database()
        query = "UPDATE direcciones SET provincia = %s, ciudad = %s,sector = %s,calle_principal = %s,calle_secundaria = %s ,numeracion = %s,referencia = %s, alias = %s WHERE id = %s AND usuario_id = %s"
        try:
            db.cursor.execute(query, (
                datos["provincia"],
                datos["ciudad"],
                datos["sector"],
                datos["calle_principal"],
                datos["calle_secundaria"],
                datos["numeracion"],
                datos["referencia"],
                datos["alias"],
                idDireccion,
                idUsuario
            ))
            db.connection.commit()  # Confirma la transacción
            resultado = {"estado":True, "mensaje": "Dirección editada correctamente"}
        except Exception as e:
            db.connection.rollback()  # Revertir si hay un error
            resultado = {"estado":False, "mensaje": "Hubo un error al editar datos"}
        finally:
            db.close()
            return resultado
        
    @classmethod
    def set_direccion_principal(cls,idUsuario,idDireccion):
        db = Database()
        query = "UPDATE direcciones SET principal = 1 WHERE id = %s AND usuario_id = %s"
        try:
            db.cursor.execute(query, (idDireccion, idUsuario))
            db.connection.commit()  # Confirma la transacción
            resultado = {"estado":True, "mensaje": "Dirección seteada como principal correctamente"}
        except Exception as e:
            db.connection.rollback()  # Revertir si hay un error
            resultado = {"estado":False, "mensaje": "Hubo un error al setear dirección"}
        finally:
            db.close()
            return resultado
        
    @classmethod
    def set_direcciones_secundarias(cls,idUsuario):
        db = Database()
        query = "UPDATE direcciones SET principal = 0 WHERE usuario_id = %s"
        try:
            db.cursor.execute(query, (idUsuario,))
            db.connection.commit()  # Confirma la transacción
            resultado = {"estado":True, "mensaje": "Dirección seteada como secundarias correctamente"}
        except Exception as e:
            db.connection.rollback()  # Revertir si hay un error
            resultado = {"estado":False, "mensaje": "Hubo un error al setear direcciónes"}
        finally:
            db.close()
            return resultado

    @classmethod
    def ver_direccion_principal(cls, idUsuario):
        db = Database()
        query = "SELECT id FROM direcciones WHERE usuario_id = %s AND principal = 1"
        db.cursor.execute(query, (idUsuario,))
        resultado = db.cursor.fetchone()
        db.close()
        if resultado:
            return {
                "idDireccion": resultado[0], 
            }
        return None

class Tracking:
    @classmethod
    def insertar_tracking(cls, tracking, idUsuario, precio, pagado,ruta, direccion):
        db = Database()
        query = "INSERT INTO trackings (numero_tracking, usuario_id, precio, pagado, ruta_recibo, direccion_destino) VALUES (%s, %s,%s, %s, %s, %s)"
        try:
            db.cursor.execute(query, (tracking,idUsuario,precio,pagado, ruta, direccion))
            db.connection.commit()  # Confirma la transacción
            resultado = {"estado":True, "mensaje": "Tracking insertado correctamente"}
        except Exception as e:
            db.connection.rollback()  # Revertir si hay un error
            resultado = {"estado":False, "mensaje": "Hubo un error al insertar datos"}
        finally:
            db.close()
            return resultado
    
    @classmethod
    def verificar_tracking(cls, tracking, idUsuario):
        db = Database()  # Crea una instancia de la clase Database
        query = "SELECT * FROM trackings WHERE numero_tracking = %s AND usuario_id = %s LIMIT 1"  # Agrega LIMIT 1
        cursor = db.connection.cursor()
        try:
            cursor.execute(query, (tracking, idUsuario))
            resultado = cursor.fetchone()  # Obtiene un solo resultado
            return resultado is not None  # Retorna True si hay un resultado
        finally:
            cursor.close()  # Cierra el cursor aquí
            db.close()  # Cierra la conexión aquí
        
    @classmethod
    def obtener_trackings(cls, idUsuario):
        db = Database()
        query = "SELECT * FROM vista_trackings WHERE usuario_id = %s"
        db.cursor.execute(query, (idUsuario,))
        resultados = db.cursor.fetchall()
        db.close()
        paquetes = []
        for resultado in resultados:
            paquete = {
                "id": resultado[0],         # Ajusta el índice según la estructura de tu tabla
                "numero_tracking": resultado[1],     # Ajusta el índice según la estructura de tu tabla
                "precio": resultado[3],   # Ajusta el índice según la estructura de tu tabla
                "pagado": resultado[4],
                "ruta": resultado[5],
                "idDireccion": resultado[6],
                "aliasDireccion": resultado[7]         
            }
            paquetes.append(paquete)
        return paquetes if paquetes else None
