# Seminario-Proyecto-2025-2026

Seminario_Proyecto/
│
├── data/                   # ALMACENAMIENTO DE DATOS (No se sube a GitHub)
│   ├── raw/                # El Excel original con los 560.000 comentarios crudos.
│   ├── processed/          # El dataset limpio de 153.446 filas (ej. parquet o sqlite).
│   └── outputs/            # Resultados finales: resúmenes, extracciones ABSA y dimensiones.
│
├── notebooks/              # ENTORNOS DE PRUEBA
│   ├── 01_exploracion.ipynb# Análisis exploratorio inicial (EDA).
│   └── 02_pruebas_absa.ipynb# Pruebas aisladas para PyABSA antes de pasarlo a producción.
│
├── src/                    # CÓDIGO FUENTE (Módulos del pipeline)
│   ├── __init__.py
│   ├── data_prep/          # Fase 1
│   │   ├── cleaning.py     # Lógica de eliminación de nulos, dueños y duplicados.
│   │   └── lang_filter.py  # Script que usa xlm-roberta-base para filtrar inglés.
│   ├── models/             # Fase 2 y 3
│   │   ├── aspect_miner.py # Implementación de PyABSA.
│   │   └── tx_classifier.py# Tu modelo multietiqueta (Dimensiones TX).
│   ├── summarization/      # Fase 4
│   │   └── generator.py    # Generación de resúmenes (Data-to-Text).
│   └── utils/              # Utilidades compartidas
│       ├── database.py     # Conexiones a SQLite/Parquet para guardado incremental.
│       └── logger.py       # Configuración para registrar errores y progreso del bucle.
│
├── main.py                 # ORQUESTADOR: Une todas las fases de 'src' y ejecuta el bucle.
├── requirements.txt        # Dependencias (pandas, pyabsa, transformers, openpyxl, etc.).
├── .env                    # Variables de entorno (paths, configuraciones de ejecución).
└── .gitignore              # Archivos a ignorar (.env, carpeta data/, __pycache__).



PyABSA (ATEPC) no escupe la palabra "good" aislada, utilizamos las posiciones de los tokens para capturar el texto que rodea al aspecto (3 palabras antes y 3 después). Esto captura perfectamente modificadores como "definitely not good".

pip install pyabsa
pip install protobuf tiktoken sentencepiece