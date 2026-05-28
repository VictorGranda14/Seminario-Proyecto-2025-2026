from __future__ import annotations

import argparse
import os
import sqlite3

import pandas as pd

from src.models.aspect_miner import AspectMinerLocal


SUPPORTED_MODELS = {"local"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Orquestador principal del backend")
    parser.add_argument(
        "--model",
        type=str,
        default="local",
        choices=sorted(SUPPORTED_MODELS),
        help="Modelo a ejecutar. Por ahora solo local.",
    )
    parser.add_argument(
        "--attraction",
        type=str,
        default="Vina Santa Rita",
        help="Atracción a procesar.",
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/processed/Comentarios_en_Final.csv",
        help="Archivo CSV ya preprocesado.",
    )
    parser.add_argument(
        "--database",
        type=str,
        default="data/outputs/resultados_nlp.db",
        help="Ruta de salida SQLite.",
    )
    return parser


def get_model(model_name: str):
    if model_name == "local":
        return AspectMinerLocal()
    raise ValueError(f"Modelo no soportado: {model_name}")


def ensure_schema(cursor: sqlite3.Cursor) -> None:
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS aspect_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            comment_id TEXT,
            attraction TEXT,
            aspect TEXT,
            opinion TEXT,
            sentiment TEXT
        )
        """
    )


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    print("Iniciando Orquestador Principal...")

    try:
        df = pd.read_csv(args.input, sep=';')
    except FileNotFoundError:
        print(f"No se encontró el dataset en {args.input}.")
        return

    if 'Comment_ID' not in df.columns:
        if 'ID' in df.columns:
            df.rename(columns={'ID': 'Comment_ID'}, inplace=True)
        else:
            df.insert(0, 'Comment_ID', [f"REV-{i+1}" for i in range(len(df))])

    if args.model not in SUPPORTED_MODELS:
        print(f"Modelo no soportado: {args.model}")
        return

    miner = get_model(args.model)
    os.makedirs(os.path.dirname(args.database), exist_ok=True)
    conn = sqlite3.connect(args.database)
    cursor = conn.cursor()
    ensure_schema(cursor)
    conn.commit()

    procesados = pd.read_sql_query("SELECT DISTINCT comment_id FROM aspect_results", conn)['comment_id'].tolist()

    atraccion = args.attraction
    df_atraccion = df[df['attraction_name'] == atraccion].copy()

    if df_atraccion.empty:
        print(f"No se encontraron comentarios para '{atraccion}'. Revisa el nombre exacto.")
        conn.close()
        return

    df_a_procesar = df_atraccion[~df_atraccion['Comment_ID'].isin(procesados)]
    total = len(df_a_procesar)

    print(f"\nProcesando '{atraccion}' con modelo '{args.model}': {total} comentarios nuevos (saltando {len(df_atraccion) - total} ya procesados).")

    contador = 0
    for _, row in df_a_procesar.iterrows():
        comentario_id = row['Comment_ID']
        texto = str(row['review_text'])

        resultados = miner.extract_aspects(texto)

        for res in resultados:
            cursor.execute(
                '''
                INSERT INTO aspect_results (comment_id, attraction, aspect, opinion, sentiment)
                VALUES (?, ?, ?, ?, ?)
                ''',
                (comentario_id, atraccion, res['aspect'], res['opinion'], res['sentiment'])
            )

        conn.commit()
        contador += 1

        if contador % 50 == 0 or contador == total:
            print(f"Progreso {atraccion}: {contador}/{total} comentarios procesados...")

    conn.close()
    print("\nProceso Masivo Finalizado.")


if __name__ == "__main__":
    main()