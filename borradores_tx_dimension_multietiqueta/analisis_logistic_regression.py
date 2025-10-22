import pandas as pd
import spacy
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
from sklearn.multioutput import MultiOutputClassifier
from sklearn.preprocessing import MultiLabelBinarizer
import joblib

# Cargar modelo spaCy
nlp = spacy.load("es_core_news_sm")

# Cargar datos
df = pd.read_excel("./datos_etiquetados/compilado_chile_con_TX.xlsx")

# Procesamiento de texto con spaCy
def procesar_texto_spacy(texto):
    doc = nlp(str(texto).lower())
    tokens = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
    return " ".join(tokens)

df["texto_limpio"] = df["review_text"].astype(str).apply(procesar_texto_spacy)

# Convertir etiquetas TX dimension a lista
df["etiquetas"] = df["TX dimension"].dropna().apply(lambda x: [i.strip() for i in x.split(",")])
df = df[df["etiquetas"].notna()]  # Eliminar filas sin etiquetas

# Vectorización de etiquetas (binaria)
mlb = MultiLabelBinarizer()
Y = mlb.fit_transform(df["etiquetas"])

# División de datos
X_train, X_test, y_train, y_test = train_test_split(
    df["texto_limpio"], Y, test_size=0.2, random_state=42
)

# Pipeline con clasificación multietiqueta
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("clf", MultiOutputClassifier(LogisticRegression(max_iter=1000)))
])

# Entrenamiento
pipeline.fit(X_train, y_train)

# Predicción y evaluación
y_pred = pipeline.predict(X_test)
print(classification_report(y_test, y_pred, target_names=mlb.classes_))

# Guardar modelo y binarizador
joblib.dump(pipeline, "modelo_multietiqueta_logreg.pkl")
joblib.dump(mlb, "binarizador_etiquetas.pkl")
