# scripts/add_ids.py

import pandas as pd
import os

# --- Configuración ---
SOURCE_FILE = "data/Chile_en_limpio.xlsx"
OUTPUT_FILE = "data/Comentarios_TripAdvisor_Ingles_SinProcesar.csv"
ID_COLUMN_NAME = "ID"

# --- Proceso Principal ---
if __name__ == "__main__":
    # Asegurarnos de que la carpeta de salida exista
    output_dir = os.path.dirname(OUTPUT_FILE)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. Cargar el archivo Excel
    print(f"Cargando datos desde {SOURCE_FILE}...")
    try:
        df = pd.read_excel(SOURCE_FILE)
        print(f"Se cargaron {len(df)} comentarios.")
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en la ruta '{SOURCE_FILE}'. Verifica el nombre y la ubicación.")
        exit() # Salimos del script si no encuentra el archivo

    # 2. Generar y añadir la columna de ID
    print(f"Generando IDs únicos para cada comentario...")
    ids = [f"{i+1}" for i in range(len(df))]
    
    # Insertamos la nueva columna al principio del DataFrame para fácil visualización
    df.insert(0, ID_COLUMN_NAME, ids)

    # 3. Guardar el nuevo DataFrame en un archivo CSV
    print(f"Guardando el nuevo dataset con IDs en {OUTPUT_FILE}...")
    # Usamos punto y coma (;) como separador para que se abra bien en tu Excel
    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig', sep=';')

    print("\n--- RESUMEN ---")
    print(f"Se procesaron {len(df)} comentarios.")
    print(f"Se añadió una nueva columna de ID llamada '{ID_COLUMN_NAME}'.")
    print("¡Proceso completado!")