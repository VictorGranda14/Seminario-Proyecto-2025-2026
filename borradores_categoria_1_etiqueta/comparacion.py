import pandas as pd
import joblib
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split
import spacy

# Cargar el modelo spaCy
nlp = spacy.load("es_core_news_sm")

# Preprocesamiento spaCy
def procesar_texto_spacy(texto):
    doc = nlp(texto.lower())
    tokens = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
    return " ".join(tokens)

# Cargar el dataset original
df = pd.read_excel("V_es_categorizado.xlsx")
df["texto_limpio"] = df["review_text"].astype(str).apply(procesar_texto_spacy)

# Dividir los datos
X = df["texto_limpio"]
y = df["categoria"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Cargar los modelos entrenados
modelo_log = joblib.load("modelos_entrenados/modelo_logistic_regression_para_categorias.pkl")
modelo_rf = joblib.load("modelos_entrenados/modelo_random_forest_para_categorias.pkl")

# Predecir con ambos modelos
y_pred_log = modelo_log.predict(X_test)
y_pred_rf = modelo_rf.predict(X_test)

# Mostrar resultados
print("=== Regresión Logística ===")
print(classification_report(y_test, y_pred_log))
print("Accuracy:", accuracy_score(y_test, y_pred_log))

print("\n=== Random Forest ===")
print(classification_report(y_test, y_pred_rf))
print("Accuracy:", accuracy_score(y_test, y_pred_rf))
