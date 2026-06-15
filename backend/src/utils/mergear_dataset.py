import pandas as pd
import re

def rescatar_formato_original(texto_roto):
    """
    Usa Regex para extraer datos rotos y los devuelve 
    empaquetados como un string de lista de diccionarios.
    """
    if pd.isna(texto_roto) or not isinstance(texto_roto, str):
        return "Neutral", "[]"

    # 1. Rescatar el general_sentiment
    match_sentiment = re.search(r'"general_sentiment"\s*:\s*"([^"]+)"', texto_roto)
    general_sentiment = match_sentiment.group(1) if match_sentiment else "Neutral"

    # 2. Rescatar los aspectos uno por uno
    patron_aspectos = r'\{\s*"aspect"\s*:\s*"([^"]+)"\s*,\s*"sentiment"\s*:\s*"([^"]+)"\s*,\s*"adjective"\s*:\s*"([^"]*)"\s*\}'
    
    aspectos_encontrados = []
    aspectos_unicos = set()

    matches = re.finditer(patron_aspectos, texto_roto)
    for match in matches:
        aspecto = match.group(1).strip()
        sentimiento = match.group(2).strip()
        adjetivo = match.group(3).strip()

        clave_unica = f"{aspecto}_{sentimiento}"
        if clave_unica not in aspectos_unicos:
            aspectos_unicos.add(clave_unica)
            aspectos_encontrados.append({
                "aspect": aspecto,
                "sentiment": sentimiento,
                "adjective": adjetivo
            })

    # Convertir la lista de diccionarios a un string exacto al original
    # Python usa comillas simples por defecto al hacer str() de un dict
    aspectos_str = str(aspectos_encontrados)
    return general_sentiment, aspectos_str

def reparar_y_fusionar_csv(ruta_base, ruta_salida):
    print(f"1. Cargando archivo maestro: {ruta_base}")
    df_base = pd.read_csv(ruta_base, engine='python', on_bad_lines='skip')
    
    # Validar si existen las columnas de error
    if 'error' not in df_base.columns:
        print("El archivo no tiene columna 'error'. No hay nada que separar.")
        return

    # 2. Separar las filas que nacieron bien de las que tienen error
    df_buenos = df_base[df_base['error'].isna()].copy()
    df_malos = df_base[df_base['error'].notna()].copy()
    
    print(f"   -> Filas buenas originales: {len(df_buenos)}")
    print(f"   -> Filas corruptas a reparar: {len(df_malos)}")

    # 3. Reparar y empaquetar las filas malas
    nuevas_filas_reparadas = []
    
    for index, fila in df_malos.iterrows():
        texto_a_procesar = fila.get('raw', '')
        if pd.isna(texto_a_procesar):
            texto_a_procesar = fila.get('aspects', '')
            
        gen_sent, aspectos_str = rescatar_formato_original(texto_a_procesar)
        
        # Solo conservamos la fila si logramos rescatar al menos un aspecto
        if aspectos_str != "[]":
            fila_reparada = fila.copy()
            fila_reparada['general_sentiment'] = gen_sent
            fila_reparada['aspects'] = aspectos_str
            nuevas_filas_reparadas.append(fila_reparada)

    df_malos_reparados = pd.DataFrame(nuevas_filas_reparadas)
    print(f"   -> Se logró reconstruir el formato original de {len(df_malos_reparados)} comentarios.")

    # 4. Fusionar (Concatenar) los buenos con los reparados
    df_final = pd.concat([df_buenos, df_malos_reparados], ignore_index=True)
    
    # 5. Limpieza definitiva (Borrar columnas residuales)
    columnas_a_borrar = ['error', 'raw']
    for col in columnas_a_borrar:
        if col in df_final.columns:
            df_final = df_final.drop(columns=[col])

    print(f"\n4. Dataset consolidado y estandarizado: {len(df_final)} filas totales.")

    # 6. Guardar archivo final
    df_final.to_csv(ruta_salida, index=False, encoding='utf-8-sig')
    print(f"5. Archivo guardado en: {ruta_salida}")

if __name__ == "__main__":
    # Toma tu archivo original directamente
    archivo_origen = r"C:\Users\ramiro\Seminario-Proyecto-2025-2026\backend\data\outputs\output_llm_sin_limpiar.csv" 
    
    # El archivo de salida quedará listo para tu base de datos
    archivo_destino = r"C:\Users\ramiro\Seminario-Proyecto-2025-2026\backend\data\outputs\output_llm_final.csv"
    
    reparar_y_fusionar_csv(archivo_origen, archivo_destino)