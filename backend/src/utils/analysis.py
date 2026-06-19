import pandas as pd
import os
import re

# --- CONFIGURACIÓN ---
INPUT_FILE = "data/processed/Analisis_Vina_Santa_Rita.xlsx"
OUTPUT_FOLDER = "data/reports"
OUTPUT_EXCEL = f"{OUTPUT_FOLDER}/Tablero_Vina_Santa_Rita.xlsx"

# Mapa de normalización
NORMALIZATION_MAP = {
    "tours": "tour", "guides": "guide", "drivers": "driver",
    "views": "view", "wines": "wine", "experiences": "experience",
    "places": "place", "landscapes": "landscape", "stops": "stop",
    "days": "day", "staffs": "staff", "buses": "bus", "walks": "walk",
    "prices": "price", "services": "service", "restaurants": "restaurant",
    "foods": "food", "lunchs": "lunch", "waits": "wait", "queues": "queue"
}

def parse_aspects_with_sentiment(aspect_string):
    """
    Transforma "guide(friendly|positive)" en diccionarios con sentimiento individual.
    """
    if not isinstance(aspect_string, str): return []
    
    pattern = r"([^,]+)\(([^|]+)\|([^)]+)\)"
    matches = re.findall(pattern, aspect_string)
    
    parsed = []
    for aspect, opinion, sentiment in matches:
        clean_aspect = aspect.strip().lower()
        clean_aspect = NORMALIZATION_MAP.get(clean_aspect, clean_aspect)
        
        parsed.append({
            'aspect': clean_aspect,
            'opinion': opinion.strip().lower(),
            'sentiment': sentiment.strip().lower() # Sentimiento específico del aspecto
        })
    return parsed

def get_top_opinions(aspect_name, df_subset):
    """Devuelve las 5 opiniones más comunes."""
    ops = df_subset[df_subset['Aspecto'] == aspect_name]['Opinion'].value_counts().head(5).index.tolist()
    return ", ".join(ops)

def get_dimension_counts(df_subset):
    """Calcula frecuencia de dimensiones."""
    df_dims = df_subset.explode('lista_dimensiones')
    df_dims = df_dims[df_dims['lista_dimensiones'] != '']
    conteo = df_dims['lista_dimensiones'].value_counts().reset_index()
    conteo.columns = ['Dimensión', 'Frecuencia']
    conteo['% del Segmento'] = (conteo['Frecuencia'] / len(df_subset) * 100).round(1).astype(str) + '%'
    return conteo

def main():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    print(f"Cargando datos desde {INPUT_FILE}...")
    try:
        df = pd.read_excel(INPUT_FILE)
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo.")
        return

    print("Procesando con precisión por aspecto...")

    # 1. Preprocesamiento
    df['lista_dimensiones'] = df['Dimensiones_TX'].fillna('').apply(lambda x: x.split(', ') if x else [])
    
    df['lista_aspectos'] = df['Aspectos_Minados'].apply(parse_aspects_with_sentiment)
    
    # Sentimiento Global (Solo para separar dimensiones generales)
    df['Sentimiento_Global'] = df['Sentimiento'].str.lower()

    # ==========================================
    # 1. ANÁLISIS DE DIMENSIONES (Usando Sentimiento Global)
    # ==========================================
    # Para las dimensiones seguimos usando el global porque la dimensión es del comentario entero
    df_pos_global = df[df['Sentimiento_Global'] == 'positive']
    df_neg_global = df[df['Sentimiento_Global'].isin(['negative', 'mixed'])]
    
    dims_pos = get_dimension_counts(df_pos_global)
    dims_neg = get_dimension_counts(df_neg_global)
    
    dims_total = get_dimension_counts(df)[['Dimensión', 'Frecuencia']].rename(columns={'Frecuencia': 'Total'})
    dims_maestra = dims_total.merge(dims_pos[['Dimensión', 'Frecuencia']], on='Dimensión', how='left').rename(columns={'Frecuencia': 'Positivas'})
    dims_maestra = dims_maestra.merge(dims_neg[['Dimensión', 'Frecuencia']], on='Dimensión', how='left').rename(columns={'Frecuencia': 'Negativas'}).fillna(0)

    # ==========================================
    # 2. ANÁLISIS DE ASPECTOS (Usando Sentimiento ESPECÍFICO)
    # ==========================================
    df_aspectos = df.explode('lista_aspectos').dropna(subset=['lista_aspectos'])
    
    # Extraemos los datos individuales
    df_aspectos['Aspecto'] = df_aspectos['lista_aspectos'].apply(lambda x: x['aspect'])
    df_aspectos['Opinion'] = df_aspectos['lista_aspectos'].apply(lambda x: x['opinion'])
    df_aspectos['Sentimiento_Aspecto'] = df_aspectos['lista_aspectos'].apply(lambda x: x['sentiment'])

    # --- FORTALEZAS (Aspectos explícitamente positivos) ---
    aspectos_pos = df_aspectos[df_aspectos['Sentimiento_Aspecto'] == 'positive']
    
    top_pos = aspectos_pos['Aspecto'].value_counts().reset_index()
    top_pos.columns = ['Aspecto (Fortaleza)', 'Frecuencia']
    top_pos['Opiniones Clave'] = top_pos['Aspecto (Fortaleza)'].apply(lambda x: get_top_opinions(x, aspectos_pos))

    # --- ALERTAS (Aspectos explícitamente negativos) ---
    aspectos_neg = df_aspectos[df_aspectos['Sentimiento_Aspecto'] == 'negative']
    
    top_neg = aspectos_neg['Aspecto'].value_counts().reset_index()
    top_neg.columns = ['Aspecto (Alerta)', 'Frecuencia']
    top_neg['Opiniones Clave'] = top_neg['Aspecto (Alerta)'].apply(lambda x: get_top_opinions(x, aspectos_neg))

    # ==========================================
    # GUARDAR REPORTE
    # ==========================================
    print(f"Guardando reporte preciso en {OUTPUT_EXCEL}...")
    
    with pd.ExcelWriter(OUTPUT_EXCEL, engine='openpyxl') as writer:
        dims_maestra.to_excel(writer, sheet_name='1. Panorama Dimensiones', index=False)
        
        # Hoja 2: Fortalezas Reales
        dims_pos.to_excel(writer, sheet_name='2. Fortalezas', index=False, startrow=0)
        top_pos.to_excel(writer, sheet_name='2. Fortalezas', index=False, startrow=len(dims_pos) + 4)
        
        # Hoja 3: Alertas Reales (¡Ahora mucho más precisas!)
        dims_neg.to_excel(writer, sheet_name='3. Alertas de Calidad', index=False, startrow=0)
        top_neg.to_excel(writer, sheet_name='3. Alertas de Calidad', index=False, startrow=len(dims_neg) + 4)

        for sheet in writer.sheets.values():
            sheet.column_dimensions['A'].width = 25
            sheet.column_dimensions['B'].width = 15
            sheet.column_dimensions['C'].width = 50

    print("¡Tablero generado!")

if __name__ == "__main__":
    main()