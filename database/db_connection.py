#RESPONSABILIDAD - CREAR BD SI NO EXISTE, CREAR CARPETA DATA SI NO EXISTE, Y APLICAR EL ESQUEMA (TODO EN EL PRIMER ARRANQUE)

import sqlite3
import logging
from pathlib import Path
from config.settings import BASE_DIR, DB_PATH

logger = logging.getLogger(__name__)

#Ruta al esquema SQL

_SCHEMA_PATH = BASE_DIR / "database" / "Schema.sql"

def conectar() -> sqlite3.Connection:
    """
    Retorna un conexion activa a SQLite
    -Crea la carpeta Data si no existe
    Crea la base de datos si no existe
    Aplica el esquema en el primer arranque
    Activa claves formaneas (Estas estan desactivadas)
    """
    #Crear carpeta data (si no existe)
    DB_PATH.parent.mkdir(parents=True,exist_ok=True)
    primera_ejecucion = not DB_PATH.exists()
    #si la carpeta no existe, es la primera ejecucion, si existe no lo es
    conexion = sqlite3.connect(DB_PATH)
    
    #Retorna filas como diccionarios en lugar de tuplas
    conexion.row_factory = sqlite3.Row
    
    #Activar claves foraneas (necesario en SQLite3)
    conexion.execute("PRAGMA foreing_keys = ON")
    if primera_ejecucion:
        _aplicar_esquema(conexion)
        logger.info(f"Base de datos creada en: {DB_PATH}")
    return conexion
    
        
def _aplicar_esquema(conexion: sqlite3.Connection) -> None:
    """Lee schema.sql y crea las tablas"""
    esquema = _SCHEMA_PATH.read_text(encoding="utf-8")
    conexion.executescript(esquema)
    conexion.commit()
    logger.info("Esquema aplicado correctamente.")
    
def cerrar_conexion(conexion: sqlite3.Connection) -> None:
    """Cierra la conexion de forma segura"""
    if conexion:
        conexion.close()