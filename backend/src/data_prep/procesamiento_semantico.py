import sqlite3
import pandas as pd
import json
import requests
import argparse
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import MiniBatchKMeans
from collections import Counter

# Configuración optimizada
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"

CATEGORIAS_OFICIALES = [
    "Local Culture and History", "Variety of Activities", "Hospitality", 
    "Infrastructure", "Environment Management", "Accessibility", 
    "Quality of Service", "Physiography", "Price", "Visitor Management", 
    "Weather", "Food", "Safety"
]

def inicializar_cache(cursor):
    """Crea una tabla para guardar la memoria del LLM y no procesar dos veces lo mismo."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diccionario_categorias (
            aspecto_consolidado TEXT PRIMARY KEY,
            categoria_oficial TEXT
        )
    """)

def limpiar_respuesta_json(texto_crudo):
    """Destruye el formato Markdown que los modelos pequeños suelen escupir por error."""
    texto = texto_crudo.strip()
    if texto.startswith("```json"):
        texto = texto[7:]
    elif texto.startswith("```"):
        texto = texto[3:]
    if texto.endswith("```"):
        texto = texto[:-3]
    return texto.strip()

def clasificar_con_ollama(aspecto, contexto):
    system_prompt = f"""You are an expert tourism researcher. Classify the "Destination Attribute" into exactly ONE of the Official Categories.

OFFICIAL CATEGORIES:
- Local Culture and History
- Variety of Activities
- Hospitality
- Infrastructure
- Environment Management
- Accessibility
- Quality of Service
- Physiography
- Price
- Visitor Management
- Weather
- Food
- Safety

RULES:
1. Pick EXACTLY ONE category from the list.
2. Return ONLY a valid JSON object. No explanations outside the JSON.
3. Format: {{"reasoning": "step-by-step analysis", "category": "Exact Category Name"}}
"""
    user_prompt = f'Aspect: "{aspecto}"\nReview context: "{contexto}"\n\nClassify this aspect:'
    
    payload = {
        "model": MODEL_NAME,
        "prompt": f"{system_prompt}\n\n{user_prompt}",
        "format": "json",
        "stream": False,
        "options": {"temperature": 0.1}
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        
        json_limpio = limpiar_respuesta_json(data.get("response", "{}"))
        resultado = json.loads(json_limpio)
        
        categoria_obtenida = str(resultado.get("category", "")).strip()
        
        for cat_oficial in CATEGORIAS_OFICIALES:
            if cat_oficial.lower() == categoria_obtenida.lower():
                return cat_oficial
                
        return "Sin clasificar"
    except Exception as e:
        print(f"Error parseando JSON de '{aspecto}': {e}")
        return "Sin clasificar"

def procesar_base_de_datos(ruta_db: str, attraction: str = None):
    conexion = sqlite3.connect(ruta_db)
    cursor = conexion.cursor()
    
    inicializar_cache(cursor)
    
    print(f"1. Extrayendo aspectos crudos{' para ' + attraction if attraction else ' (TODA LA BASE)'}...")
    
    query = """
        SELECT aspecto_detectado, opinion_detectada 
        FROM analisis_crudo 
        WHERE aspecto_detectado IS NOT NULL AND aspecto_detectado != ''
    """
    params = []
    
    if attraction:
        query += " AND atraccion = ?"
        params.append(attraction)
        
    df_crudo = pd.read_sql_query(query, conexion, params=params)

    if df_crudo.empty:
        print("No hay datos para procesar con esos filtros.")
        return

    # ==========================================
    # FASE 1: AGRUPACIÓN SEMÁNTICA
    # ==========================================
    print("2. Cargando modelo de Embeddings...")
    modelo_embedding = SentenceTransformer('all-MiniLM-L6-v2')
    
    agrupado = df_crudo.groupby('aspecto_detectado', dropna=False).agg(
        frecuencia=('aspecto_detectado', 'count'),
        opiniones=('opinion_detectada', lambda x: [str(op) for op in x if pd.notna(op)])
    ).reset_index()

    print(f"3. Clustering Semántico ({len(agrupado)} aspectos) usando MiniBatchKMeans...")
    embeddings = modelo_embedding.encode(agrupado['aspecto_detectado'].tolist())
    
    # TRUCO MATEMÁTICO: Normalizar los vectores
    embeddings_norm = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    
    # Cálculo dinámico de 'K'
    n_clusters = max(2, len(agrupado) // 15)
    print(f"   -> Formando {n_clusters} clusters semánticos...")
    
    cluster_model = MiniBatchKMeans(n_clusters=n_clusters, batch_size=1024, random_state=42, n_init="auto")
    agrupado['Cluster_ID'] = cluster_model.fit_predict(embeddings_norm)

    # RECONSTRUCCIÓN DEL BUCLE (Recuperado)
    aspectos_consolidados = {}
    for cluster_id, grupo in agrupado.groupby('Cluster_ID'):
        etiqueta_dominante = grupo.loc[grupo['frecuencia'].idxmax(), 'aspecto_detectado']
        
        opiniones_mezcladas = []
        for lista_ops in grupo['opiniones']:
            for op_string in lista_ops:
                adjetivos = [adj.strip() for adj in str(op_string).split(',') if adj.strip()]
                opiniones_mezcladas.extend(adjetivos)
        
        top_5_opiniones = ", ".join([op for op, _ in Counter(opiniones_mezcladas).most_common(5)])
        
        for _, fila in grupo.iterrows():
            aspectos_consolidados[fila['aspecto_detectado']] = {
                'consolidado': etiqueta_dominante,
                'contexto': top_5_opiniones
            }

    # ==========================================
    # FASE 2: LLM + SISTEMA DE CACHÉ
    # ==========================================
    unicos_consolidados = {datos['consolidado']: datos['contexto'] for datos in aspectos_consolidados.values()}
    
    cache_df = pd.read_sql_query("SELECT aspecto_consolidado, categoria_oficial FROM diccionario_categorias", conexion)
    diccionario_memoria = dict(zip(cache_df['aspecto_consolidado'], cache_df['categoria_oficial']))
    
    mapeo_categorias = {}
    total_a_procesar = len(unicos_consolidados)
    procesados_nuevos = 0
    
    print(f"4. Clasificando {total_a_procesar} aspectos macro con Ollama...")
    
    for i, (aspecto, contexto) in enumerate(unicos_consolidados.items(), 1):
        if aspecto in diccionario_memoria and diccionario_memoria[aspecto] != "Sin clasificar":
            mapeo_categorias[aspecto] = diccionario_memoria[aspecto]
            continue
            
        print(f"   [{i}/{total_a_procesar}] LLM Inferencia: {aspecto}...")
        categoria = clasificar_con_ollama(aspecto, contexto)
        mapeo_categorias[aspecto] = categoria
        procesados_nuevos += 1
        
        cursor.execute("""
            INSERT OR REPLACE INTO diccionario_categorias (aspecto_consolidado, categoria_oficial)
            VALUES (?, ?)
        """, (aspecto, categoria))
        conexion.commit()

    print(f"-> Se llamaron a Ollama {procesados_nuevos} veces. ({total_a_procesar - procesados_nuevos} ahorrados por caché).")

    # ==========================================
    # FASE 3: EXPORTACIÓN DE RESCATE (CSV)
    # ==========================================
    print("5. Exportando resultados a CSV...")
    
    filas_mapeo = []
    for aspecto_crudo, datos in aspectos_consolidados.items():
        aspecto_limpio = datos['consolidado']
        categoria_macro = mapeo_categorias.get(aspecto_limpio, "Sin clasificar")
        
        filas_mapeo.append({
            "aspecto_detectado": aspecto_crudo,
            "aspecto_consolidado": aspecto_limpio,
            "categoria_oficial": categoria_macro
        })
        
    df_mapeo = pd.DataFrame(filas_mapeo)
    
    # Guardamos directo en tu Google Drive
    ruta_rescate = "/content/drive/MyDrive/proyecto_tesis/diccionario_mapeo_llm.csv"
    df_mapeo.to_csv(ruta_rescate, index=False, encoding='utf-8-sig')
    
    print(f"¡Procesamiento semántico finalizado en tiempo récord!")
    print(f"-> Descarga el archivo '{ruta_rescate}' a tu PC.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Procesamiento Semántico de Aspectos Turísticos")
    parser.add_argument("--database", default=r"C:\Users\ramiro\Seminario-Proyecto-2025-2026\backend\data\turismo.sqlite", help="Ruta a la base de datos SQLite")
    parser.add_argument("--attraction", default=None, help="Nombre de la atracción para procesar de forma aislada")
    
    args = parser.parse_args()
    procesar_base_de_datos(args.database, args.attraction)