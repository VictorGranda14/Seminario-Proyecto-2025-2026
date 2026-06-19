## Estructura del Proyecto

```text
Seminario-Proyecto-2025-2026/
│
├── data/                   # NO subir a GitHub (añadir al .gitignore)
│   ├── raw/                # CSV original de TripAdvisor
│   ├── processed/          # Datos limpios listos para inferencia
│   └── outputs/            # JSONs exportados para el dashboard interactivo
│
├── notebooks/              # Jupyter notebooks para pruebas rápidas o EDA
│
├── src/
│   ├── config/             # Variables de entorno y mapeos
│   │   └── settings.py     # Rutas de carpetas, credenciales de Azure, etc.
│   │
│   ├── data_prep/          # Pipeline ETL y limpieza estandarizada
│   │   └── cleaner.py      # Separación de respuestas, detección de idioma
│   │
│   ├── models/             # Patrón Strategy para la inferencia
│   │   ├── base_model.py   # Interfaz/Clase padre (AnalizadorBase)
│   │   ├── azure_model.py  # Conexión a la API de Microsoft Azure
│   │   ├── local_model.py  # Arquitectura Híbrida (PyABSA + SpaCy)
│   │   └── slm_model.py    # Futura implementación SLM
│   │
│   ├── summarization/      # Generación de resúmenes ejecutivos
│   │   └── generator.py
│   │
│   └── utils/
│       └── exporter.py     # Conversión de DataFrames a JSON
│
├── .env.example            # Plantilla de variables de entorno (claves API)
├── .gitignore              # Archivos a ignorar (data/, .env, venv/, etc.)
├── requirements.txt        # Dependencias del proyecto
└── main.py                 # Orquestador principal (CLI)
```
## Instalación y dependencias

1. Clonar el repositorio e ingresar a la carpeta.
2. Crear y activar un entorno virtual aislando las dependencias: 
```text
# En Windows
   python -m venv venv
   venv\Scripts\activate
# En macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
```
3. Instalar las dependencias del proyecto:
```text
pip install -r requirements.txt
```
4. Descargar los modelos lingüísticos base para SpaCy:
```text
# Modelo para análisis en inglés (Requerido para NLP general)
   python -m spacy download en_core_web_sm
   
# Modelo para análisis en español (Opcional, según requerimientos de idioma)
   python -m spacy download es_core_news_sm
```

## Ejecución

El pipeline de análisis se orquesta a través del archivo "main.py" utilizando argumentos por consola para seleccionar el comportamiento sin modificar el código fuente.

Opciones disponibles:

- model: Define la arquitectura a utilizar (azure, local, slm).

- limit: (Opcional) Limita la cantidad de filas a procesar para realizar pruebas rápidas y evitar consumos innecesarios de API.

### Ejemplos 
- Ejecutar el modelo local con todo el dataset:
```text
python main.py --model local
```
- Ejecutar el modelo de Azure con un límite de prueba (ej. 500 comentarios):
```text
python main.py --model azure --limit 500
```