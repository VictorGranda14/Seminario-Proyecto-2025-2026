import pandas as pd
from src.azure_client import analyze_sentiments_and_opinions, classify_tx_dimensions
from src.data_processing import load_data, filter_by_attraction

# --- CONFIGURACIÓN DEL ANÁLISIS ---
SOURCE_FILE = "data/processed/Comentarios_en_Final.xlsx"
OUTPUT_FILE = "data/processed/Analisis_Atraccion_Especifica.xlsx"
ATTRACTION_TO_ANALYZE = "Sousas Tour"  
COMMENT_COLUMN = "review_text"
ID_COLUMN = "Comment_ID"
BATCH_SIZE = 5 

def main():
    """
    Orquesta el análisis completo para una única atracción turística.
    """
    # 1. Cargar los datos limpios
    print(f"Cargando datos desde {SOURCE_FILE}...")
    df_full = load_data(SOURCE_FILE)
    if df_full is None:
        return
    
    # 2. Filtrar para la atracción específica
    df_attraction = filter_by_attraction(df_full, ATTRACTION_TO_ANALYZE)

    if df_attraction.empty:
        print(f"No se encontraron comentarios para la atracción '{ATTRACTION_TO_ANALYZE}'.")
        return
    
    print(f"Se encontraron {len(df_attraction)} comentarios para analizar.")

    # 3. Preparar los datos para las APIs
    comments_list = df_attraction[COMMENT_COLUMN].tolist()
    ids_list = df_attraction[ID_COLUMN].tolist()
    
    # Listas para guardar los resultados
    sentiment_results = []
    dimension_results = []

    # 4. Procesar en lotes y llamar a las APIs
    print("Iniciando procesamiento en lotes con las APIs de Azure...")
    for i in range(0, len(comments_list), BATCH_SIZE):
        batch = comments_list[i:i+BATCH_SIZE]
        
        print(f"  Procesando lote {i//BATCH_SIZE + 1}...")
        
        # Llamada a la API de Sentimiento
        sentiments = analyze_sentiments_and_opinions(batch)
        sentiment_results.extend(sentiments)
        
        # Llamada a la API de Clasificación de Dimensiones
        dimensions = classify_tx_dimensions(batch)
        dimension_results.extend(dimensions)

    # 5. Combinar todo en un nuevo DataFrame
    print("Combinando los resultados del análisis...")
    
    final_data = []
    for i in range(len(comments_list)):
        final_data.append({
            'Comment_ID': ids_list[i],
            'review_text': comments_list[i],
            'Sentimiento': sentiment_results[i][0], # El primer elemento de la tupla es el sentimiento
            'Aspectos_Minados': sentiment_results[i][1], # El segundo son los aspectos
            'Dimensiones_TX': dimension_results[i]
        })
        
    results_df = pd.DataFrame(final_data)

    # 6. Guardar el archivo de resultados
    print(f"Guardando el análisis para '{ATTRACTION_TO_ANALYZE}' en {OUTPUT_FILE}...")
    results_df.to_excel(OUTPUT_FILE, index=False)
    
    print("\nAnálisis para la atracción completado")
    print("\nPrimeras 5 filas del resultado:")
    print(results_df.head())


if __name__ == "__main__":
    main()