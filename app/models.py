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

class UsuarioBase:

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
                "primerNombre": resultado[2],     # Ajusta el índice según la estructura de tu tabla
                "primerApellido": resultado[4],   # Ajusta el índice según la estructura de tu tabla
                "correo": resultado[6],     # Ajusta el índice según la estructura de tu tabla
                "rol": resultado[8],        # Ajusta el índice según la estructura de tu tabla
            }
        return None
    
    @classmethod
    def obtener_usuario(cls, id):
        db = Database()
        query = "SELECT * FROM usuarios WHERE id = %s"
        db.cursor.execute(query, (id,))
        resultado = db.cursor.fetchone()
        db.close()
        if resultado:
            return {
                "id": resultado[0], 
                "cedula": resultado[1],         
                "primerNombre": resultado[2],     # Ajusta el índice según la estructura de tu tabla
                "segundoNombre": resultado[3],     # Ajusta el índice según la estructura de tu tabla
                "primerApellido": resultado[4],   # Ajusta el índice según la estructura de tu tabla
                "segundoApellido": resultado[5],   # Ajusta el índice según la estructura de tu tabla
                "correo": resultado[6],     # Ajusta el índice según la estructura de tu tabla
                "rol": resultado[8],        # Ajusta el índice según la estructura de tu tabla
                "telefono": resultado[9],      
                "imagen": resultado[10],        
            }
        return None
    

    @classmethod
    def editar_usuario(cls, id, telefono):
        db = Database()
        query = "UPDATE usuarios SET telefono = %s WHERE id = %s"
        try:
            db.cursor.execute(query, (telefono,id))
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
        return {"password": None}


    
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
            return resultado 
        finally:
            cursor.close()  # Cierra el cursor aquí
            db.close()  # Cierra la conexión aquí
    

    @classmethod
    def insertar_usuario(cls, data, password):
        db = Database()
        query = """
                INSERT INTO usuarios (cedula, primerNombre,segundoNombre, primerApellido, segundoApellido ,correo, password, rol_id, telefono) 
                VALUES (%s, %s,%s, %s, %s, %s, %s,2, %s)
                """
        try:
            db.cursor.execute(query, (data["cedula"],data["primerNombre"],data["segundoNombre"],data["primerApellido"],data["segundoApellido"],data["correo"],password,data["telefono"]))
            db.connection.commit()  # Confirma la transacción
            resultado = {"estado":True, "mensaje": "Usuario insertado correctamente"}
        except Exception as e:
            db.connection.rollback()  # Revertir si hay un error
            resultado = {"estado":False, "mensaje": f"Hubo un error al insertar {e}"}
        finally:
            db.close()
            return resultado
        

    @classmethod
    def insertar_codigo_temporal(cls, correo, codigo):
        db = Database()
        query = "INSERT INTO codigos (correo, codigo) VALUES (%s, %s)"
        try:
            db.cursor.execute(query, (correo,codigo))
            db.connection.commit()  # Confirma la transacción
            resultado = True
        except Exception as e:
            db.connection.rollback()  # Revertir si hay un error
            resultado = False
        finally:
            db.close()
            return resultado
        
    
    @classmethod
    def verificar_codigo_temporal(cls, correo, codigo):
        db = Database()  # Crea una instancia de la clase Database
        query = """
                select * from codigos
                where correo = %s and codigo = %s
                LIMIT 1
                """  
        cursor = db.connection.cursor()
        try:
            cursor.execute(query, (correo,codigo))
            resultado = cursor.fetchone()  # Obtiene un solo resultado
            if resultado:
                # Crear un diccionario con los nombres de las columnas como claves
                columnas = [desc[0] for desc in cursor.description]
                resultado_dict = dict(zip(columnas, resultado))
                return resultado_dict
            else:
                return None  # Si no hay resultado, retorna None
        finally:
            cursor.close()  # Cierra el cursor aquí
            db.close()  # Cierra la conexión aquí

    
        
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

class DireccionesBase:
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

class TrackingBase:
    @classmethod
    def insertar_tracking(cls, tracking, idUsuario, precio, pagado,ruta, direccion):
        db = Database()
        query = "INSERT INTO trackings (numero_tracking, usuario_id, precio, pagado, ruta_recibo, direccion_destino) VALUES (%s, %s,%s, %s, %s, %s)"
        try:
            db.cursor.execute(query, (tracking,idUsuario,precio,pagado, ruta, direccion))
            db.connection.commit()  # Confirma la transacción
            resultado = True
        except Exception as e:
            db.connection.rollback()  # Revertir si hay un error
            resultado = False
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
        query = "SELECT * FROM vista_trackings"
        params = []
        if idUsuario:  # Si idUsuario tiene un valor
            query += " WHERE usuario_id = %s"
            params.append(idUsuario)
        db.cursor.execute(query, tuple(params))
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
    


    @classmethod
    def obtener_trackings_completos(cls, idTracking = None, buscador = ""):
        db = Database()
        query = """
                select u.id as idUsuario, cedula ,primerNombre, segundoNombre, primerApellido, segundoApellido, telefono, 
                provincia, ciudad, sector, calle_principal, calle_secundaria, referencia, numeracion,
                numero_tracking, t.id, t.ruta_recibo
                from trackings as t
                LEFT JOIN direcciones as d on t.direccion_destino = d.id
                INNER JOIN usuarios as u on u.id = t.usuario_id 
                
                """
        params = []
        if idTracking:
            query += " WHERE t.id = %s"
            params.append(idTracking)

        # Si se proporciona un valor en 'buscador', lo agregamos al filtro
        if buscador:
            if params:  # Si ya tenemos parámetros (por ejemplo, idTracking), usamos 'AND'
                query += " AND t.numero_tracking LIKE %s"
            else:  # Si no hay parámetros previos, usamos 'WHERE'
                query += " WHERE t.numero_tracking LIKE %s"
            params.append(f"%{buscador}%")
        db.cursor.execute(query, tuple(params))
        resultados = db.cursor.fetchall()
        db.close()
        paquetes = []
        for resultado in resultados:
            paquete = {
                "idUsuarios": resultado[0],         # Ajusta el índice según la estructura de tu tabla
                "cedula": resultado[1],     # Ajusta el índice según la estructura de tu tabla
                "primerNombre": resultado[2],   # Ajusta el índice según la estructura de tu tabla
                "segundoNombre": resultado[3],
                "primerApellido": resultado[4],
                "segundoApellido": resultado[5],
                "telefono": resultado[6],
                "provincia": resultado[7],
                "ciudad": resultado[8],
                "sector": resultado[9],           
                "calle_principal": resultado[10],  
                "calle_secundaria": resultado[11],  
                "referencia": resultado[12],  
                "numeracion": resultado[13],  
                "numero_tracking": resultado[14],  
                "idTracking": resultado[15],
                "rutaImagen": resultado[16]
            }
            paquetes.append(paquete)
        return paquetes
