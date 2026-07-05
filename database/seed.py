import sqlite3
import logging as log
from database.db_connection import conectar, cerrar_conexion

logger = log.getLogger(__name__)


# -----DATOS INICIALES --------
# (keyword, command_type, target_windows, target_linux)

COMANDOS_MAPA=[
    ("chrome",          "open_app", "chrome.exe",       "google-chrome"),
    ("navegador",       "open_app", "chrome.exe",       "google-chrome"),
    ("spotify",         "open_app", "Spotify.exe",      "spotify"),
    ("calculadora",     "open_app", "calc.exe",         "gnome-calculator"),
    ("bloc de notas",   "open_app", "notepad.exe",      "gedit"),
    ("explorador",      "open_app", "explorer.exe",     "nautilus"),
    ("apaga",           "system",   "shutdown /s /t 0", "shutdown -h now"),
    ("reinicia",        "system",   "shutdown /r /t 0", "reboot"),
]

#---- Gatillos para el modo de conversa------

# (keyword, target_mode, weight)
# weight va de 0.0 a 1.0 — más alto significa más certeza de ese modo.
TRIGGERS_MODOS = [
    ("Explicame","Tutor", 0.9),
    ("No entiendo","Tutor", 0.8),
    ("Como funciona","Tutor", 0.8),
    ("qué es",          "tutor",        0.7),
    ("enséñame",        "tutor",        0.9),
    ("cuál es la diferencia", "tutor",  0.7),
    ("qué opinas",      "conversacion", 0.7),
    ("cuéntame",        "conversacion", 0.6),
    ("qué harías",      "conversacion", 0.7),
    ("hablemos de",     "conversacion", 0.6),    
]

def seed_mapaComandos(conn : sqlite3.Connection) -> None:
    """
        Insera los comandos del PC en la tabla 'command_mappings'.
    """
    conn.executemany(
        
    """
        INSERT OR IGNORE INTO mapa_comandos (palabra_clave , tipo_comando, target_windows, target_linux)
        VALUES (? , ? , ? , ?)
    """,
    COMANDOS_MAPA
    )
    logger.info(f"{len(COMANDOS_MAPA)} comandos procesados")
    
    
def seed_triggerModos(conn : sqlite3.Connection) -> None:
    """
        Insera los comandos del PC en la tabla 'mode_triggers'.
    """
    conn.executemany(
        
    """
        INSERT OR IGNORE INTO triggers_de_modo (palabra_clave , modo_objetivo, peso)
        VALUES (? , ? , ?)
    """,
    TRIGGERS_MODOS
    )
    logger.info(f"{len(TRIGGERS_MODOS)} comandos procesados")
    
def ejecutar_seeds()-> None: 
    conn = None
    try:
        conn = conectar()
        seed_mapaComandos(conn)
        seed_triggerModos(conn)
        
        conn.commit()
        #confirma las operaciones en la BD
        print("Seed completada correctamente :D")
    except sqlite3.Error as e:
        print(f"Error en seed: {e}")
        logger.error(f"Error Ejecutando seed: {e}")
        if conn:
            conn.rollback()
    finally:
        #finally siempre se ejecuta, haya error o no, por eso garantizo el cierre de conexion con la bd aun tieniendo fallos
        if conn:
            cerrar_conexion(conn)
            
if __name__ == "__main__":
    #esta condicion solo se cumple cuando se corre este archivo directamente, es decir (python database/seed.py)
    #es falso siempre que se importe seed.py en otro lado, por lo que no se ejecutará ejecutar_seeds()
    log.basicConfig(level=log.INFO)
    ejecutar_seeds()