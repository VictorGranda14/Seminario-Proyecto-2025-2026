import joblib
import numpy as np
import pandas as pd

# Cargar binarizador y modelo entrenado
mlb = joblib.load("binarizador_etiquetas.pkl")
modelo = joblib.load("modelo_multietiqueta_logreg.pkl")

# Cargar los datos usados en entrenamiento
df = pd.read_excel("./datos_etiquetados/V_XIII_es_con_TX.xlsx")

# Convertir TX dimension a listas
df["etiquetas"] = df["TX dimension"].dropna().apply(lambda x: [i.strip() for i in x.split(",")])
df = df[df["etiquetas"].notna()]  # Eliminar filas sin etiquetas

# Vectorizar etiquetas con el binarizador ya entrenado
Y = mlb.transform(df["etiquetas"])

# Calcular frecuencia de cada etiqueta
frecuencia = dict(zip(mlb.classes_, np.sum(Y, axis=0)))

# Mostrar etiquetas ordenadas por frecuencia
print("\nFrecuencia de aparición de cada dimensión TX:")
for etiqueta, freq in sorted(frecuencia.items(), key=lambda x: x[1]):
    print(f"{etiqueta}: {freq} ejemplos")
