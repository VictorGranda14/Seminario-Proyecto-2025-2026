import pandas as pd
import os
import re
from transformers import pipeline

# --- CONFIGURACIÓN DE RUTAS ---
INPUT_FILE = "../../data/raw/Chile_en_limpio.xlsx"
OUTPUT_FILE = "../../data/processed/Dataset_Limpio_Final.csv"

# Marcadores para recortar respuestas de propietarios
OWNER_MARKERS = [
    "response from the owner",
    "respuesta del propietario",
    "resposta do proprietário",
    "obrigado pela sua visita",
    "thank you for your visit",
    "dear guest,",
    "review of:",
    "thank you for sharing your experience",
    "thank you for your",
]

def remove_owner_responses(text):
    """Recorta el comentario si encuentra una respuesta del dueño."""
    if not isinstance(text, str):
        return text
        
    text_lower = text.lower()
    for marker in OWNER_MARKERS:
        index = text_lower.find(marker)
        if index != -1:
            return text[:index].strip()
    return text.strip()

def run_cleaning_pipeline():
    print("Iniciando Pipeline de Limpieza")
    
    # 1. Carga de datos
    print(f"Cargando datos desde {INPUT_FILE}...")
    df = pd.read_excel(INPUT_FILE)
    inicial_len = len(df)
    
    # 2. Filtrado inicial y eliminación de columnas irrelevantes
    if 'language' in df.columns:
        df = df[df['language'] == 'english'].copy()
    
    columnas_a_mantener = ['region_name', 'attraction_name', 'rating_review', 'review_text']
    df = df[[col for col in columnas_a_mantener if col in df.columns]]
    
    # 3. Limpieza de Nulos, Duplicados y Saltos de línea
    df = df.dropna(subset=['review_text'])
    df = df.drop_duplicates(subset=['review_text'])
    df['review_text'] = df['review_text'].replace(r'\n|\r', ' ', regex=True)
    
    # 4. Creación de ID Único
    df.insert(0, 'Comment_ID', [f"REV-{i+1}" for i in range(len(df))])
    
    # 5. Recorte de respuestas de propietarios
    print("Recortando respuestas de propietarios...")
    df['review_text'] = df['review_text'].apply(remove_owner_responses)
    # Volver a quitar comentarios que hayan quedado vacíos tras el recorte
    df = df[df['review_text'].str.len() > 10] 
    
    # 6. Validación de idioma con Transformer (xlm-roberta-base)
    print("Cargando modelo xlm-roberta-base para validación de idioma...")
    # Usamos un modelo afinado para detección de idioma basado en xlm-roberta
    lang_classifier = pipeline("text-classification", model="papluca/xlm-roberta-base-language-detection", device=-1)
    
    print(f"Validando {len(df)} comentarios (Esto puede tomar un tiempo)...")
    valid_texts = []
    
    for idx, row in df.iterrows():
        text = row['review_text']
        # Truncar a ~512 palabras (aproximación rápida a tokens) para evitar errores del transformer
        truncated_text = " ".join(text.split()[:400])
        
        try:
            prediction = lang_classifier(truncated_text)[0]
            if prediction['label'] == 'en':  # Solo mantenemos si el transformer confirma que es inglés
                valid_texts.append(row)
        except Exception as e:
            continue # Si falla un texto muy raro, lo saltamos
            
    df_final = pd.DataFrame(valid_texts)
    
    # 7. Guardado Final
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    df_final.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig', sep=';')
    
    print("\n--- RESUMEN DE LIMPIEZA ---")
    print(f"Comentarios originales: {inicial_len}")
    print(f"Comentarios finales válidos: {len(df_final)}")
    print(f"Dataset listo guardado en: {OUTPUT_FILE}")

if __name__ == "__main__":
    run_cleaning_pipeline()