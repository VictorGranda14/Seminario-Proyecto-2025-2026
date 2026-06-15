import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from collections import Counter # Importamos Counter para contar las frecuencias

# ==========================================
# 1. CONFIGURACIÓN INICIAL
# ==========================================
archivo_entrada = "../data/reports/Tablero_LLM_Vina_Santa_Rita.xlsx" 
archivo_salida = "../data/reports/absa_LLM_SANTA_RITA_consolidado365.xlsx"

# Definimos las hojas exactas que queremos procesar
hojas_a_procesar = ["2. Fortalezas", "3. Alertas de Calidad"]

print("Cargando modelo de embeddings (esto puede tardar unos segundos la primera vez)...")
modelo_embedding = SentenceTransformer('all-MiniLM-L6-v2') 

# ==========================================
# 2. PROCESAMIENTO POR HOJA
# ==========================================
# Leemos el Excel especificando las hojas. Esto devuelve un diccionario de DataFrames
excel_data = pd.read_excel(archivo_entrada, sheet_name=hojas_a_procesar)

# Usamos ExcelWriter para poder guardar múltiples hojas en el archivo de salida
with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
    
    for nombre_hoja, df in excel_data.items():
        print(f"\n--- Procesando hoja: {nombre_hoja} ---")
        
        # Identificar dinámicamente el nombre de la columna de aspectos 
        # (ya que puede ser "Aspecto (Fortaleza)" o "Aspecto (Alerta)")
        col_aspecto = [col for col in df.columns if 'Aspecto' in str(col)][0]
        col_frecuencia = 'Frecuencia'
        col_opiniones = 'Adjetivos Clave'
        
        # Limpiamos filas vacías por seguridad
        df = df.dropna(subset=[col_aspecto]).copy()
        
        # 3. GENERAR EMBEDDINGS
        aspectos = df[col_aspecto].tolist()
        embeddings = modelo_embedding.encode(aspectos)
        
        # 4. CLUSTERING
        clustering_model = AgglomerativeClustering(
            n_clusters=None, 
            distance_threshold=0.365, # Ajusta este valor si necesitas fusionar más o menos
            metric='cosine', 
            linkage='average'
        )
        df['Cluster_ID'] = clustering_model.fit_predict(embeddings)
        
        # 5. FUSIÓN DE DATOS
        filas_consolidadas = []
        
        for cluster_id, grupo in df.groupby('Cluster_ID'):
            aspectos_grupo = grupo[col_aspecto].tolist()
            
            # Sumar la frecuencia total del clúster
            frecuencia_total = grupo[col_frecuencia].sum()
            
            # NUEVO: Elegir como etiqueta el aspecto que tenga la frecuencia MÁXIMA dentro de este grupo
            indice_max_frecuencia = grupo[col_frecuencia].idxmax()
            etiqueta_dominante = grupo.loc[indice_max_frecuencia, col_aspecto]
            
            # --- Lógica Modificada de Opiniones Clave (Contar y Ordenar) ---
            opiniones_mezcladas = []
            for op_string in grupo[col_opiniones].dropna():
                # Separar por comas, limpiar espacios y omitir vacíos
                adjetivos = [adj.strip() for adj in str(op_string).split(',') if adj.strip()]
                opiniones_mezcladas.extend(adjetivos)
            
            # Usar Counter para contar cuántas veces aparece cada adjetivo
            conteo_opiniones = Counter(opiniones_mezcladas)
            
            # most_common() devuelve una lista de tuplas ordenadas de mayor a menor: [('good', 5), ('bad', 2), ...]
            # Extraemos solo las palabras (elemento 0 de la tupla) ya ordenadas
            opiniones_ordenadas = [palabra for palabra, cuenta in conteo_opiniones.most_common()]
            
            opiniones_finales_str = ", ".join(opiniones_ordenadas)
            # -------------------------------------------------------------
            
            filas_consolidadas.append({
                'Aspecto Consolidado': etiqueta_dominante,
                'Aspectos Originales (Fusionados)': " | ".join(aspectos_grupo),
                'Frecuencia Total': frecuencia_total,
                'Opiniones Clave Consolidadas': opiniones_finales_str
            })
            
        # Crear DataFrame final para esta hoja
        df_final = pd.DataFrame(filas_consolidadas)
        df_final = df_final.sort_values(by='Frecuencia Total', ascending=False)
        
        # Guardar en el Excel de salida bajo la misma pestaña
        df_final.to_excel(writer, sheet_name=nombre_hoja, index=False)
        print(f"Hoja '{nombre_hoja}' consolidada con éxito: se redujeron de {len(df)} a {len(df_final)} aspectos.")

print(f"\n¡Proceso terminado! Archivo completo guardado en: {archivo_salida}")