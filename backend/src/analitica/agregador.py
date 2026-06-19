from __future__ import annotations

import argparse
import json
import re
from collections import Counter
import unicodedata
from typing import Iterable

import pandas as pd

from src.utils.database import DBManager

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Agregador de métricas para el dashboard")
    parser.add_argument("--database", default="C:\\Users\\ramiro\\Seminario-Proyecto-2025-2026\\backend\\data\\turismo.sqlite", help="Ruta de la base SQLite.")
    parser.add_argument("--attraction", default=None, help="Atracción a consolidar.")
    return parser


def normalize_sentiment(value) -> str:
    text = str(value or "").strip().lower()
    if text in {"positive", "positivo", "pos"}:
        return "positive"
    if text in {"negative", "negativo", "neg"}:
        return "negative"
    if text in {"mixed", "neutral", "neutro", "unknown", ""}:
        return "neutral"
    return "neutral"


def load_raw_dataframe(db: DBManager, attraction: str | None = None) -> pd.DataFrame:
    query = "SELECT * FROM analisis_crudo"
    clauses: list[str] = []
    params: list[str] = []

    if attraction:
        clauses.append("atraccion = ?")
        params.append(attraction)

    if clauses:
        query += " WHERE " + " AND ".join(clauses)

    return pd.read_sql_query(query, db.conn, params=params)


def extract_top_texts(texts: Iterable[str], limit: int = 3) -> list[str]:
    counts = Counter(str(text or "").strip() for text in texts if str(text or "").strip())
    return [text for text, _ in counts.most_common(limit)]


def build_sentiment_ratio(df: pd.DataFrame) -> dict:
    comments = df.groupby("id_comentario", as_index=False)["polaridad_general_comentario"].first()
    counts = comments["polaridad_general_comentario"].map(normalize_sentiment).value_counts().to_dict()
    total = max(len(comments), 1)

    positive = round((counts.get("positive", 0) / total) * 100)
    neutral = round((counts.get("neutral", 0) / total) * 100)
    negative = max(0, 100 - positive - neutral)

    return {
        "positive": positive,
        "neutral": neutral,
        "negative": negative,
    }


def build_tx_dimensions(df: pd.DataFrame) -> list[dict]:
    comentarios_unicos = df.drop_duplicates(subset=['id_comentario']).copy()
    dimensiones_stats = {}
    
    for _, row in comentarios_unicos.iterrows():
        dim_text = str(row.get("dimension_tx", ""))
        dim_text = dim_text.replace('[', '').replace(']', '').replace('"', '').replace("'", "")
        
        if not dim_text.strip():
            continue
            
        dims = [d.strip() for d in dim_text.split(',') if d.strip()]
        
        # Extraemos la polaridad general del comentario
        polaridad = normalize_sentiment(row.get("polaridad_general_comentario", ""))
        
        for dim in dims:
            if dim.lower() in ["sin clasificar", ""]:
                continue
                
            if dim not in dimensiones_stats:
                dimensiones_stats[dim] = {"total": 0, "positive": 0, "negative": 0}
                
            # Sumamos al total general
            dimensiones_stats[dim]["total"] += 1
            
            # Repartición binaria: o es positivo, o es fricción/neutro
            if polaridad == "positive":
                dimensiones_stats[dim]["positive"] += 1
            elif polaridad in ["negative", "neutral"]:
                dimensiones_stats[dim]["negative"] += 1

    if not dimensiones_stats:
        return []

    # Ordenamos de mayor a menor según el total de apariciones
    return [
        {
            "dimension": dim,
            "total": stats["total"],
            "positive": stats["positive"],
            "negative": stats["negative"]
        }
        for dim, stats in sorted(dimensiones_stats.items(), key=lambda item: item[1]["total"], reverse=True)
    ]


def build_dimension_totals(df: pd.DataFrame) -> list[dict]:
    comentarios_unicos = df.drop_duplicates(subset=['id_comentario']).copy()
    dimensiones_stats = {}
    total_general = 0
    
    for _, row in comentarios_unicos.iterrows():
        dim_text = str(row.get("dimension_tx", ""))
        dim_text = dim_text.replace('[', '').replace(']', '').replace('"', '').replace("'", "")
        
        if not dim_text.strip():
            continue
            
        dims = [d.strip() for d in dim_text.split(',') if d.strip()]
        polaridad = normalize_sentiment(row.get("polaridad_general_comentario", ""))
        
        for dim in dims:
            if dim.lower() in ["sin clasificar", ""]:
                continue
                
            if dim not in dimensiones_stats:
                dimensiones_stats[dim] = {"count": 0, "positive": 0, "negative": 0}
                
            dimensiones_stats[dim]["count"] += 1
            total_general += 1
            
            # Repartición binaria para las barras globales
            if polaridad == "positive":
                dimensiones_stats[dim]["positive"] += 1
            elif polaridad in ["negative", "neutral"]:
                dimensiones_stats[dim]["negative"] += 1

    if not dimensiones_stats:
        return []
        
    total_general = max(total_general, 1)
    
    return [
        {
            "dimension": dim,
            "count": stats["count"],
            "percentage": round((stats["count"] / total_general) * 100, 2),
            "positive": stats["positive"],
            "negative": stats["negative"]
        }
        for dim, stats in sorted(dimensiones_stats.items(), key=lambda item: item[1]["count"], reverse=True)
    ]


def build_comment_rankings(df: pd.DataFrame, column_name: str, label_name: str, limit: int = 5) -> list[dict]:
    if column_name not in df.columns:
        return []

    counts = df.groupby(column_name)["id_comentario"].nunique().sort_values(ascending=False)
    return [
        {label_name: str(name), "commentCount": int(count)}
        for name, count in counts.head(limit).items()
    ]


def build_summary_overview(df: pd.DataFrame) -> dict:
    total_comments = int(df["id_comentario"].nunique())
    total_attractions = int(df["atraccion"].nunique()) if "atraccion" in df.columns else 0
    total_rubros = int(df["rubro"].nunique()) if "rubro" in df.columns else 0

    return {
        "totalComments": total_comments,
        "totalAttractions": total_attractions,
        "totalRubros": total_rubros,
        "dimensionTotals": build_dimension_totals(df),
        "topAttractions": build_comment_rankings(df, "atraccion", "attraction"),
        "topRubros": build_comment_rankings(df, "rubro", "rubro"),
    }


def normalize_identifier(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_") or "sin_clasificar"


def build_view_payload(df: pd.DataFrame, *, tipo_vista: str, identificador_vista: str, nombre_vista: str) -> dict:
    cleaned_df = df.copy()
    cleaned_df["rubro"] = cleaned_df.get("rubro", "Sin clasificar").fillna("Sin clasificar")

    total_reviews = int(cleaned_df["id_comentario"].nunique())
    sentiment_ratio = build_sentiment_ratio(cleaned_df)
    tx_dimensions = build_tx_dimensions(cleaned_df)
    aspect_analysis = build_aspect_analysis(cleaned_df, tipo_vista)
    macro_categories = build_macro_categories(cleaned_df)
    summary_overview = build_summary_overview(cleaned_df)

    return {
        "vistaInfo": {
            "identificadorVista": identificador_vista,
            "nombreVista": nombre_vista,
            "tipoVista": tipo_vista,
            "totalReviews": total_reviews,
            "sentimentRatio": sentiment_ratio,
        },
        "summaryOverview": summary_overview,
        "executiveSummary": build_executive_summary(nombre_vista, tipo_vista, sentiment_ratio, tx_dimensions, aspect_analysis, summary_overview),
        "txDimensions": tx_dimensions,
        "macroCategories": macro_categories,
        "aspectAnalysis": aspect_analysis,
    }
    

def build_aspect_analysis(df: pd.DataFrame, tipo_vista: str) -> dict:
    if tipo_vista == "pais":
        columna_agrupacion = "categoria_oficial"
    else:
        columna_agrupacion = "aspecto_consolidado"

    if columna_agrupacion not in df.columns:
        columna_agrupacion = "aspecto_detectado"

    grouped = df.groupby(columna_agrupacion)
    strengths = []
    alerts = []

    for aspect, group in grouped:
        aspect_name = str(aspect or "general").strip()
        if aspect_name.lower() in ["general", "sin clasificar", ""]:
            continue

        es_positivo = group["polaridad_aspecto"].map(normalize_sentiment) == "positive"
        es_negativo = group["polaridad_aspecto"].map(normalize_sentiment) == "negative"

        positive = int(es_positivo.sum())
        negative = int(es_negativo.sum())
        total_freq = len(group)

        # --- PROCESAR FORTALEZAS ---
        if positive > 0:
            opiniones_pos_raw = group.loc[es_positivo, "opinion_detectada"].dropna().astype(str).tolist()
            opiniones_pos_limpias = []
            
            for op in opiniones_pos_raw:
                for palabra in op.split(','):
                    palabra_limpia = palabra.strip().lower()
                    if palabra_limpia and palabra_limpia != 'nan':
                        opiniones_pos_limpias.append(palabra_limpia)

            top_opinions_pos = [op for op, _ in Counter(opiniones_pos_limpias).most_common(5)]
            
            entry_pos = {
                "aspect": aspect_name.title() if tipo_vista != "pais" else aspect_name,
                "freq": positive, 
                "totalFreq": total_freq,
                "keywords": top_opinions_pos,
                "positiveCount": positive,
                "negativeCount": negative,
            }
            strengths.append((positive, total_freq, aspect_name, entry_pos))

        # --- PROCESAR ALERTAS ---
        if negative > 0:
            opiniones_neg_raw = group.loc[es_negativo, "opinion_detectada"].dropna().astype(str).tolist()
            opiniones_neg_limpias = []
            
            for op in opiniones_neg_raw:
                for palabra in op.split(','):
                    palabra_limpia = palabra.strip().lower()
                    if palabra_limpia and palabra_limpia != 'nan':
                        opiniones_neg_limpias.append(palabra_limpia)

            top_opinions_neg = [op for op, _ in Counter(opiniones_neg_limpias).most_common(5)]
            
            entry_neg = {
                "aspect": aspect_name.title() if tipo_vista != "pais" else aspect_name,
                "freq": negative,
                "totalFreq": total_freq,
                "keywords": top_opinions_neg,
                "positiveCount": positive,
                "negativeCount": negative,
            }
            alerts.append((negative, total_freq, aspect_name, entry_neg))

    strengths = [item[-1] for item in sorted(strengths, key=lambda item: (item[0], item[1]), reverse=True)[:5]]
    alerts = [item[-1] for item in sorted(alerts, key=lambda item: (item[0], item[1]), reverse=True)[:5]]

    return {
        "strengths": strengths,
        "alerts": alerts,
    }


def build_executive_summary(*args, **kwargs) -> str:
    return "Resumen ejecutivo en construcción. Aquí se inyectará el análisis semántico del LLM en la fase final."


def build_macro_categories(df: pd.DataFrame) -> list[dict]:
    if "categoria_oficial" not in df.columns:
        return []

    df_cat = df.dropna(subset=["categoria_oficial"]).copy()
    grouped = df_cat.groupby("categoria_oficial")
    resultados = []

    for cat, group in grouped:
        cat_name = str(cat).strip()
        if cat_name.lower() in ["general", "sin clasificar", ""]:
            continue

        positive = (group["polaridad_aspecto"].map(normalize_sentiment) == "positive").sum()
        negative = (group["polaridad_aspecto"].map(normalize_sentiment) == "negative").sum()
        freq = len(group)

        resultados.append({
            "category": cat_name,
            "freq": int(freq),
            "positiveCount": int(positive),
            "negativeCount": int(negative),
        })

    return sorted(resultados, key=lambda x: x["freq"], reverse=True)

def get_existing_summary(db: DBManager, identificador_vista: str) -> str | None:
    """Busca el JSON existente en la BD y rescata el resumen si ya fue generado por la IA."""
    try:
        query = "SELECT json_completo FROM metricas_consolidadas WHERE identificador_vista = ?"
        cursor = db.conn.cursor()
        cursor.execute(query, (identificador_vista,))
        row = cursor.fetchone()
        
        if row and row[0]:
            datos = json.loads(row[0])
            if isinstance(datos, str):
                datos = json.loads(datos)
            
            resumen_actual = datos.get("executiveSummary", "")
            
            if resumen_actual and "Resumen ejecutivo en construcción" not in resumen_actual:
                return resumen_actual
    except Exception as e:
        pass
        
    return None

def aggregate_view(
    db: DBManager,
    df: pd.DataFrame,
    *,
    tipo_vista: str,
    identificador_vista: str,
    nombre_vista: str,
) -> dict:
    payload = build_view_payload(
        df,
        tipo_vista=tipo_vista,
        identificador_vista=identificador_vista,
        nombre_vista=nombre_vista,
    )
    
    resumen_guardado = get_existing_summary(db, identificador_vista)
    
    if resumen_guardado:
        payload["executiveSummary"] = resumen_guardado

    db.upsert_metricas_consolidadas(identificador_vista, nombre_vista, tipo_vista, payload)
    return payload


def aggregate_attraction(db_path: str, attraction: str) -> dict:
    db = DBManager(db_path)
    try:
        df = load_raw_dataframe(db, attraction)
        if df.empty:
            raise ValueError(f"No hay datos para la atracción '{attraction}'.")

        return aggregate_view(
            db,
            df,
            tipo_vista="atraccion",
            identificador_vista=normalize_identifier(attraction),
            nombre_vista=attraction,
        )
    finally:
        db.close()


def aggregate_all_views(db_path: str) -> list[dict]:
    db = DBManager(db_path)
    try:
        print("-> Leyendo la tabla 'analisis_crudo' desde SQLite...")
        df = load_raw_dataframe(db)
        if df.empty:
            raise ValueError("No hay datos para consolidar.")
        
        print(f"-> Base cargada exitosamente. Total de filas en memoria: {len(df)}")
        payloads: list[dict] = []

        grupos_atracciones = list(df.groupby("atraccion"))
        total_atracciones = len(grupos_atracciones)
        print(f"\n[Fase 1/3] Procesando {total_atracciones} atracciones turísticas...")
        
        for i, (attraction_name, attraction_group) in enumerate(grupos_atracciones, 1):
            if i % 50 == 0 or i == 1 or i == total_atracciones:
                print(f"   ↳ Progress: [{i}/{total_atracciones}] Consolidando: '{attraction_name}'...")
                
            payloads.append(
                aggregate_view(
                    db,
                    attraction_group,
                    tipo_vista="atraccion",
                    identificador_vista=normalize_identifier(attraction_name),
                    nombre_vista=str(attraction_name),
                )
            )

        grupos_rubros = list(df.groupby(df["rubro"].fillna("Sin clasificar")))
        total_rubros = len(grupos_rubros)
        print(f"\n[Fase 2/3] Procesando {total_rubros} rubros comerciales...")
        
        for i, (rubro_name, rubro_group) in enumerate(grupos_rubros, 1):
            print(f"   ↳ Progress: [{i}/{total_rubros}] Consolidando rubro: '{rubro_name}'...")
            payloads.append(
                aggregate_view(
                    db,
                    rubro_group,
                    tipo_vista="rubro",
                    identificador_vista=f"rubro_{normalize_identifier(rubro_name)}",
                    nombre_vista=str(rubro_name),
                )
            )

        print("\n[Fase 3/3] Compilando e inyectando vista macro-nacional ('chile_global')...")
        payloads.append(
            aggregate_view(
                db,
                df,
                tipo_vista="pais",
                identificador_vista="chile_global",
                nombre_vista="Chile",
            )
        )

        return payloads
    finally:
        db.close()


def main() -> None:
    args = build_parser().parse_args()
    print("==================================================")
    print("        INICIANDO PIPELINE DE AGREGACIÓN          ")
    print("==================================================")
    
    if args.attraction:
        payload = aggregate_attraction(args.database, args.attraction)
        print(f"\nÉxito: Se consolidó la atracción individual: '{args.attraction}'.")
    else:
        payloads = aggregate_all_views(args.database)
        print("\n==================================================")
        print("          EJECUCIÓN FINALIZADA CON ÉXITO          ")
        print("==================================================")
        print(f"Total de vistas calculadas e inyectadas: {len(payloads)}")
        print(f"Destino: Tabla 'metricas_consolidadas' en '{args.database}'")
        print("==================================================")


if __name__ == "__main__":
    main()