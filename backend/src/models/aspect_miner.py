import warnings
import spacy
from pyabsa import AspectTermExtraction as ATEPC
import logging

from src.models.base_model import BaseAnalysisModel

# Suprimimos advertencias de librerías subyacentes (HuggingFace/Transformers) 
# para mantener la consola limpia y enfocada solo en nuestros logs de orquestación.
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)

class AspectMinerLocal(BaseAnalysisModel):
    name = "local"
    def __init__(self):
        """
        Constructor del pipeline híbrido (Neuro-simbólico).
        Combina un modelo probabilístico (Transformers) con un motor determinista (Reglas gramaticales).
        """
        print("Inicializando modelo base de Minería de Opiniones (PyABSA/DeBERTa)...")
        # El modelo 'english' base se encarga de la Detección de Aspectos y Clasificación de Polaridad (ATEPC)
        self.extractor = ATEPC.AspectExtractor('english')
        
        print("Cargando motor gramatical (SpaCy) para extracción precisa y limpieza heurística...")
        try:
            # Cargamos el modelo pequeño de SpaCy. Es suficiente para etiquetado POS y árboles de dependencia.
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("No se encontró el modelo de SpaCy. Ejecuta en terminal: python -m spacy download en_core_web_sm")
            self.nlp = None
            
        # DICCIONARIOS DE CONTROL (Capa Heurística)
        # 1. Stopwords de Aspectos: Palabras que PyABSA detecta erróneamente como aspectos útiles.
        # Filtramos pronombres y palabras vacías para asegurar la calidad de la base de datos.
        self.stop_aspects = {"it", "this", "they", "that", "people", "everything", "nothing", 
                             "something", "one", "he", "she", "we", "us", "them", "there", "here"}
        
        # 2. Entidades Core (Core Entities): Palabras críticas del negocio (Enoturismo / Astroturismo / Agencias).
        # Actúan como "red de seguridad" si el modelo probabilístico (PyABSA) falla en detectarlas.
        self.palabras_criticas = {"wine", "tour", "guide", "food", "tasting", "ticket", "experience",
                                  "stars", "telescope", "sky", "driver", "place", "transport", 
                                  "van", "bus", "view", "landscape", "walk", "staff", "reservation", 
                                  "transportation", "company"}
        
        # 3. Stopwords de Opiniones (Ruido descriptivo)
        # Palabras que SpaCy clasifica como adjetivos/adverbios pero que no aportan valor de sentimiento
        self.stop_opinions = {"many", "other", "much", "more", "less", "few", "actual", 
                              "same", "several", "own", "only", "such", "certain", "various", 
                              "entire", "whole", "enough", "first", "last", "next", "final",
                              "finally", "also", "very", "really", "too", "quite", "just", "even"}

    def _extraer_adjetivo_preciso(self, oracion, aspecto, polaridad):
        """
        Intento 1 de extracción: Análisis de Dependencias Sintácticas.
        Incorpora filtro de ruido (stop_opinions) y heurística posicional.
        """
        if not self.nlp: 
            return ""
            
        doc = self.nlp(oracion)
        opinion_parts = []
        aspecto_raiz = aspecto.split()[-1].lower() 
        
        for token in doc:
            if token.text.lower() == aspecto_raiz:
                
                # Caso A: El adjetivo modifica directamente al sustantivo
                for child in token.children:
                    if child.dep_ in ["amod", "advmod"]:
                        texto_adjetivo = child.text.lower()
                        
                        # FILTRO DE RUIDO
                        if texto_adjetivo not in self.stop_opinions:
                            # 1. Búsqueda de negación estricta
                            neg = " ".join([w.text for w in child.children if w.dep_ == "neg"])
                            
                            # 2. Heurística posicional (si falla el árbol)
                            if not neg:
                                palabras_previas = [doc[i].text.lower() for i in range(max(0, child.i - 2), child.i)]
                                if any(n in palabras_previas for n in ["not", "no", "never", "n't", "barely"]):
                                    neg = "not"
                                    
                            opinion_parts.append(f"{neg} {texto_adjetivo}".strip())
                            
                        # Atrapa adjetivos encadenados por conjunción, aplicando el mismo filtro
                        for conj in child.children:
                            if conj.dep_ == "conj":
                                texto_conj = conj.text.lower()
                                if texto_conj not in self.stop_opinions:
                                    opinion_parts.append(texto_conj)

                # Caso B: El adjetivo está en el predicado, tras un verbo
                if token.dep_ in ["nsubj", "nsubjpass"]:
                    verb = token.head 
                    for child in verb.children:
                        if child.dep_ in ["acomp", "attr", "oprd"]:
                            texto_adjetivo = child.text.lower()
                            
                            # FILTRO DE RUIDO
                            if texto_adjetivo not in self.stop_opinions:
                                # 1. Búsqueda de negación estricta
                                neg = " ".join([w.text for w in verb.children if w.dep_ == "neg"] + 
                                               [w.text for w in child.children if w.dep_ == "neg"])
                                
                                # 2. Heurística posicional
                                if not neg:
                                    palabras_previas = [doc[i].text.lower() for i in range(max(0, child.i - 2), child.i)]
                                    if any(n in palabras_previas for n in ["not", "no", "never", "n't", "barely"]):
                                        neg = "not"
                                        
                                opinion_parts.append(f"{neg} {texto_adjetivo}".strip())
                                
                            # Atrapa adjetivos encadenados por conjunción, aplicando el mismo filtro
                            for conj in child.children:
                                if conj.dep_ == "conj": 
                                    texto_conj = conj.text.lower()
                                    if texto_conj not in self.stop_opinions:
                                        opinion_parts.append(texto_conj)
        
        if opinion_parts:
            # Retornamos los adjetivos unidos, eliminando duplicados
            return " ".join(list(dict.fromkeys(opinion_parts)))
            
        return ""

    def _lematizar_aspecto(self, aspecto):
        """
        Normalización de texto. Convierte plurales a singulares para evitar que 
        'guide' y 'guides' se agrupen como aspectos distintos en el análisis estadístico.
        """
        if not self.nlp: return aspecto.lower()
        return " ".join([token.lemma_ for token in self.nlp(aspecto.lower())])

    def extract_aspects(self, text: str):
        """
        Función principal oquestadora. Recibe un texto, extrae aspectos, 
        limpia los datos y aplica mecanismos de respaldo.
        """
        if not isinstance(text, str) or len(text.strip()) == 0:
            return []

        # --- FASE 1: INFERENCIA MODELO TRANSFORMER ---
        result = self.extractor.predict(text, save_result=False, print_result=False, ignore_error=True)
        extracted_data = []
        aspectos_encontrados = [] # Registro para evitar colisiones con la red de seguridad
        
        # Manejo de la estructura de salida dinámica de PyABSA
        if isinstance(result, list) and len(result) > 0:
            res_dict = result[0]
        elif isinstance(result, dict):
            res_dict = result
        else:
            return []
            
        oracion_completa = text
        if 'tokens' in res_dict:
            # Reconstruimos la oración original sin perder el contexto que PyABSA procesó
            oracion_completa = " ".join(res_dict['tokens']).replace(" .", ".").replace(" ,", ",")
            
        # Si el modelo encontró aspectos matemáticamente
        if 'aspect' in res_dict and res_dict['aspect']:
            for i in range(len(res_dict['aspect'])):
                aspecto_crudo = res_dict['aspect'][i].lower()
                polaridad = res_dict['sentiment'][i].lower()
                
                # Limpieza Heurística 1: Lematización
                aspecto_limpio = self._lematizar_aspecto(aspecto_crudo)
                
                # Limpieza Heurística 2: Eliminación de ruido (Stopwords)
                if aspecto_limpio in self.stop_aspects:
                    continue
                
                # --- FASE 2: EXTRACCIÓN DE OPINIONES ---
                # Intento principal (Alta Precisión): Análisis de Dependencias
                opinion_precisa = self._extraer_adjetivo_preciso(oracion_completa, aspecto_limpio, polaridad)
                
                # Intento secundario (Alto Recall): Fallback por Etiquetado POS
                # Se activa si el intento principal falló debido a gramática informal (ej. mala puntuación)
                if not opinion_precisa.strip():
                    if self.nlp:
                        doc_oracion = self.nlp(oracion_completa)
                        raiz = aspecto_limpio.split()[-1]
                        
                        aspect_token = None
                        for t in doc_oracion:
                            if t.text.lower() == raiz:
                                aspect_token = t
                                break
                                
                        if aspect_token:
                            # Escaneamos una ventana de contexto de +/- 4 tokens alrededor del aspecto
                            inicio = max(0, aspect_token.i - 4)
                            fin = min(len(doc_oracion), aspect_token.i + 5)
                            adjetivos = []
                            
                            for t in doc_oracion[inicio:fin]:
                                # Extraemos estrictamente Adjetivos (ADJ) o Adverbios (ADV)
                                if t.pos_ in ["ADJ", "ADV"] and t.text.lower() != raiz:
                                    neg = " ".join([w.text for w in t.children if w.dep_ == "neg"])
                                    adjetivos.append(f"{neg} {t.text}".strip())
                            
                            if adjetivos:
                                opinion_precisa = " ".join(list(dict.fromkeys(adjetivos))).lower()
                            else:
                                opinion_precisa = "mencion general" # Se documenta la mención sin adjetivo claro
                    else:
                        opinion_precisa = "mencion general"
                
                # Guardamos el dato limpio y procesado
                extracted_data.append({
                    'aspect': aspecto_limpio,
                    'opinion': opinion_precisa,
                    'sentiment': polaridad
                })
                aspectos_encontrados.append(aspecto_limpio)

        # --- FASE 3: RED DE SEGURIDAD BASADA EN REGLAS ---
        # Fuerza la búsqueda de "entidades core" que PyABSA ignoró por sesgos del pre-entrenamiento.
        if self.nlp:
            doc = self.nlp(oracion_completa.lower())
            raices_encontradas = [a.split()[-1] for a in aspectos_encontrados]
            
            for token in doc:
                lema = token.lemma_ 
                
                if lema in self.palabras_criticas and lema not in raices_encontradas:
                    opinion_forzada = self._extraer_adjetivo_preciso(oracion_completa, lema, "neutral")
                    
                    if opinion_forzada.strip() != "":
                        # Heurística simple de polaridad basada en la existencia de modificadores negativos
                        sentimiento_parche = "negative" if "not " in opinion_forzada or "no " in opinion_forzada else "positive"
                        
                        extracted_data.append({
                            'aspect': lema,
                            'opinion': opinion_forzada,
                            'sentiment': sentimiento_parche
                        })
                        raices_encontradas.append(lema)
        
        return extracted_data

# --- BLOQUE DE PRUEBA LOCAL ---
# Permite testear el script de forma aislada sin levantar todo el orquestador (main.py)
if __name__ == "__main__":
    miner = AspectMinerLocal()
    
    comentarios_prueba = [
        "We did this tour, extraordinary. A very friendly astronomer guide the incredible views.",
        "They have 7 professional telescopes. We were picked up as promised. Midnight snack options were good.",
        "First we received basic explanations via a short video before we started stargazing."
    ]
    
    for c in comentarios_prueba:
        print(f"\nAnalizando: '{c}'")
        resultados = miner.extract_aspects(c)
        if not resultados:
            print(" - (Ningún aspecto con adjetivo válido encontrado)")
        for r in resultados:
            print(f" - Aspecto: {r['aspect']} | Opinión: {r['opinion']} | Sentimiento: {r['sentiment']}")