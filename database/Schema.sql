-- Esquema completo de la base de datos del asistente tutor.
-- Se aplica automáticamente en el primer arranque.

CREATE TABLE IF NOT EXISTS students (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    learning_style  TEXT DEFAULT 'paso_a_paso',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS topics (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id       INTEGER NOT NULL REFERENCES students(id),
    name             TEXT NOT NULL,
    category         TEXT,
    domain_level     INTEGER DEFAULT 0,
    times_reviewed   INTEGER DEFAULT 0,
    last_reviewed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id         INTEGER NOT NULL REFERENCES students(id),
    topic_id           INTEGER REFERENCES topics(id),
    mode               TEXT DEFAULT 'tutor',
    summary            TEXT,
    started_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at           TIMESTAMP,
    last_checkpoint_at TIMESTAMP,
    checkpoint_count   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS messages (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES sessions(id),
    role       TEXT NOT NULL,
    content    TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS errors (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id   INTEGER NOT NULL REFERENCES students(id),
    topic_id     INTEGER REFERENCES topics(id),
    description  TEXT NOT NULL,
    frequency    INTEGER DEFAULT 1,
    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS session_keywords (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES sessions(id),
    topic_id   INTEGER REFERENCES topics(id),
    keyword    TEXT NOT NULL,
    frequency  INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS command_mappings (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword        TEXT UNIQUE NOT NULL,
    command_type   TEXT NOT NULL,
    target_windows TEXT,
    target_linux   TEXT,
    usage_count    INTEGER DEFAULT 0,
    last_used_at   TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mode_triggers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword     TEXT UNIQUE NOT NULL,
    target_mode TEXT NOT NULL,
    weight      REAL DEFAULT 0.5
);