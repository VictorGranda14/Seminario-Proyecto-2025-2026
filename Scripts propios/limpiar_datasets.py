import os
import re
import pandas as pd

COLUMNAS_A_ELIMINAR = [
    "language", "username", "title", "written_date",
    "visit_date", "contribution", "sentiment", "sentiment_score"
]

def limpiar_review_text(serie: pd.Series) -> pd.Series:
    """
    Reemplaza guiones y saltos de línea por espacio en review_text,
    colapsa espacios múltiples y recorta extremos.
    Abarca -, ‐ - ‒ — ― y \n, \r, \t.
    """
    if serie.isna().all():
        return serie

    # Convertir a string solo donde no hay NaN (evita "nan" como texto)
    serie = serie.astype("string")  # dtype str NA-aware

    # Reemplazar guiones y saltos de línea/tab por espacio
    # Rango de guiones unicode: U+2010..U+2015
    patron = r'[\-\u2010-\u2015]|\r?\n|\t'
    serie = serie.str.replace(patron, ' ', regex=True)

    # Colapsar espacios múltiples y recortar
    serie = serie.str.replace(r'\s+', ' ', regex=True).str.strip()

    return serie

def main():
    print("=== Limpieza de dataset ===\n")

    ruta_in = input("Ruta del archivo Excel a limpiar (p. ej., C:\\Users\\Tú\\dataset.xlsx):\n> ").strip()
    if not os.path.isfile(ruta_in):
        print("No se encontró el archivo especificado.")
        return

    # Nombre salida por defecto
    base, ext = os.path.splitext(ruta_in)
    ruta_out = input(f"Ruta de salida (ENTER para '{base}_cleaned.xlsx'):\n> ").strip() or f"{base}_cleaned.xlsx"

    try:
        df = pd.read_excel(ruta_in)
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return

    print(f"\nArchivo cargado: {os.path.basename(ruta_in)}")
    print(f"Forma inicial: {df.shape[0]} filas, {df.shape[1]} columnas")

    # 1) Drop columnas
    cols_presentes = [c for c in COLUMNAS_A_ELIMINAR if c in df.columns]
    if cols_presentes:
        df = df.drop(columns=cols_presentes)
        print(f"Columnas eliminadas: {', '.join(cols_presentes)}")
    else:
        print("Ninguna de las columnas objetivo estaba presente para eliminar.")

    # 2) Drop duplicados (filas idénticas)
    antes_dup = len(df)
    df = df.drop_duplicates(keep='first')
    dup_eliminados = antes_dup - len(df)
    print(f"Duplicados eliminados: {dup_eliminados}")

    # 3) Drop nulos (cualquier columna con NaN)
    antes_na = len(df)
    df = df.dropna(how='any')
    na_eliminados = antes_na - len(df)
    print(f"Filas con nulos eliminadas: {na_eliminados}")

    # 4) Limpiar review_text (guiones y saltos de línea -> espacio)
    if "review_text" in df.columns:
        df["review_text"] = limpiar_review_text(df["review_text"])
        print("'review_text' limpiado (guiones/saltos de línea → espacio, espacios colapsados).")
    else:
        print("No se encontró la columna 'review_text' para limpiar.")

    # Guardar resultado
    try:
        df.to_excel(ruta_out, index=False)
        print(f"\nLimpieza completada. Archivo guardado en:\n{ruta_out}")
        print(f"Forma final: {df.shape[0]} filas, {df.shape[1]} columnas")
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")

if __name__ == "__main__":
    main()
