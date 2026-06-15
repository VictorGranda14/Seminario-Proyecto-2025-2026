import pandas as pd
import csv

def filtrar_atracciones_minimas(ruta_entrada, ruta_salida, minimo_comentarios=10):
    print(f"1. Cargando dataset maestro: {ruta_entrada}")
    df = pd.read_csv(ruta_entrada)
    
    filas_originales = len(df)
    atracciones_originales = df['attraction_name'].nunique()
    print(f"   -> Filas totales actuales: {filas_originales}")
    print(f"   -> Atracciones únicas actuales: {atracciones_originales}")

    # 2. Matemáticas de agrupación: Contar IDs únicos por atracción
    # Usamos nunique() para no contar el mismo comentario varias veces
    conteo_por_atraccion = df.groupby('attraction_name')['ID'].nunique()
    
    # 3. Filtrar la lista de atracciones válidas
    atracciones_validas = conteo_por_atraccion[conteo_por_atraccion >= minimo_comentarios].index
    
    # 4. Aplicar la máscara al DataFrame original
    df_filtrado = df[df['attraction_name'].isin(atracciones_validas)]
    
    filas_finales = len(df_filtrado)
    atracciones_finales = df_filtrado['attraction_name'].nunique()
    
    print("\n2. Resultados del filtro:")
    print(f"   -> Se eliminaron {atracciones_originales - atracciones_finales} atracciones irrelevantes.")
    print(f"   -> Se descartaron {filas_originales - filas_finales} filas en total.")
    print(f"   -> Atracciones que sobrevivieron: {atracciones_finales}")

    # 5. Guardar el archivo listo y esterilizado
    df_filtrado.to_csv(ruta_salida, index=False, encoding='utf-8-sig', quoting=csv.QUOTE_MINIMAL)
    print(f"\n3. Archivo filtrado y final guardado en: {ruta_salida}")

if __name__ == "__main__":
    # Ajusta con tu ruta del archivo definitivo fusionado
    archivo_entrada = r"C:\Users\ramiro\Seminario-Proyecto-2025-2026\backend\data\outputs\output_llm.csv"
    
    # Puedes sobreescribirlo o crear uno nuevo con "_FILTRADO"
    archivo_salida = r"C:\Users\ramiro\Seminario-Proyecto-2025-2026\backend\data\outputs\output_llm_filtrado.csv"
    
    filtrar_atracciones_minimas(archivo_entrada, archivo_salida)