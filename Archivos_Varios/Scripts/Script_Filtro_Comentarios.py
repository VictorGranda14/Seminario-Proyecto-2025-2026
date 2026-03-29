import pandas as pd
from transformers import pipeline
import os

# --- Configuración ---
SOURCE_FILE = "data/Comentarios_en_SinFiltrado.xlsx"
OUTPUT_FILE = "data/processed/Comentarios_en_Final.xlsx"
COMMENT_COLUMN = "review_text"

# Columnas que quieres MANTENER en el archivo final
FINAL_COLUMNS = ["ID", "region_name", "attraction_name", "rating_review", "review_text", "companion_type", "location"]

BATCH_SIZE = 64
MAX_LENGTH = 512

# --- Muestreo para pruebas ---
PROCESS_SAMPLE = False
SAMPLE_SIZE = 1000

REPLY_MARKERS = [
    # --- Marcadores en Inglés ---
    "response from the owner",
    "response from manager",
    "management response",
    "owner response",
    "review of:",
    "dear guest,",
    "dear traveler,",
    "thank you for your review",
    "thank you for your feedback",
    "thank you for sharing your experience",
    "thank you for your visit",
    "thank you for your",
    "thank you very much",
    "we appreciate your feedback",
    "we are sorry to hear",
    "we sincerely apologize",

    # --- Marcadores en Español ---
    "respuesta del propietario",
    "estimado viajero",
    "estimada viajera",
    "estimado cliente",
    "gracias por su comentario",
    "gracias por tu comentario",
    "agradecemos sus comentarios",
    "lamentamos sinceramente",

    # --- Marcadores en Portugués ---
    "resposta do proprietário",
    "resposta do gerente",
    "prezado viajante",
    "caro cliente",
    "obrigado pela sua visita",
    "agradecemos o seu feedback",
    "obrigado pelo seu comentário",
]

if __name__ == "__main__":
    output_dir = os.path.dirname(OUTPUT_FILE)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Cargando modelo de detección de idioma...")
    language_detector = pipeline("text-classification", model="papluca/xlm-roberta-base-language-detection")

    print(f"Cargando datos desde {SOURCE_FILE}...")
    df = pd.read_excel(SOURCE_FILE)
    
    if PROCESS_SAMPLE:
        print(f"Seleccionando una muestra aleatoria de {SAMPLE_SIZE} comentarios...")
        df = df.sample(n=SAMPLE_SIZE, random_state=42).copy()
    
    initial_rows = len(df)
    
    # --- Inicializamos contadores y la lista para los resultados finales ---
    trimmed_count = 0
    final_rows_data = []

    print("Iniciando limpieza y filtrado de comentarios en lotes...")
    for i in range(0, len(df), BATCH_SIZE):
        batch_df = df.iloc[i:i+BATCH_SIZE]
        
        cleaned_batch = []
        original_comments_batch = []
        
        # 1. Limpieza de comentarios en el lote
        for index, row in batch_df.iterrows():
            original_comment = str(row[COMMENT_COLUMN]) if pd.notna(row[COMMENT_COLUMN]) else ""
            cleaned_comment = original_comment.strip()
            comment_lower = cleaned_comment.lower()
            was_trimmed = False

            for marker in REPLY_MARKERS:
                marker_index = comment_lower.find(marker)
                if marker_index != -1:
                    cleaned_comment = cleaned_comment[:marker_index].strip()
                    was_trimmed = True
                    break
            
            if was_trimmed:
                trimmed_count += 1
            
            cleaned_batch.append(cleaned_comment)
            original_comments_batch.append(row.to_dict()) # Guardamos la info original de la fila

        # 2. Detección de idioma en el lote limpio
        truncated_batch = [c[:MAX_LENGTH] for c in cleaned_batch]
        try:
            language_results = language_detector(truncated_batch, top_k=1)
            detected_languages = [res[0]['label'] for res in language_results]
        except Exception:
            detected_languages = ['Error'] * len(batch_df)

        # 3. Construcción de la lista de resultados finales
        for j, lang in enumerate(detected_languages):
            if lang == 'en' and cleaned_batch[j]: # Si es inglés y no está vacío
                # Tomamos la info original y reemplazamos el comentario por el limpio
                final_row = original_comments_batch[j]
                final_row[COMMENT_COLUMN] = cleaned_batch[j]
                final_rows_data.append(final_row)

        if (i // BATCH_SIZE) % 10 == 0:
            print(f"  Procesados {i + len(batch_df)} de {initial_rows} comentarios...")

    # --- Creación del DataFrame final y guardado ---
    print("Creando el DataFrame final con los datos limpios...")
    df_final = pd.DataFrame(final_rows_data)
    
    # Asegurarnos de que solo queden las columnas deseadas
    df_final = df_final[FINAL_COLUMNS]

    conserved_count = len(df_final)
    discarded_count = initial_rows - conserved_count

    print(f"\n--- RESUMEN DEL PROCESO ---")
    print(f"Filas iniciales procesadas: {initial_rows}")
    print(f"Comentarios recortados (respuesta de propietario): {trimmed_count}")
    print(f"Comentarios conservados (inglés): {conserved_count}")
    print(f"Comentarios descartados (otro idioma, vacíos, etc.): {discarded_count}")
    
    print(f"\nGuardando el resultado final en {OUTPUT_FILE}...")
    df_final.to_excel(OUTPUT_FILE, index=False)

    print("¡Proceso de limpieza completado!")