import argparse
import time

# Importamos los dos motores de nuestra nueva arquitectura
from src.data_prep.csv_a_sqlite import poblar_sqlite_desde_csv
from src.analitica.agregador import aggregate_all_views

DEFAULT_INPUT = "data/outputs/output_llm.csv"
DEFAULT_DB = "data/turismo.sqlite"

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Orquestador ETL: Desde el CSV del LLM hasta los JSON de React.")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="Ruta del CSV generado por el modelo LLM.")
    parser.add_argument("--database", default=DEFAULT_DB, help="Ruta de la base de datos SQLite.")
    parser.add_argument("--skip-load", action="store_true", help="Salta la carga del CSV y solo re-calcula las métricas.")
    return parser

def main() -> None:
    args = build_parser().parse_args()
    start_time = time.time()

    print("=== INICIANDO PIPELINE ETL ===")
    
    # FASE 1: Extraer del CSV y Cargar a SQLite (Staging)
    if not args.skip_load:
        print(f"\n[Fase 1] Cargando datos desde {args.input} hacia la Base de Datos...")
        try:
            poblar_sqlite_desde_csv(args.input, args.database)
            print("[Fase 1] Carga completada exitosamente.")
        except Exception as e:
            print(f"[ERROR FASE 1] Fallo al cargar el CSV a SQLite: {e}")
            return
    else:
        print("\n[Fase 1] Omitida por el usuario (--skip-load).")

    # FASE 2: Transformar y Generar JSONs (Agregación)
    print(f"\n[Fase 2] Consolidando métricas y generando JSONs para el Dashboard...")
    try:
        # aggregate_all_views retorna una lista de todos los JSONs generados, pero ya los guarda en SQLite internamente
        vistas_generadas = aggregate_all_views(args.database)
        print(f"[Fase 2] Se generaron y guardaron {len(vistas_generadas)} vistas (País, Rubros, Atracciones).")
    except Exception as e:
        print(f"[ERROR FASE 2] Falló el motor de agregación: {e}")
        return

    elapsed = round(time.time() - start_time, 2)
    print(f"\n=== PIPELINE FINALIZADO CON ÉXITO EN {elapsed} SEGUNDOS ===")

if __name__ == "__main__":
    main()