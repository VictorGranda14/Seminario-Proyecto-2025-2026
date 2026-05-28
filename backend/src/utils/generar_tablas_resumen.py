import pandas as pd
import sqlite3
import os
from collections import Counter

# --- CONFIGURACION ---
ATRACCIONES_OBJETIVO = ["Vina Santa Rita"]

def extraer_opiniones_ordenadas(serie_opiniones):
    """
    Filtra ruido, cuenta frecuencias y devuelve TODAS las opiniones 
    ordenadas matemáticamente por peso real, sin truncar datos.
    """
    # 1. Descartar valores vacíos y menciones generales
    opiniones_validas = [
        str(op).strip().lower() for op in serie_opiniones 
        if str(op).strip().lower() not in ["", "mencion general", "mención general"]
    ]
    
    if not opiniones_validas:
        return ""
        
    # 2. Conteo estadístico
    conteo = Counter(opiniones_validas)
    
    # 3. Extraer TODAS las opiniones (most_common sin parámetros las devuelve todas ordenadas)
    todas_opiniones = [f"{palabra} ({frecuencia})" for palabra, frecuencia in conteo.most_common()]
    
    return ", ".join(todas_opiniones)

def agregar_aspectos(df, polaridad):
    """
    Filtra por polaridad, agrupa por aspecto, cuenta la frecuencia 
    y extrae el top 5 de opiniones clave unicas.
    """
    # Nuevo enfoque estricto:
    if polaridad == 'positive':
        df_filtrado = df[df['sentiment'] == 'positive'].copy()
    else:
        # Para negativos, atrapamos todo lo que NO sea positivo (incluyendo mixed/neutral)
        df_filtrado = df[df['sentiment'] != 'positive'].copy()
    
    if df_filtrado.empty:
        return pd.DataFrame()

    # Agrupacion estadistica aplicando la nueva funcion del Top 5
    resumen = df_filtrado.groupby('aspect').agg(
        Frecuencia=('aspect', 'count'),
        Opiniones_Clave=('opinion', extraer_opiniones_ordenadas) # Esta función ahora devuelve TODAS las opiniones ordenadas por frecuencia
    ).reset_index()
    
    # Renombrar columna
    tipo_aspecto = "Fortaleza" if polaridad == "positive" else "Debilidad"
    resumen.rename(columns={'aspect': f'Aspecto ({tipo_aspecto})'}, inplace=True)
    
    # Ordenar de mayor a menor frecuencia
    resumen = resumen.sort_values(by='Frecuencia', ascending=False)
    
    return resumen

def main():
    print("Iniciando generacion de tablas de resumen estadistico...")
    
    ruta_db = "data/outputs/resultados_nlp.db"
    ruta_salida = "data/outputs/Tablas_Resumen_Tesis.xlsx"
    
    if not os.path.exists(ruta_db):
        print("Error: No se encontro la base de datos local.")
        return
        
    conexion = sqlite3.connect(ruta_db)
    
    # Usamos Pandas ExcelWriter para guardar multiples hojas en un solo archivo
    try:
        with pd.ExcelWriter(ruta_salida, engine='openpyxl') as writer:
            
            for atraccion in ATRACCIONES_OBJETIVO:
                print(f"Procesando: {atraccion}")
                
                # Extraemos solo los datos de esta atraccion
                df = pd.read_sql_query(
                    "SELECT aspect, opinion, sentiment FROM aspect_results WHERE attraction = ?", 
                    conexion, 
                    params=(atraccion,)
                )
                
                if df.empty:
                    print(f"Advertencia: No hay datos minados para '{atraccion}' en la base de datos.")
                    continue
                
                # Generar tablas
                df_positivos = agregar_aspectos(df, 'positive')
                df_negativos = agregar_aspectos(df, 'negative')
                
                # Guardar en el Excel en pestanas separadas
                nombre_hoja_pos = f"{atraccion[:25]}_Pos" # Excel limita nombres de hoja a 31 chars
                nombre_hoja_neg = f"{atraccion[:25]}_Neg"
                
                if not df_positivos.empty:
                    df_positivos.to_excel(writer, sheet_name=nombre_hoja_pos, index=False)
                if not df_negativos.empty:
                    df_negativos.to_excel(writer, sheet_name=nombre_hoja_neg, index=False)
                    
        print(f"\nTablas generadas con exito. Archivo guardado en: {ruta_salida}")
        
    except Exception as e:
        print(f"Error al generar el archivo Excel: {e}")
    finally:
        conexion.close()

if __name__ == "__main__":
    main()