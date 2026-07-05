# Assistant — Tutor Inteligente con Memoria Persistente

Asistente conversacional híbrido diseñado como tutor académico personal.
Combina un LLM externo (Claude / GPT) con memoria local persistente en SQLite,
permitiendo un seguimiento real del progreso del estudiante entre sesiones.

---

## ¿Qué problema resuelve?

Los chatbots de IA convencionales no recuerdan nada entre conversaciones o utilizan tokens en exceso para hacerlo.
Este sistema mantiene un perfil académico del estudiante: qué temas estudió,
qué nivel de dominio tiene en cada uno, qué errores comete con frecuencia,
y usa esa información para personalizar cada sesión de tutoría.

---

## Estado actual del proyecto

| Módulo               | Estado        |
|----------------------|---------------|
| Esquema de base de datos | ✅ Completo |
| Conexión SQLite      | ✅ Completo   |
| Datos iniciales (seed) | 🔄 En progreso |
| Memory Manager       | 🔜 Pendiente  |
| Context Builder      | 🔜 Pendiente  |
| LLM Client           | 🔜 Pendiente  |
| Session Manager      | 🔜 Pendiente  |
| CLI Interface        | 🔜 Pendiente  |
| Tools Manager        | 🔜 Pendiente  |

---

## Arquitectura del sistema

```
I/O Layer (CLI / Voz / Hardware)
          ↓
    Orquestador (main.py)
    ↙         ↓         ↘
Memory    Context      Tools
Manager   Builder      Manager
    ↘         ↓         ↙
         LLM Client
         (Claude API)
          ↓
     APIs externas
```

**Principios de diseño:**
- El LLM es intercambiable — el sistema no depende de un proveedor específico.
- La memoria es el núcleo diferenciador — toda persistencia vive en SQLite local.
- Cada módulo tiene una sola responsabilidad — sin dependencias circulares.
- El hardware es accesorio — el sistema funciona completo sin él.

---

## Estructura del proyecto

```
assistant/
├── main.py                  # Orquestador y punto de entrada
├── config/
│   ├── settings.py          # Variables de entorno y constantes
│   └── prompts.py           # Todos los system prompts del LLM
├── core/
│   ├── memory_manager.py    # Lectura y escritura en SQLite
│   ├── context_builder.py   # Ensamblado del prompt para el LLM
│   ├── llm_client.py        # Interfaz unificada con APIs externas
│   └── session_manager.py   # Ciclo de vida y checkpointing de sesiones
├── tools/
│   ├── tools_manager.py     # Enrutador de herramientas
│   ├── app_launcher.py      # Abrir programas (Windows y Linux)
│   └── file_search.py       # Búsqueda de archivos locales
├── io/
│   ├── io_layer.py          # Clase base abstracta de I/O
│   └── cli_interface.py     # Implementación por terminal (MVP)
├── database/
│   ├── schema.sql           # Definición de tablas
│   ├── seed.py              # Datos iniciales
│   └── db_connection.py     # Conexión única y reutilizable
└── data/                    # Generado en tiempo de ejecución (no en git)
```

---

## Base de datos

El sistema usa **SQLite local** — sin servidor ni configuracion, lo que hace el sistema portable

### Tablas principales

| Tabla | Propósito |
|---|---|
| `students` | Perfil del estudiante |
| `topics` | Temas con nivel de dominio (0–10) |
| `sessions` | Cada conversación con checkpointing |
| `messages` | Historial de mensajes por sesión |
| `errors` | Errores conceptuales frecuentes |
| `session_keywords` | Palabras clave extraídas por sesión |
| `command_mappings` | Mapeo de palabras a comandos del PC |
| `mode_triggers` | Palabras que activan modo tutor o conversación |

### Decisiones de diseño notables

**Resumen por sesión en lugar de historial completo:**
Al cerrar cada sesión, el LLM genera un resumen de 2-3 oraciones que se guarda
en `sessions.summary`. Las sesiones futuras usan ese resumen como contexto,
no los mensajes raw — esto mantiene el uso de tokens bajo control indefinidamente.

**Checkpointing ante cierres inesperados:**
Los mensajes se escriben en la BD en el momento que ocurren, no al cerrar.
El `domain_level` y las keywords se actualizan cada 3 intercambios.
Al arrancar, el sistema detecta sesiones huérfanas y las recupera.

**Multi-usuario preparado:**
Todas las tablas tienen `student_id`. El MVP usa un solo perfil,
pero la estructura soporta múltiples estudiantes sin cambios de esquema.

---

## Instalación

### Requisitos
- Python 3.10 o superior
- Cuenta en [Anthropic Console](https://console.anthropic.com) o cualquier ia de tu preferencia para obtener una API Key

### Pasos (Proximamente se creará un ejecutable para Windows y Linux)

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/assistant.git
cd assistant

# 2. Crear y activar el entorno virtual
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env y añadir tu API Key de la ia de tu eleccion

# 5. Ejecutar el sistema
python main.py
```

La base de datos se crea automáticamente en `data/assistant.db`
en el primer arranque — no se necesita ningún paso adicional.

---

## Compatibilidad

| Sistema operativo | Estado |
|---|---|
| Windows 10 / 11 | ✅ Soportado |
| Ubuntu / Debian  | ✅ Soportado |
| macOS            | ✅ Probable (no testeado) |

El proyecto usa `pathlib` para todas las rutas y fuerza UTF-8 en la salida
estándar, lo que garantiza compatibilidad entre sistemas operativos.

---

## Fases de desarrollo

- **Fase 1 (actual):** Tutor académico + memoria local + interfaz CLI
- **Fase 2:** Búsqueda web integrada + interfaz de voz (STT/TTS)
- **Fase 3:** Control avanzado del PC + automatización de flujos
- **Fase 4:** Hardware físico ESP32 (pantalla + servo + LEDs)
- **Fase 5:** Avatar físico con presencia visual
- **Fase 6:** Memoria en nube + multi-dispositivo

---

## Tecnologías utilizadas

| Tecnología | Rol |
|---|---|
| Python 3.10+ | Lenguaje principal |
| SQLite | Base de datos local persistente |
| Anthropic API | Motor de lenguaje (LLM) |
| python-dotenv | Manejo de variables de entorno |
| pathlib | Rutas multiplataforma |

---

## Autor

Desarrollado por Angel Orellana como proyecto de portafolio.
Ingeniería de Software — Universidad Estatal de la Peninsula de Santa Elena.
