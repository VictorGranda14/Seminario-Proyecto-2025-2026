import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# --- Configuración del Cliente ---
AZURE_ENDPOINT = os.getenv("AZURE_LANGUAGE_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_LANGUAGE_KEY")

def _get_authenticated_client():
    """Crea y devuelve un cliente autenticado para Text Analytics."""
    credential = AzureKeyCredential(AZURE_KEY)
    client = TextAnalyticsClient(endpoint=AZURE_ENDPOINT, credential=credential)
    return client

# --- Funciones para llamar a las APIs y PARSEAR los resultados ---
def analyze_sentiments_and_opinions(comments: list[str]) -> list[tuple[str, str]]:
    """
    Analiza una lista de comentarios y devuelve una lista de tuplas 
    con (sentimiento_general, aspectos_minados_con_sentimiento).
    Formato de salida: "aspecto(opinion|sentimiento), aspecto2(opinion2|sentimiento2)"
    """
    client = _get_authenticated_client()
    response = client.analyze_sentiment(
        documents=comments, 
        show_opinion_mining=True,
        language="en"
    )
    
    parsed_results = []
    for doc in response:
        if doc.is_error:
            parsed_results.append(("ERROR", "ERROR"))
            continue
            
        # Parsear los aspectos, sus opiniones Y SU SENTIMIENTO
        mined_opinions = []
        for sentence in doc.sentences:
            if sentence.mined_opinions:
                for mined_opinion in sentence.mined_opinions:
                    target = mined_opinion.target
                    assessments = mined_opinion.assessments
                    
                    aspect_text = target.text
                    
                    # Unimos opiniones y tomamos el sentimiento de la primera (generalmente coinciden)
                    opinion_texts = " ".join([a.text for a in assessments])
                    # Tomamos el sentimiento de la opinión (positive/negative/mixed)
                    sentiment = assessments[0].sentiment if assessments else "neutral"
                    
                    # Guardamos con el separador '|'
                    mined_opinions.append(f"{aspect_text}({opinion_texts}|{sentiment})")
        
        parsed_results.append((doc.sentiment, ", ".join(mined_opinions)))
        
    return parsed_results

def classify_tx_dimensions(comments: list[str]) -> list[str]:
    """
    Clasifica una lista de comentarios y devuelve una lista de strings 
    con las dimensiones TX encontradas.
    """
    client = _get_authenticated_client()
    
    project_name = "Clasificador-Multietiqueta-Tesis" 
    deployment_name = "model-v1"

    poller = client.begin_multi_label_classify(
        documents=comments,
        project_name=project_name,
        deployment_name=deployment_name,
        language="en"
    )
    
    result = poller.result()
    
    parsed_results = []
    for doc_result in result:
        if doc_result.is_error:
            parsed_results.append("ERROR")
            continue
        
        # Extraemos las categorías (etiquetas) y las unimos con comas
        # doc_result.classifications es una lista de objetos ClassificationCategory
        labels = [classification.category for classification in doc_result.classifications]
        
        # Si no encontró ninguna etiqueta, esto quedará como una cadena vacía "", lo cual es correcto
        parsed_results.append(", ".join(labels))
        
    return parsed_results