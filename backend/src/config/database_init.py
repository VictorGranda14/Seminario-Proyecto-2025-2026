from __future__ import annotations

import re
import sqlite3
import unicodedata


VIEW_TYPES = {"pais", "rubro", "atraccion"}


def _column_exists(cursor: sqlite3.Cursor, table_name: str, column_name: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table_name})")
    return any(row[1] == column_name for row in cursor.fetchall())


def _table_exists(cursor: sqlite3.Cursor, table_name: str) -> bool:
    cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?", (table_name,))
    return cursor.fetchone() is not None


def _slugify(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    while "__" in text:
        text = text.replace("__", "_")
    return text.strip("_") or "sin_clasificar"


def _migrate_metricas_consolidadas(cursor: sqlite3.Cursor) -> None:
    if not _table_exists(cursor, "metricas_consolidadas"):
        return

    if _column_exists(cursor, "metricas_consolidadas", "identificador_vista"):
        return

    cursor.execute(
        """
        CREATE TABLE metricas_consolidadas_new (
            identificador_vista TEXT PRIMARY KEY,
            nombre_vista TEXT NOT NULL,
            tipo_vista TEXT NOT NULL CHECK (tipo_vista IN ('pais', 'rubro', 'atraccion')),
            json_completo TEXT NOT NULL,
            ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute("SELECT nombre_atraccion, json_completo, ultima_actualizacion FROM metricas_consolidadas")
    rows = cursor.fetchall()

    for row in rows:
        nombre_vista = row[0]
        identificador_vista = _slugify(nombre_vista)
        cursor.execute(
            """
            INSERT INTO metricas_consolidadas_new (
                identificador_vista,
                nombre_vista,
                tipo_vista,
                json_completo,
                ultima_actualizacion
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (identificador_vista, nombre_vista, "atraccion", row[1], row[2]),
        )

    cursor.execute("DROP TABLE metricas_consolidadas")
    cursor.execute("ALTER TABLE metricas_consolidadas_new RENAME TO metricas_consolidadas")


def initialize_database(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS analisis_crudo (
            id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
            id_comentario TEXT NOT NULL,
            atraccion TEXT NOT NULL,
            rubro TEXT NOT NULL DEFAULT 'Sin clasificar',
            texto_original TEXT NOT NULL,
            modelo_usado TEXT NOT NULL,
            polaridad_general_comentario TEXT,
            aspecto_detectado TEXT,
            opinion_detectada TEXT, 
            polaridad_aspecto TEXT,
            dimension_tx TEXT,
            fecha_procesamiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    if not _column_exists(cursor, "analisis_crudo", "opinion_detectada"):
        cursor.execute("ALTER TABLE analisis_crudo ADD COLUMN opinion_detectada TEXT")

    _migrate_metricas_consolidadas(cursor)

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS metricas_consolidadas (
            identificador_vista TEXT PRIMARY KEY,
            nombre_vista TEXT NOT NULL,
            tipo_vista TEXT NOT NULL CHECK (tipo_vista IN ('pais', 'rubro', 'atraccion')),
            json_completo TEXT NOT NULL,
            ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_analisis_crudo_atraccion ON analisis_crudo(atraccion)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_analisis_crudo_rubro ON analisis_crudo(rubro)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_analisis_crudo_modelo ON analisis_crudo(modelo_usado)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_analisis_crudo_comentario ON analisis_crudo(id_comentario)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_metricas_tipo_vista ON metricas_consolidadas(tipo_vista)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_metricas_nombre_vista ON metricas_consolidadas(nombre_vista)")
    conn.commit()
