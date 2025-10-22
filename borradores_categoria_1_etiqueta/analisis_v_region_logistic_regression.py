import pandas as pd
import spacy
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

import joblib

# Cargar modelo de spaCy en español
nlp = spacy.load("es_core_news_sm")

# Cargar los datos
df = pd.read_excel("./V_es_categorizado.xlsx")

# Preprocesamiento con spaCy
def procesar_texto_spacy(texto):
    doc = nlp(texto.lower())
    tokens = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
    return " ".join(tokens)

# Aplicar preprocesamiento
df["texto_limpio"] = df["review_text"].astype(str).apply(procesar_texto_spacy)

# Dividir datos
X = df["texto_limpio"]
y = df["categoria"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Pipeline: vectorización + modelo
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("clf", LogisticRegression(max_iter=1000))
])

# Entrenar modelo
pipeline.fit(X_train, y_train)

# Evaluación
y_pred = pipeline.predict(X_test)
print(classification_report(y_test, y_pred))

# Guardar pipeline completo
joblib.dump(pipeline, "modelo_logistic_regression_categorias.pkl")