import pandas as pd
import sqlite3
import ast
from src.config.database_init import initialize_database

def poblar_sqlite_desde_csv(ruta_csv: str, ruta_db: str):
    print(f"1. Leyendo dataset maestro: {ruta_csv}")
    df = pd.read_csv(ruta_csv)
    
    # 2. Conectar e Inicializar DB
    conexion = sqlite3.connect(ruta_db)
    initialize_database(conexion)
    cursor = conexion.cursor()
    
    # IMPORTANTE: Vaciamos la tabla de análisis crudo antes de inyectar 
    # para evitar duplicar millones de filas si corres el script 2 veces.
    print("2. Purgando tabla 'analisis_crudo' antigua para inyección limpia...")
    cursor.execute("DELETE FROM analisis_crudo")
    
    filas_a_insertar = []
    
    print("3. Adaptando datos y desempaquetando aspectos...")
    # 3. Iterar y Adaptar los datos
    for _, row in df.iterrows():
        
        # A) Leer el JSON con comillas simples de forma segura, evadiendo los NaN
        aspectos_raw = row.get('aspects')
        if pd.isna(aspectos_raw):
            aspectos = []
        else:
            try:
                aspectos = ast.literal_eval(str(aspectos_raw))
            except Exception as e:
                aspectos = []
            
        # B) Inyectar array vacío si no tienes dimensiones en el CSV (usando 'Dimensiones' exacto)
        dimensiones_raw = row.get('Dimensiones')
        dimensiones_str = '[]' if pd.isna(dimensiones_raw) else str(dimensiones_raw)
        
        # C) Mapear tus columnas a lo que espera SQLite
        id_com = row.get('ID', 'N/A')
        atraccion = row.get('attraction_name', 'Desconocido')
        texto = row.get('review_text', '')
        polaridad = str(row.get('general_sentiment', 'neutral')).lower()
        
        # D) Inyectar datos clave
        rubro = row.get('rubro', 'Turismo General')
        modelo = 'qwen2.5-3b' # Modificado para reflejar tu motor local real
        
        for aspecto_obj in aspectos:
            filas_a_insertar.append((
                str(id_com),
                str(atraccion),
                str(rubro),
                str(texto),
                modelo,
                polaridad,
                aspecto_obj.get('aspect', ''),
                aspecto_obj.get('adjective', ''), 
                aspecto_obj.get('sentiment', ''),
                dimensiones_str
            ))
            
    # 4. Inserción Masiva
    print(f"4. Inyectando {len(filas_a_insertar)} registros estructurados en SQLite...")
    cursor.executemany("""
        INSERT INTO analisis_crudo (
            id_comentario, atraccion, rubro, texto_original, modelo_usado, 
            polaridad_general_comentario, aspecto_detectado, opinion_detectada, 
            polaridad_aspecto, dimension_tx
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, filas_a_insertar)
    
    conexion.commit()
    conexion.close()
    print("¡Base de datos poblada exitosamente! Lista para conectar al backend de Next.js.")

if __name__ == "__main__":
    # Ajusta con tu ruta del archivo definitivo fusionado
    archivo_maestro = r"C:\Users\ramiro\Seminario-Proyecto-2025-2026\backend\data\outputs\output_llm.csv"
    base_de_datos = r"C:\Users\ramiro\Seminario-Proyecto-2025-2026\backend\data\turismo.sqlite"
    
    poblar_sqlite_desde_csv(archivo_maestro, base_de_datos)