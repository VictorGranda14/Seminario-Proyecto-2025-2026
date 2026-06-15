import json
import os
import sqlite3
from datetime import datetime, timezone

from src.config.database_init import initialize_database

class DBManager:
    def __init__(self, db_path="data/turismo.sqlite"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        initialize_database(self.conn)

    def save_raw_rows(self, rows):
        if not rows:
            return

        cursor = self.conn.cursor()
        cursor.executemany(
            """
            INSERT INTO analisis_crudo (
                id_comentario,
                atraccion,
                rubro,
                texto_original,
                modelo_usado,
                polaridad_general_comentario,
                aspecto_detectado,
                opinion_detectada,
                polaridad_aspecto,
                dimension_tx
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    row["id_comentario"],
                    row["atraccion"],
                    row.get("rubro", "Sin clasificar"),
                    row["texto_original"],
                    row["modelo_usado"],
                    row.get("polaridad_general_comentario"),
                    row.get("aspecto_detectado"),
                    row.get("opinion_detectada"),
                    row.get("polaridad_aspecto"),
                    row.get("dimension_tx"),
                )
                for row in rows
            ],
        )
        self.conn.commit()

    def upsert_metricas_consolidadas(self, identificador_vista: str, nombre_vista: str, tipo_vista: str, json_completo: dict):
        cursor = self.conn.cursor()
        payload = json.dumps(json_completo, ensure_ascii=False)
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute(
            """
            INSERT INTO metricas_consolidadas (identificador_vista, nombre_vista, tipo_vista, json_completo, ultima_actualizacion)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(identificador_vista)
            DO UPDATE SET nombre_vista = excluded.nombre_vista,
                          tipo_vista = excluded.tipo_vista,
                          json_completo = excluded.json_completo,
                          ultima_actualizacion = excluded.ultima_actualizacion
            """,
            (identificador_vista, nombre_vista, tipo_vista, payload, now),
        )
        self.conn.commit()

    def fetch_metricas_consolidadas(self, identificador_vista: str, tipo_vista: str | None = None):
        cursor = self.conn.cursor()
        query = "SELECT identificador_vista, nombre_vista, tipo_vista, json_completo, ultima_actualizacion FROM metricas_consolidadas WHERE identificador_vista = ?"
        params = [identificador_vista]

        if tipo_vista:
            query += " AND tipo_vista = ?"
            params.append(tipo_vista)

        cursor.execute(query, params)
        row = cursor.fetchone()
        
        if row is None:
            return None
        return dict(row)

    def fetch_metricas_por_tipo(self, tipo_vista: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT identificador_vista, nombre_vista, tipo_vista, json_completo, ultima_actualizacion FROM metricas_consolidadas WHERE tipo_vista = ? ORDER BY nombre_vista",
            (tipo_vista,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()