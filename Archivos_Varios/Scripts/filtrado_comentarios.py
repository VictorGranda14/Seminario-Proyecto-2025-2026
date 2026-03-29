import pandas as pd
from transformers import pipeline

# --- Configuración ---
SOURCE_FILE = "data/Chile_en_limpio.xlsx"
OUTPUT_FILE = "data/procesado/comentarios_limpios_ingles.csv"
COMMENT_COLUMN = "review_text"

# Marcadores comunes que indican el inicio de la respuesta de un propietario
REPLY_MARKERS = [
    "response from the owner",
    "respuesta del propietario",
    "resposta do proprietário",
    "obrigado pela sua visita",
    "thank you for your visit",
    "dear guest,",
    "Review of:",
    "Thank you for sharing your experience",
    "Thank you for your",
]

# Cargar el detector de idioma
print("Cargando modelo de detección de idioma...")
try:
    language_detector = pipeline("text-classification", model="papluca/xlm-roberta-base-language-detection")
except Exception as e:
    print(f"Error al cargar el modelo: {e}")
    language_detector = None

def clean_and_split_comment(comment: str) -> str:
    """
    Busca marcadores de respuesta de propietarios y, si los encuentra,
    se queda solo con la parte del comentario original.
    """
    if not isinstance(comment, str):
        return "" # Devuelve un string vacío si el comentario no es texto

    comment_lower = comment.lower()
    split_index = -1

    for marker in REPLY_MARKERS:
        index = comment_lower.find(marker)
        if index != -1:
            split_index = index
            break # Nos detenemos al encontrar el primer marcador

    if split_index != -1:
        # Nos quedamos con el texto ANTES del marcador
        return comment[:split_index].strip()
    else:
        # Si no se encontró ningún marcador, devolvemos el comentario original
        return comment.strip()

def detect_language(comment: str) -> str:
    """Detecta el idioma de un comentario."""
    if not language_detector or not comment:
        return "N/A"
    try:
        result = language_detector(comment, top_k=1)
        return result[0]['label']
    except Exception:
        return "Error"

# --- Proceso Principal ---
if __name__ == "__main__":
    # 1. Cargar el Excel
    print(f"Cargando datos desde {SOURCE_FILE}...")
    df = pd.read_excel(SOURCE_FILE, nrows=1000)
    # df = pd.read_excel(SOURCE_FILE)

    # 2. Aplicar la función de limpieza a toda la columna de comentarios
    print("Limpiando comentarios y separando respuestas de propietarios...")
    df['Comentario_Limpio'] = df[COMMENT_COLUMN].apply(clean_and_split_comment)

    # 3. (Red de Seguridad) Detectar el idioma del comentario ya limpio
    print("Verificando el idioma de los comentarios limpios...")
    df['Idioma_Detectado'] = df['Comentario_Limpio'].apply(detect_language)

    # 4. Filtrar para quedarnos solo con los comentarios en inglés
    print("Filtrando para mantener solo los comentarios en inglés...")
    df_final_ingles = df[df['Idioma_Detectado'] == 'en'].copy()

    # 5. Guardar el resultado final
    print(f"Se encontraron {len(df_final_ingles)} comentarios limpios en inglés.")
    print(f"Guardando el resultado en {OUTPUT_FILE}...")
    df_final_ingles.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig', sep=';')

    print("Proceso de limpieza completado")