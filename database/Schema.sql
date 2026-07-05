-- Esquema completo de la base de datos del asistente tutor.
-- Se aplica automáticamente en el primer arranque.

CREATE TABLE IF NOT EXISTS estudiantes (
    id_estudiante              INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre            TEXT NOT NULL,
    estilo_aprendizaje  TEXT DEFAULT 'paso_a_paso',
    creado_en      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS temas (
    id_tema               INTEGER PRIMARY KEY AUTOINCREMENT,
    id_estudiante       INTEGER NOT NULL REFERENCES estudiantes(id_estudiante),
    nombre             TEXT NOT NULL,
    categoria         TEXT,
    nivel_dominio   INTEGER 
                    CHECK (nivel_dominio BETWEEN 0 AND 10)
                    DEFAULT 0 ,
    veces_revisado   INTEGER DEFAULT 0,
    ultima_revision TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sesiones (
    id_sesion                 INTEGER PRIMARY KEY AUTOINCREMENT,
    id_estudiante         INTEGER NOT NULL REFERENCES estudiantes(id_estudiante),
    id_tema           INTEGER REFERENCES temas(id_tema),
    modo               TEXT DEFAULT 'tutor',
    resumen            TEXT,
    empezado_en         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    terminado_en           TIMESTAMP,
    ultimo_guardado TIMESTAMP,
    veces_guardado   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS mensajes (
    id_mensaje         INTEGER PRIMARY KEY AUTOINCREMENT,
    id_sesion INTEGER NOT NULL REFERENCES sesiones(id_sesion),
    rol       TEXT NOT NULL,
    contenido    TEXT NOT NULL,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS errores (
    id_error           INTEGER PRIMARY KEY AUTOINCREMENT,
    id_estudiante   INTEGER NOT NULL REFERENCES estudiantes(id_estudiante),
    id_tema     INTEGER REFERENCES temas(id_tema),
    descripcion  TEXT NOT NULL,
    frecuencia    INTEGER DEFAULT 1,
    ultima_vista TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS palabras_clave_de_sesion (
    id_palabra_clave         INTEGER PRIMARY KEY AUTOINCREMENT,
    id_sesion INTEGER NOT NULL REFERENCES sesiones(id_sesion),
    id_tema   INTEGER REFERENCES temas(id_tema),
    palabra_clave    TEXT NOT NULL,
    frecuencia  INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS mapa_comandos (
    id_comando             INTEGER PRIMARY KEY AUTOINCREMENT,
    palabra_clave        TEXT UNIQUE NOT NULL,
    tipo_comando   TEXT NOT NULL,
    target_windows TEXT,
    target_linux   TEXT,
    veces_usado    INTEGER DEFAULT 0,
    ultimo_uso   TIMESTAMP
);

CREATE TABLE IF NOT EXISTS triggers_de_modo (
    id_trigger          INTEGER PRIMARY KEY AUTOINCREMENT,
    palabra_clave     TEXT UNIQUE NOT NULL,
    modo_objetivo TEXT NOT NULL,
    peso      REAL DEFAULT 0.5
);