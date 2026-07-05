#Este documento tiene la respondsabilidad de manejar los mensajes, perfiles, sesiones, 
#errores y demas temas de interes para la base de datos. NINGUN OTRO MODULO TOCA LA BD
import sqlite3
import logging as log
from database.db_connection import conectar, cerrar_conexion
from typing import Optional

logger = log.getLogger(__name__)

class MemoryManager:
    """
        Gestiona toda la persistencia del sistema
        Se instancia una vez en Orquestador y se pasa a los modulos que lo necesitan
    """
    def __init__(self):
        self.conn: sqlite3.Connection = conectar()
    
    def cerrar(self) ->None:
        """Cierra la conexion de la BD de forma segura, debe llamarse al apagar el sistema"""
        cerrar_conexion(self.conn)
        
#---- ESTUDIANTE------

def crearEstudiante(self, nombre:str , estilo:str = "paso_a_paso") -> int:
    """_summary_
        Crea el perfil del estudiante en la BD
    Args:
        nombre (str): _description_
        estilo (str, optional): _description_. Defaults to "paso_a_paso".

    Returns:
        int: _description_
    """
    cursor = self.conn.execute(
        #self.conn.execute() Ejecuta el codigo SQL y retorna el cursor
        """
            INSERT INTO estudiantes (nombre , estilo_aprendizaje)
            VALUES (?,?)
        """,
        (nombre, estilo)
    )
    self.conn.commit()
    return cursor.lastrowid #contiene el id de la ultima linea agregada, en este caso id de students

def obtenerEstudiante(self, id_estudiante : int) -> Optional[sqlite3.Row]:
    """_summary_
        Retorna el registro del estudiante objetivo o None si no existe
    Args:
        id_estudiante (int): _description_

    Returns:
        Optional[sqlite3.Row]: _description_
    """
    cursor = self.conn.execute(
        "SELECT * FROM estudiantes where id_estudiante = ?",
        (id_estudiante,) #la coma al final dice que es una tupla de un solo elemento, si no enviamos tuplas, SQL lanza un error
    )
    return cursor.fetchoe() #retorna la primera fila de un resultado, fetchall si queremos una lista de todas las filas

def obtener_o_crear_estudiante(self, nombre:str) -> int:
    """_summary_
    Busca un estudiante por nombre, si no existe, lo crea
    Args:
        nombre (str): _description_

    Returns:
        int: id_estudiante
    """
    cursor = self.conn.execute(
        """
            SELECT * FROM estudiantes WHERE nombre = ?
        """,
        (nombre,)
    )
    fila = cursor.fetchone()
    if fila:
        return fila["id_estudiante"] #accedemos por nombre de la columna gracias a row_factory
    else:
        return self.crearEstudiante(nombre)        

#--- TEMAS ----
def obtener_o_crear_tema(self, id_estudiante: int, nombre: str, categoria: str = "") -> int:
    """_summary_
        Busca un tema por nombre para el estudiante seleccionado
        Si no existe, lo creamos con domain_level 0
        Retorna id del tema
        Los temas se crean cuando se mencionan por primera vez.
    Args:
        id_estudiante (int): _description_
        nombre (str): _description_
        categoria (str, optional): _description_. Defaults to "".

    Returns:
        int: _description_
    """
    cursor = self.conn.execute(
        """
            SELECT id FROM temas
            WHERE id_estudiante = ? AND nombre = ?
        """
        )
    fila = cursor.fetchone()

    if fila:
        return fila["id_estudiante"]
    
    cursor = self.conn.execute(
    """
        INSERT INTO temas (id_estudiante,nombre,categoria)
        VALUES (? , ? , ?) 
    """,
    (id_estudiante,nombre, categoria)
    )
    self.conn.commit()
    return cursor.lastrowid

def obtener_tema(self, id_tema: int) -> Optional[sqlite3.Row]:
    """RETORNA todos los datos de un tema de la tabla temas"""
    cursor = self.conn.execute(
        """
            SELECT * FROM temas
            WHERE id_tema = ?
        """,
        (id_tema,)
    )
    return cursor.fetchone()


def actualizarDominio(self , id_tema: int, nuevo_dominio:int) -> None:
    """_summary_
        Actualiza El dominio sobre un tema tratado, el valor está entre 0 y 10 
        y registra cuantas veces has repasado un tema, ademas de la ultima vez    
        se llama en cada checkpoint de sesión
        
        Args:
            id_tema (int): _description_
            nuevo_dominio (int): _description_
    """
    self.conn.execute(
    """
        UPDATE temas
        SET nivel_dominio = ? , veces_revisado = veces_revisado + 1, ultima_revision = CURRENT_TIMESTAMP
        WHERE id_tema = ?
    """,
    (nuevo_dominio, id_tema)        
    )
    self.conn.commit()

#----SESIONES -----
def crearSesion(self, id_estudiante: int, id_tema:int, modo:str= "tutor") -> int:
    """_summary_
        Abre una sesion nueva, tambien 'terminado_en' queda en NULL, 
        lo que nos va a permitir detectar sesiones huerfanas cuando el sistema se caiga
        Retorna el id de la nueva sesion creada
        Args:
            id_estudiante (int): _description_
            id_tema (int): _description_
            modo (str, optional): _description_. Defaults to "tutor".

        Returns:
            int: _description_
    """
    cursor = self.conn.execute(
        """
            INSERT INTO sesiones (id_estudiante, id_tema, modo)
            VALUES (? , ? , ?)
        """,
        (id_estudiante, id_tema,modo)
    )
    cursor.self.commit()
    return cursor.lastrowid

def crearCheckpoint(self, id_sesion:int) -> None:
    """_summary_
        Marca un punto de guardado en la sesion activa y suma 1 al contador de checkpoints
        se llama cada 'settings.GUADRAR_CADA' desde el orquestador
        Args:
            sesion_id (int): _description_
    """
    self.conn.execute(
    """
        UPDATE sesiones
        SET ultimo_guardado = CURRENT_TIMESTAMP, veces_guardado = veces_guardado + 1
        WHERE id_sesion = ?
    """,
    (id_sesion,)        
    )
    self.conn.commit()
    logger.info(f"Checkpoint guardado - sesion {id_sesion}")
    
def cerrarSesion(self, id_sesion: int, resumen:str) -> None:
    """
        Cierra la sesion correctamente: guarda el resumen y registra la hora de cierre
        terminado_en deja de ser null y se convierte en CURRENT_TIMESTAMP, por lo que ya no es huerfana 
    """
    self.conn.execute(
        """
            UPDATE sesiones
            SET terminado_en = CURRENT_TIMESTAMP, resumen = ?
            WHERE id_sesion = ?
        """,
        (resumen, id_sesion)
    )
    self.conn.commit()
    
def recuperar_sesiones_huerfanas(self , id_estudiante: int) -> list:
    """
        Recupera las sesiones con 'terminado_en' = NULL que empezaron hace mas de 5 mins    
        Args:
            id_estudiante (int): _description_

        Returns:
            list: _description_
    """
    cursor = self.conn.execute(
        """
            SELECT * FROM sesiones
            WHERE id_estudiante = ? AND terminado_en = NULL AND empezado_en < datetime('now' , '-5 minutes')
            ORDER BY empezado_en DESC
        """,# datetime es una funcion de SQLite, datetime('now' , '-5 minutes') => Hace 5 minutos exactos xd
        (id_estudiante,)
    )
    return cursor.fetchall() #si no hay huerfanas, retorna una lista vacia

def obtener_resumenes_recientes(self, id_estudiante: int , limite: int = 5) -> list:
    """
    Retorna resumenes de las ultimas sesiones cerradas,
    lo va a usar el contextBuilder para darle un contexto al LLM 
    sin gastar tokens ni todos los mensajes con ruido
    
    Args:
        id_estudiante (int): _description_
        limite (int, optional): _description_. Defaults to 5.

    Returns:
        list: _description_
    """
    cursor = self.conn.execute(
    """
        SELECT resumen, modo, empezado_en FROM sesiones
        WHERE id_estudiante = ? 
        AND terminado_en IS NOT NULL 
        AND resumen IS NOT NULL
        ORDER BY empezado_en DESC
        LIMIT ?
    """,
    (id_estudiante, limite)
    )
    return cursor.fetchall()


#---- MENSAJES -----
def guardarMensaje(self,id_sesion:int, rol:str , contenido: str) -> None:
    """
    Guarda un mensaje en la BD en el momento en el que ocurre. rol es user o assistant
    Se llama despues de cada intercambio
    Args:
        id_sesion (int): _description_
        rol (str): _description_
        contenido (str): _description_
    """
    self.conn.execute(
        """
            INSERT INTO mensajes (id_sesion, rol, contenido)
            VALUES (? , ? , ?)
        """,
        (id_sesion, rol, contenido)
    )
    self.conn.commit()

def obtener_mensajes_recientes(self, id_sesion: int, limite: int = 20) -> list:
    """
        Retorna los ultimos mensajes de una sesion activa
    """
    cursor = self.conn.execute(
        """
            SELECT rol, contenido FROM (
                SELECT rol, contenido FROM mensajes
                WHERE id_sesion = ?
                ORDER BY creado_en DESC
                LIMIT ?
            )
            ORDER BY creado_en ASC
        """,
        (id_sesion,limite)        
    )
    return cursor.fetchall()

# ---- ERRORES -----

def registrarError(self, id_estudiante:int, id_tema:int, descripcion:str) -> None:
    """
    Registra los errores cometidos por el estudiante, 
    si ya existe un error identico para el tema, aumenta la frecuencia + 1
    Args:
        id_estudiante (int): _description_
        id_tema (int): _description_
        descripcion (str): _description_
    """
    cursor = self.conn.execute(
        """
            SELECT id_error FROM errores
            WHERE id_estudiante = ? 
            AND id_tema = ?
            AND id_descripcion = ?
        """
    )
    existente = cursor.fetchone()
    if existente:
        self.conn.execute(
        """
            UPDATE errores
            SET frecuencia = frecuencia + 1, ultima_revision = CURRENT_TIMESTAMP 
            WHERE id_error = ? 
        """,
        (existente["id_error"])
        )
    else: 
        self.conn.execute(
        """
            INSERT INTO errores (id_estudiante, id_tema , descripcion)
            VALUES (? , ? , ?)
        """,
        (id_estudiante,id_tema, descripcion)
        )
    self.conn.commit()
        
def obtener_errores_frecuentes(self, id_estudiante: int , id_tema : int , limite:int = 5) -> list:
    """
    Retorna los errores mas frecuentes de un estudiante sobre un tema, 
    el Context BUilder los usa para que el LLM puedasaber donde se confunde el estudiante

    Args:
        id_estudiante (int): _description_
        id_tema (int): _description_
        limite (int, optional): _description_. Defaults to 5.

    Returns:
        list: _description_
    """
    cursor = self.conn.execute(
        """
            SELECT descripcion, frecuencia FROM errores
            WHERE id_estudiante = ? AND id_tema = ?
            ORDER BY frecuencia DESC
            LIMIT ?
        """,
        (id_estudiante,id_tema, limite)
        )
    return cursor.fetchall()

# --- Palabras Clave ----
def guardar_pablabras_clave(self, id_sesion:int, id_tema:int, palabras_clave:list[str]) -> None:
    """
    Guarda las palabras clave extraidas al cerrar una sesion, Incrementa la frecuencia si ya existe
    Args:
        id_sesion (int): _description_
        id_tema (int): _description_
        palabras_clave (list[str]): _description_
    """
    for palabra in palabras_clave:
        cursor = self.conn.execute(
            """
                SELECT id_palabra_clave FROM palabras_clave_de_sesion
                WHERE id_sesion = ? AND palabra_clave = ?
            """,
            (id_sesion, palabra)
        )
        existente = cursor.fetchone()
        
        if existente:
            self.conn.execute(
                """
                    UPDATE palabras_clave_de_sesion
                    SET frecuencia = frecuencia +1 
                    WHERE id_palabra = ?
                """,
                (existente["id_palabra"],)
            )
        else:
            self.conn.execute(
                """
                    INSERT INTO palabras_clave_de_sesion (id_sesion, id_tema, palabra_clave)
                    VALUES(? , ? , ?)
                """,
                (id_sesion,id_tema,palabra)
            )
    self.conn.commit()
            