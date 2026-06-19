from __future__ import annotations

import json
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.utils.database import DBManager

DEFAULT_DB = "data/turismo.sqlite"

app = FastAPI(title="Seminario Proyecto API", version="0.1.0")

allowed_origins = os.getenv(
	"ALLOWED_ORIGINS",
	"http://localhost:3000,http://127.0.0.1:3000",
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=[origin.strip() for origin in allowed_origins.split(",") if origin.strip()],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


def get_default_db_path() -> str:
	return os.getenv("DATABASE_URL", DEFAULT_DB)


def resolve_database_path(database: str | None) -> str:
	return database or get_default_db_path()


def get_db(database_path: str | None = None) -> DBManager:
	return DBManager(resolve_database_path(database_path))


@app.get("/health")
def health():
	return {"status": "ok", "default_database": get_default_db_path()}


@app.get("/metricas")
def list_metricas(database: str | None = None, tipo_vista: str | None = None):
	db = get_db(database)
	try:
		rows = db.fetch_metricas_por_tipo(tipo_vista) if tipo_vista else (
			db.fetch_metricas_por_tipo("atraccion") + db.fetch_metricas_por_tipo("rubro") + db.fetch_metricas_por_tipo("pais")
		)
		return [
			{
				"identificador_vista": row["identificador_vista"],
				"nombre_vista": row["nombre_vista"],
				"tipo_vista": row["tipo_vista"],
				"ultima_actualizacion": row["ultima_actualizacion"],
			}
			for row in rows
		]
	finally:
		db.close()


@app.get("/metricas/disponibles")
def list_all_metricas(database: str | None = None):
	return list_metricas(database=database)


@app.get("/metricas/{identificador_vista}")
def get_metricas(identificador_vista: str, database: str | None = None, tipo_vista: str | None = None):
	db = get_db(database)
	try:
		row = db.fetch_metricas_consolidadas(identificador_vista, tipo_vista)
		if row is None:
			raise HTTPException(status_code=404, detail="No se encontraron métricas consolidadas para esa vista.")

		payload = json.loads(row["json_completo"])
		payload["identificador_vista"] = row["identificador_vista"]
		payload["nombre_vista"] = row["nombre_vista"]
		payload["tipo_vista"] = row["tipo_vista"]
		payload["ultima_actualizacion"] = row["ultima_actualizacion"]
		return payload
	finally:
		db.close()