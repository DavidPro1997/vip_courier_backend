from flask import Flask
from app.config import Config
import mysql.connector

app = Flask(__name__)
app.config.from_object(Config)

# Conexión a la base de datos
def get_db_connection():
    connection = mysql.connector.connect(
        host=app.config['DB_HOST'],
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD'],
        database=app.config['DB_NAME']
    )
    return connection

from app import routes  # Importar rutas