import pandas as pd
from src.models.aspect_miner import AspectMinerLocal
import sqlite3
import os

# Lista Atracciones
ATRACCIONES = ["Vina Santa Rita"]

def main():
    print("Iniciando Orquestador Principal...")
    
    # 1. Cargar datos limpios
    data_path = "data/processed/Comentarios_en_Final.csv"
    try:
        df = pd.read_csv(data_path, sep=';') 
    except FileNotFoundError:
        print(f"No se encontró el dataset en {data_path}.")
        return

    # Bloque de compatibilidad de ID
    if 'Comment_ID' not in df.columns:
        if 'ID' in df.columns:
            df.rename(columns={'ID': 'Comment_ID'}, inplace=True)
        else:
            df.insert(0, 'Comment_ID', [f"REV-{i+1}" for i in range(len(df))])

    miner = AspectMinerLocal()
    os.makedirs("data/outputs", exist_ok=True)
    conn = sqlite3.connect("data/outputs/resultados_nlp.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aspect_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            c_id TEXT,
            attraction TEXT,
            aspect TEXT,
            opinion TEXT,
            sentiment TEXT
        )
    ''')
    conn.commit()

    # Leemos lo que ya está en la base de datos para no repetir
    procesados = pd.read_sql_query("SELECT DISTINCT c_id FROM aspect_results", conn)['c_id'].tolist()

    # 2. Iterar sobre las atracciones seleccionadas
    for atraccion in ATRACCIONES:
        df_atraccion = df[df['attraction_name'] == atraccion].copy()
        
        if df_atraccion.empty:
            print(f"No se encontraron comentarios para '{atraccion}'. Revisa el nombre exacto.")
            continue
            
        df_a_procesar = df_atraccion[~df_atraccion['Comment_ID'].isin(procesados)]
        total = len(df_a_procesar)
        
        print(f"\nProcesando '{atraccion}': {total} comentarios nuevos (saltando {len(df_atraccion) - total} ya procesados).")
        
        contador = 0
        for index, row in df_a_procesar.iterrows():
            comentario_id = row['Comment_ID']
            texto = str(row['review_text'])
            
            resultados = miner.extract_aspects(texto)
            
            for res in resultados:
                cursor.execute('''
                    INSERT INTO aspect_results (c_id, attraction, aspect, opinion, sentiment)
                    VALUES (?, ?, ?, ?, ?)
                ''', (comentario_id, atraccion, res['aspect'], res['opinion'], res['sentiment']))
            
            conn.commit()
            contador += 1
            
            # Imprimir progreso cada 50 comentarios para saber que no está congelado
            if contador % 50 == 0 or contador == total:
                print(f"Progreso {atraccion}: {contador}/{total} comentarios procesados...")

    conn.close()
    print("\nProceso Masivo Finalizado.")

if __name__ == "__main__":
    main()