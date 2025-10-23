# main.py

import pandas as pd
from src.azure_client import analyze_sentiments_and_opinions, classify_tx_dimensions
import time

# --- Configuración ---
SOURCE_FILE = "data/raw/comentarios_tripadvisor.xlsx"
OUTPUT_FILE = "data/processed/resultados_completos.csv"
COMMENT_COLUMN = "review_text"
BATCH_SIZE = 5  # Tamaño del lote para enviar a la API (máximo 5 para clasificación)

def main():
    """
    Función principal que lee los comentarios, llama a las APIs de Azure en lotes,
    y guarda los resultados en un nuevo archivo.
    """
    # 1. Cargar los datos
    print(f"Cargando datos desde {SOURCE_FILE}...")
    df = pd.read_excel(SOURCE_FILE)
    print(f"Se cargaron {len(df)} comentarios.")

    # Listas para guardar todos los resultados
    all_sentiments = []
    all_opinions = []
    all_dimensions = []

    # 2. Procesar el DataFrame en lotes
    for i in range(0, len(df), BATCH_SIZE):
        batch_df = df.iloc[i:i+BATCH_SIZE]
        comments_batch = batch_df[COMMENT_COLUMN].tolist()
        
        print(f"Procesando lote {i//BATCH_SIZE + 1} de {len(df)//BATCH_SIZE + 1}...")

        try:
            # 3. Llamar a las APIs de Azure
            sentiment_results = analyze_sentiments_and_opinions(comments_batch)
            dimension_results = classify_tx_dimensions(comments_batch)

            # 4. Añadir resultados a las listas
            for sentiment, opinion in sentiment_results:
                all_sentiments.append(sentiment)
                all_opinions.append(opinion)
            
            all_dimensions.extend(dimension_results)

        except Exception as e:
            print(f"  -> Ocurrió un error en este lote: {e}")
            # Añadir valores de error para mantener la consistencia de las filas
            all_sentiments.extend(["ERROR"] * len(comments_batch))
            all_opinions.extend(["ERROR"] * len(comments_batch))
            all_dimensions.extend(["ERROR"] * len(comments_batch))
        
        # Pausa para no exceder los límites de la API (20 llamadas por minuto para F0)
        time.sleep(3) 

    # 5. Añadir las nuevas columnas al DataFrame
    print("Añadiendo resultados al DataFrame...")
    df['Sentimiento'] = all_sentiments
    df['Aspectos'] = all_opinions
    df['Dimensiones_TX'] = all_dimensions

    # 6. Guardar el resultado final
    print(f"Guardando resultados en {OUTPUT_FILE}...")
    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print("¡Proceso completado exitosamente!")


if __name__ == "__main__":
    main()