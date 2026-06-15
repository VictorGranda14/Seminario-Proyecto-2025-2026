import pandas as pd
import csv

def fusionar_aspectos_y_dimensiones(ruta_aspectos, ruta_dimensiones, ruta_salida):
    print("1. Cargando archivo maestro de aspectos (el que acabamos de reparar)...")
    df_aspectos = pd.read_csv(ruta_aspectos)
    
    print("2. Cargando archivo de dimensiones...")
    # Pandas maneja las dobles comillas escapadas por defecto, 
    # pero nos aseguramos de que no se rompa nada en la lectura.
    df_dimensiones = pd.read_csv(ruta_dimensiones)
    
    # 3. Aislamiento de columnas útiles
    # No queremos duplicar el texto, la región ni el location. 
    # Solo necesitamos el ID (para enlazar), el rubro y la dimensión final.
    if 'ID' not in df_dimensiones.columns or 'Dimensiones' not in df_dimensiones.columns:
        print("Error: El CSV de dimensiones no tiene las columnas 'ID' o 'Dimensiones'.")
        return
        
    columnas_utiles = ['ID', 'rubro', 'Dimensiones']
    # Filtramos las columnas que existen (por si acaso no tienes 'rubro' en el archivo)
    columnas_a_cruzar = [col for col in columnas_utiles if col in df_dimensiones.columns]
    
    df_dim_filtrado = df_dimensiones[columnas_a_cruzar]
    
    # Eliminar posibles duplicados en el archivo de dimensiones para evitar que el merge multiplique filas
    df_dim_filtrado = df_dim_filtrado.drop_duplicates(subset=['ID'])

    print(f"3. Cruzando datos usando el 'ID' como llave...")
    # Un 'left join' asegura que conservamos todas las filas de aspectos,
    # y les pegamos la dimensión correspondiente según su ID.
    df_final = pd.merge(df_aspectos, df_dim_filtrado, on='ID', how='left')
    
    print(f"4. ¡Cruce exitoso! Dataset final contiene {len(df_final)} filas.")
    
    # 5. Guardado de seguridad para SQLite
    # quoting=csv.QUOTE_MINIMAL le dice a Pandas que solo use comillas envolventes 
    # cuando la celda contenga comas o corchetes, protegiendo el JSON interno.
    df_final.to_csv(ruta_salida, index=False, encoding='utf-8-sig', quoting=csv.QUOTE_MINIMAL)
    print(f"5. Archivo DEFINITIVO guardado en: {ruta_salida}")

if __name__ == "__main__":
    # RUTAS: Ajusta los nombres de tus archivos
    # 1. Tu CSV que ya tiene los aspectos limpios y rescatados
    archivo_aspectos = r"C:\Users\ramiro\Seminario-Proyecto-2025-2026\backend\data\outputs\output_llm_sin_dimensiones.csv"
    
    # 2. El CSV que tiene las dimensiones evaluadas
    archivo_dimensiones = r"C:\Users\ramiro\Seminario-Proyecto-2025-2026\backend\data\outputs\reviews_con_dimensiones_limpias.csv"
    
    # 3. El CSV maestro definitivo que irá a SQLite
    archivo_destino = r"C:\Users\ramiro\Seminario-Proyecto-2025-2026\backend\data\outputs\output_llm.csv"
    
    fusionar_aspectos_y_dimensiones(archivo_aspectos, archivo_dimensiones, archivo_destino)