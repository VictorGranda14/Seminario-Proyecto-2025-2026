import sqlite3
import requests
import json
import time

# Configuración del motor local
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:3b" # Cambiar a "qwen2.5:7b" si tienes la versión de 7B activa en Ollama

def generar_resumen_local(nombre, tipo, total_reviews, polaridad_positiva, categorias_top, top_fortalezas, top_alertas):
    contexto_tipo = f"el rubro sectorial '{nombre}'" if tipo == "rubro" else f"la atracción turística '{nombre}'"
        
    prompt = f"""Actúa como un analista experto en turismo. Escribe un resumen ejecutivo de un solo párrafo (máximo 4 líneas) para {contexto_tipo}. 
    
Basa tu análisis ESTRICTAMENTE en estos datos consolidados:
- Volumen de opiniones: {total_reviews}
- Positividad general: {polaridad_positiva}%
- Fortalezas destacadas: {top_fortalezas}
- Fricciones o alertas operativas: {top_alertas}

Reglas: 
1. Mantén un tono formal, directo y profesional.
2. NO inventes información, limítate a sintetizar los datos proporcionados.
3. Traduce naturalmente al español cualquier atributo o palabra clave que venga en inglés.
4. No saludes, no uses viñetas, ni des explicaciones. Devuelve únicamente el párrafo redactado.
"""
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
        }
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()
    except Exception as e:
        print(f"Error en la API de Ollama para {nombre}: {e}")
        return "No se pudo generar el resumen ejecutivo en este momento."

def formatear_aspectos(lista_aspectos):
    if not lista_aspectos:
        return "Ninguna"
    
    textos = []
    for item in lista_aspectos[:3]: # Tomamos el Top 3
        aspecto = item.get("aspect", "")
        keywords = item.get("keywords", [])
        
        if isinstance(keywords, list):
            kw_str = ", ".join(keywords)
        else:
            kw_str = str(keywords)
            
        texto_final = f"{aspecto} (Atributos: {kw_str})" if kw_str else aspecto
        textos.append(texto_final)
        
    return " | ".join(textos)

def procesar_resumenes_json(ruta_db: str):
    conexion = sqlite3.connect(ruta_db)
    cursor = conexion.cursor()

    # Procesamos únicamente Rubros y Atracciones
    cursor.execute("""
        SELECT identificador_vista, nombre_vista, tipo_vista, json_completo 
        FROM metricas_consolidadas 
        WHERE tipo_vista IN ('atraccion', 'rubro')
    """)
    filas = cursor.fetchall()

    if not filas:
        print("No se encontraron entidades para procesar.")
        conexion.close()
        return

    print(f"Analizando {len(filas)} entidades (Rubros y Atracciones)...")

    for fila in filas:
        id_vista, nombre, tipo, json_str = fila
        
        try:
            datos_vista = json.loads(json_str)
            if isinstance(datos_vista, str):
                datos_vista = json.loads(datos_vista)
        except Exception as e:
            print(f"Error decodificando el JSON de {nombre}: {e}")
            continue

        resumen_actual = datos_vista.get("executiveSummary", "")
        
        if isinstance(resumen_actual, str):
            texto_limpio = resumen_actual.strip()
            
            es_marcador_posicion = (
                texto_limpio == "" or
                "Por definir" in texto_limpio or
                "en construcción" in texto_limpio or
                "análisis semántico" in texto_limpio or
                texto_limpio.startswith("Resumen ejecutivo") or 
                len(texto_limpio) < 40
            )
            
            if not es_marcador_posicion:
                continue

        print(f"Generando resumen para [{tipo.upper()}] {nombre}...")
        
        info_vista = datos_vista.get("vistaInfo", {})
        ratio_sentimiento = info_vista.get("sentimentRatio", {})
        total_rev = info_vista.get("totalReviews", 0)
        pct_positivo = ratio_sentimiento.get("positive", 0)

        # --- EXTRACTOR SEGURO DE CATEGORÍAS OFICIALES AFECTADAS ---
        macro_cats_lista = datos_vista.get("macroCategories", [])
        if macro_cats_lista and isinstance(macro_cats_lista, list):
            macro_cats_ordenadas = sorted(macro_cats_lista, key=lambda x: x.get("freq", 0), reverse=True)
            categorias_top = ", ".join([f"{c.get('category', '')} ({c.get('freq', 0)} opiniones)" for c in macro_cats_ordenadas[:2]])
        else:
            categorias_top = f"Rubro {nombre}" if tipo == "rubro" else "No especificado"

        analisis_aspectos = datos_vista.get("aspectAnalysis", {})
        fortalezas = formatear_aspectos(analisis_aspectos.get("strengths", []))
        alertas = formatear_aspectos(analisis_aspectos.get("alerts", []))

        inicio_tiempo = time.time()
        
        resumen_texto = generar_resumen_local(nombre, tipo, total_rev, pct_positivo, categorias_top, fortalezas, alertas)
        
        tiempo_transcurrido = time.time() - inicio_tiempo
        print(f"✓ Generado en {tiempo_transcurrido:.2f} segundos.")

        # Asignar e inyectar el texto limpio en la estructura JSON
        datos_vista["executiveSummary"] = resumen_texto
        json_actualizado = json.dumps(datos_vista, ensure_ascii=False)

        cursor.execute("""
            UPDATE metricas_consolidadas 
            SET json_completo = ? 
            WHERE identificador_vista = ?
        """, (json_actualizado, id_vista))
        
        conexion.commit()

    conexion.close()
    print("Pipeline de generación finalizado con éxito.")

if __name__ == "__main__":
    ruta_base_datos = "C:\\Users\\ramiro\\Seminario-Proyecto-2025-2026\\backend\\data\\turismo.sqlite"
    procesar_resumenes_json(ruta_base_datos)