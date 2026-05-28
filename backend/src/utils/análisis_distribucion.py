import pandas as pd
import os

# --- Configuración ---
SOURCE_FILE = "data/processed/Comentarios_en_FINAL.xlsx"
OUTPUT_FILE = "data/processed/distribucion_comentarios.txt"
ATTRACTION_COLUMN = "attraction_name"

def analyze_and_export_distribution():
    """
    Carga el dataset, analiza la distribución de comentarios por atracción
    y exporta el informe a un archivo TXT.
    """
    # 1. Cargar los datos
    print(f"Cargando datos desde {SOURCE_FILE}...")
    try:
        df = pd.read_excel(SOURCE_FILE)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en la ruta '{SOURCE_FILE}'.")
        return

    # 2. Contar comentarios y calcular promedio
    print("Contando comentarios y calculando el promedio...")
    comment_counts = df.groupby(ATTRACTION_COLUMN).size()
    average_comments = comment_counts.mean()

    # 3. Escribir el informe en el archivo de texto
    print(f"Guardando el informe en {OUTPUT_FILE}...")
    try:
        # Usamos 'with open' para manejar el archivo de forma segura
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write("--- ANÁLISIS DE DISTRIBUCIÓN DE COMENTARIOS ---\n\n")
            f.write("Número de comentarios por atracción (ordenado de mayor a menor):\n")
            
            # .to_string() convierte la tabla de pandas a un formato de texto perfecto para el TXT
            f.write(comment_counts.sort_values(ascending=False).to_string())
            
            f.write("\n\n--------------------------------------------------\n\n")
            f.write("--- Resumen Estadístico ---\n\n")
            f.write(f"Número total de atracciones únicas: {len(comment_counts)}\n")
            f.write(f"Promedio de comentarios por atracción: {average_comments:.2f}\n")

        print("\n¡Informe exportado exitosamente! ✅")
    except Exception as e:
        print(f"Ocurrió un error al guardar el archivo: {e}")

if __name__ == "__main__":
    analyze_and_export_distribution()