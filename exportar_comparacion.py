import pandas as pd
import sqlite3
import os

def calcular_sentimiento_general(polaridades):
    """
    Infiere el sentimiento general del comentario basado en la mayoría de sus aspectos.
    """
    conteos = polaridades.value_counts()
    
    if len(conteos) == 0:
        return "neutral"
    
    if len(conteos) > 1:
        # Si hay positivos y negativos al mismo tiempo
        if 'positive' in conteos and 'negative' in conteos:
            if conteos['positive'] == conteos['negative']:
                return "mixed"
    
    # Devuelve el sentimiento que más se repite
    return conteos.idxmax()

def main():
    print("📊 Generando reporte con formato Azure para comparación...")
    
    ruta_db = "data/outputs/resultados_nlp.db"
    ruta_csv_limpio = "data/processed/Dataset_Limpio_Final.csv"
    ruta_salida = "data/outputs/Comparacion_Modelos.xlsx"
    
    if not os.path.exists(ruta_db):
        print("❌ No se encontró la base de datos de resultados.")
        return
        
    # 1. Extraer datos de SQLite
    conexion = sqlite3.connect(ruta_db)
    df_db = pd.read_sql_query("SELECT * FROM aspect_results", conexion)
    conexion.close()
    
    if len(df_db) == 0:
        print("⚠️ La base de datos está vacía.")
        return

    # 2. Reconstruir el formato de Azure agrupando por Comment_ID
    # Creamos la cadena: aspecto(opinion|sentimiento)
    df_db['formato_azure'] = df_db.apply(
        lambda row: f"{row['aspect']}({row['opinion']}|{row['sentiment']})", axis=1
    )
    
    # Agrupamos todos los aspectos que pertenecen al mismo comentario
    df_agrupado = df_db.groupby('c_id').agg({
        'formato_azure': lambda x: ', '.join(x),
        'sentiment': calcular_sentimiento_general,
        'attraction': 'first' # Mantenemos el nombre de la atracción
    }).reset_index()
    
    df_agrupado.rename(columns={
        'formato_azure': 'Local_Aspects_Output',
        'sentiment': 'Local_General_Sentiment',
        'c_id': 'Comment_ID'
    }, inplace=True)
    
    # 3. Cruzar con el texto original del dataset
    try:
        df_original = pd.read_csv(ruta_csv_limpio, sep=';', usecols=['Comment_ID', 'review_text', 'rating_review'])
        
        # Hacemos un Left Join para pegar el texto original al lado de nuestras extracciones
        df_final = pd.merge(df_agrupado, df_original, on='Comment_ID', how='left')
        
        # Ordenar columnas para que sea fácil de leer
        columnas_ordenadas = ['Comment_ID', 'attraction', 'rating_review', 'review_text', 'Local_General_Sentiment', 'Local_Aspects_Output']
        df_final = df_final[columnas_ordenadas]
        
    except Exception as e:
        print(f"⚠️ No se pudo cruzar con el dataset original ({e}). Se exportarán solo los resultados crudos.")
        df_final = df_agrupado

    # 4. Exportar a Excel
    df_final.to_excel(ruta_salida, index=False)
    print(f"✅ ¡Reporte generado con éxito! Guardado en: {ruta_salida}")

if __name__ == "__main__":
    main()