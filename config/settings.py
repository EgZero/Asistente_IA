import sys
import io
from pathlib import Path
from dotenv import load_dotenv
import os

if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

load_dotenv()

# Direccion a la raiz del proyecto
BASE_DIR = Path(__file__).parent.parent 

#Rutas - Siempre uso pathlib
DB_PATH = BASE_DIR /os.getenv("DB_PATH", "data/Asistente.db")
LOG_PATH = BASE_DIR / "data" / "Asistente.log"

#LLM

LLM_API_KEY = os.getenv("LLM_API_KEY" , "")
LLM_MODEL = os.getenv("LLM_MODEL" , "calude-haiku-4-5")

#Comprotamiento de sesion
GUADRAR_CADA = 3 #Guardar cada 3 intercambios (Checkpoints)