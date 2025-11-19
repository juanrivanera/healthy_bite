import sqlite3
import os

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "healthy_bite.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    # Tabla cliente
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cliente (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        disciplina TEXT,
        plan_id INTEGER,
        altura REAL,
        peso REAL,
        objetivo TEXT
    )
    """)

    # Tabla nutricionista
    cur.execute("""
    CREATE TABLE IF NOT EXISTS nutricionista (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        matricula TEXT NOT NULL
    )
    """)

    # Tabla plan
    cur.execute("""
    CREATE TABLE IF NOT EXISTS plan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT NOT NULL,
        precio REAL NOT NULL
    )
    """)

    # Tabla plato
    cur.execute("""
    CREATE TABLE IF NOT EXISTS plato (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT
    )
    """)

    # Tabla recomendacion
    cur.execute("""
    CREATE TABLE IF NOT EXISTS recomendacion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nutricionista_id INTEGER,
        cliente_id INTEGER,
        texto TEXT,
        fecha TEXT
    )
    """)

    # Tabla pedido
    cur.execute("""
    CREATE TABLE IF NOT EXISTS pedido (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        plato_id INTEGER NOT NULL,
        restriccion TEXT,
        comentarios TEXT,
        fecha TEXT,
        estado TEXT NOT NULL DEFAULT 'Pendiente'
    )
    """)

    # ALTERs por si la tabla ya existía
    try:
        cur.execute("ALTER TABLE cliente ADD COLUMN altura REAL")
    except sqlite3.OperationalError:
        pass

    try:
        cur.execute("ALTER TABLE cliente ADD COLUMN peso REAL")
    except sqlite3.OperationalError:
        pass

    try:
        cur.execute("ALTER TABLE cliente ADD COLUMN objetivo TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cur.execute("ALTER TABLE cliente ADD COLUMN plan_id INTEGER")
    except sqlite3.OperationalError:
        pass

    try:
        cur.execute(
            "ALTER TABLE pedido ADD COLUMN estado TEXT NOT NULL DEFAULT 'Pendiente'"
        )
    except sqlite3.OperationalError:
        pass

    # Datos iniciales de plan
    cur.execute("SELECT COUNT(*) AS c FROM plan")
    row = cur.fetchone()
    if row["c"] == 0:
        cur.executemany(
            "INSERT INTO plan (nombre, descripcion, precio) VALUES (?, ?, ?)",
            [
                (
                    "Plan Básico",
                    "10 comidas mensuales, pensado para quienes entrenan 2 a 3 veces por semana.",
                    75000,
                ),
                (
                    "Plan Intermedio",
                    "20 comidas mensuales, incluye colaciones para entrenamientos moderados.",
                    100000,
                ),
                (
                    "Plan Full",
                    "30 comidas mensuales, ideal para deportistas de alto rendimiento.",
                    125000,
                ),
            ],
        )

    # Datos iniciales de platos
    cur.execute("SELECT COUNT(*) AS c FROM plato")
    row = cur.fetchone()
    if row["c"] == 0:
        cur.executemany(
            "INSERT INTO plato (nombre, descripcion) VALUES (?, ?)",
            [
                (
                    "Pollo grillado con vegetales",
                    "Pechuga de pollo grillada con zanahoria, brócoli y chauchas al vapor.",
                ),
                (
                    "Bowl vegetariano con quinoa",
                    "Quinoa con mix de verduras salteadas y garbanzos.",
                ),
                (
                    "Ensalada fresca con atún",
                    "Mix verde con atún en agua, tomate cherry y huevo duro.",
                ),
            ],
        )

    conn.commit()
    conn.close()
