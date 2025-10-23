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
    con (sentimiento_general, aspectos_minados).
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
            
        # Parsear los aspectos y sus opiniones en un solo string
        mined_opinions = []
        for sentence in doc.sentences:
            for opinion in sentence.mined_opinions:
                aspect = opinion.aspect.text
                opinion_texts = " ".join([o.text for o in opinion.opinions])
                mined_opinions.append(f"{aspect}({opinion_texts})")
        
        parsed_results.append((doc.sentiment, ", ".join(mined_opinions)))
        
    return parsed_results

def classify_tx_dimensions(comments: list[str]) -> list[str]:
    """
    Clasifica una lista de comentarios y devuelve una lista de strings 
    con las dimensiones TX encontradas.
    """
    client = _get_authenticated_client()
    project_name = "ClasificadorDimensionesTX"  # El nombre que le diste a tu proyecto
    deployment_name = "deployment-name"       # El nombre que le diste al despliegue

    poller = client.begin_multi_label_classify(
        documents=comments,
        project_name=project_name,
        deployment_name=deployment_name
    )
    
    result = poller.result()
    
    parsed_results = []
    for doc_result in result:
        if doc_result.is_error:
            parsed_results.append("ERROR")
            continue
        
        # Unir todas las etiquetas encontradas en un solo string
        labels = [classification.category for classification in doc_result.classifications]
        parsed_results.append(", ".join(labels))
        
    return parsed_results