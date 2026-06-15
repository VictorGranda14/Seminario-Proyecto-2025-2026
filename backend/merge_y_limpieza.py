import pandas as pd
import ast

# 1. Configuración de archivos
ARCHIVO_LLM = "C:\\Users\\ramiro\\Seminario-Proyecto-2025-2026\\backend\\data\\outputs\\output_llm.csv"       # El CSV que generó tu compañero (con errores y sin filtrar)
ARCHIVO_FILTRADO = "C:\\Users\\ramiro\\Seminario-Proyecto-2025-2026\\backend\\data\\processed\\Comentarios_Final.csv"     # El CSV correcto (con más de 9 reviews y la columna 'rubro')
ARCHIVO_SALIDA = "C:\\Users\\ramiro\\Seminario-Proyecto-2025-2026\\backend\\data\\outputs\\output_llm_limpia.csv"   # El CSV final listo para tu base de datos   

print("1. Cargando archivos CSV...")
df_llm = pd.read_csv(ARCHIVO_LLM, dtype=str)
df_filtrado = pd.read_csv(ARCHIVO_FILTRADO, dtype=str)

# ==========================================
# 1. DESTRUCCIÓN DE COLUMNAS FANTASMA
# ==========================================
# El error del LLM desbordó texto hacia la derecha creando columnas "Unnamed".
# Las eliminamos para que el texto multilínea no contamine la salida.
columnas_reales = [col for col in df_llm.columns if not col.startswith('Unnamed')]
df_llm = df_llm[columnas_reales]

# ==========================================
# 2. LIMPIEZA ESTRUCTURAL (Filtrar IDs)
# ==========================================
df_llm['ID'] = pd.to_numeric(df_llm['ID'], errors='coerce')
df_llm = df_llm.dropna(subset=['ID']).copy()
df_llm['ID'] = df_llm['ID'].astype(int)

df_filtrado['ID'] = pd.to_numeric(df_filtrado['ID'], errors='coerce').fillna(-1).astype(int)

# ==========================================
# 3. ELIMINACIÓN ESTRICTA DE FILAS MALAS
# ==========================================
columna_aspectos = 'aspects' # Verifica que este sea el nombre exacto de la columna

if columna_aspectos in df_llm.columns:
    df_llm[columna_aspectos] = df_llm[columna_aspectos].fillna('')
    
    # Regla: Un formato correcto DEBE ser una lista y empezar con '['. 
    # Todo lo que tenga errores, llaves '{' o texto corrido se descarta.
    filas_antes = len(df_llm)
    df_llm = df_llm[df_llm[columna_aspectos].str.strip().str.startswith('[')].copy()
    print(f"-> Se eliminaron {filas_antes - len(df_llm)} filas con alucinaciones de formato.")

# ==========================================
# 4. MERGE (Cruce con Rubro)
# ==========================================
df_final = pd.merge(
    df_filtrado[['ID', 'rubro']], 
    df_llm, 
    on='ID', 
    how='inner'
)

# ==========================================
# 5. VALIDACIÓN SINTÁCTICA FINAL
# ==========================================
def validar_y_limpiar_json(valor):
    texto = str(valor).strip()
    try:
        parsed = ast.literal_eval(texto)
        if isinstance(parsed, list):
            return texto 
    except:
        pass
    return "[]"

if columna_aspectos in df_final.columns:
    df_final[columna_aspectos] = df_final[columna_aspectos].apply(validar_y_limpiar_json)

df_final.to_csv(ARCHIVO_SALIDA, index=False)
print(f"-> Filas finales limpias y cruzadas: {len(df_final)}")
print(f"Proceso finalizado. Archivo guardado: {ARCHIVO_SALIDA}")