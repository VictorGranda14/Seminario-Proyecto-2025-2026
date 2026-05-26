# scripts/select_random_sample.py

import pandas as pd
# --- Configuración ---
SOURCE_FILE = "data/processed/Comentarios_en_Final.xlsx"
OUTPUT_FILE = "data/comentarios_doccano.txt"
COMMENT_COLUMN = "review_text"
SAMPLE_SIZE = 2000

def select_and_save_random_sample():
    
    print(f"Cargando datos desde {SOURCE_FILE}...")
    try:
        df = pd.read_excel(SOURCE_FILE)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en la ruta '{SOURCE_FILE}'. Verifica el nombre y la ubicación.")
        return

    print(f"Seleccionando una muestra aleatoria de {SAMPLE_SIZE} comentarios...")
    
    # Esta es la línea clave: toma una muestra aleatoria del DataFrame
    # random_state=42 asegura que siempre obtengas la MISMA muestra aleatoria,
    # lo cual es bueno para la reproducibilidad de tu experimento.
    random_sample_df = df.sample(n=SAMPLE_SIZE, random_state=42)

    print(f"Guardando la muestra en {OUTPUT_FILE}...")
    
    # Extrae solo la columna de comentarios de la muestra
    comments_to_save = random_sample_df[COMMENT_COLUMN]

    # Guarda los comentarios en un archivo .txt, un comentario por línea
    comments_to_save.to_csv(OUTPUT_FILE, index=False, header=False, encoding='utf-8')

    print("¡Proceso completado! Tu archivo está listo para ser importado en Doccano. ✅")

if __name__ == "__main__":
    select_and_save_random_sample()