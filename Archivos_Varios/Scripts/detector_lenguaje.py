from transformers import pipeline

# --- Configuración del Modelo ---
# Cargamos el pipeline de "detección de texto".
try:
    language_detector = pipeline("text-classification", model="papluca/xlm-roberta-base-language-detection")
except Exception as e:
    print(f"Error al cargar el modelo de detección de idioma: {e}")
    language_detector = None

# --- Función para Detectar el Idioma ---
def detect_language(comment: str) -> str:
    """
    Detecta el idioma de un comentario usando un modelo de Hugging Face.
    Devuelve el código del idioma (ej. 'es' para español) o 'Error' si falla.
    """
    if not language_detector:
        return "Error: Modelo no cargado"
        
    try:
        # El pipeline procesa el texto y devuelve la etiqueta con la puntuación más alta
        result = language_detector(comment, top_k=1)
        # El resultado es una lista, tomamos el primer elemento
        language_code = result[0]['label']
        return language_code
    except Exception as e:
        print(f"Error al detectar el idioma del comentario: {comment[:50]}... - {e}")
        return "Error"

if __name__ == "__main__":
    comentario_es = "Esta es una prueba para ver si detecta el español correctamente."
    comentario_en = "This is a test to see if it detects English correctly."
    comentario_fr = "Ceci est un test pour voir s'il détecte correctement le français."

    lang_es = detect_language(comentario_es)
    lang_en = detect_language(comentario_en)
    lang_fr = detect_language(comentario_fr)

    print(f"Texto: '{comentario_es}' -> Idioma Detectado: {lang_es}")
    print(f"Texto: '{comentario_en}' -> Idioma Detectado: {lang_en}")
    print(f"Texto: '{comentario_fr}' -> Idioma Detectado: {lang_fr}")