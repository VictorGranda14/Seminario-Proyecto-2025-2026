# 🗺️ Tourism Analytics Dashboard — Seminario Proyecto 2025–2026

> **Plataforma de Análisis de Experiencia Turística basada en NLP**
> Extracción de aspectos, análisis de sentimiento y visualización interactiva de reseñas de TripAdvisor para el turismo chileno.

---

## 📋 Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Instalación y Configuración](#instalación-y-configuración)
- [Ejecución del Pipeline](#ejecución-del-pipeline)
- [API REST](#api-rest)
- [Dashboard Frontend](#dashboard-frontend)
- [Modelos de Análisis](#modelos-de-análisis)
- [Esquema de Base de Datos](#esquema-de-base-de-datos)

---

## Descripción General

Este proyecto implementa un pipeline de análisis semántico end-to-end sobre comentarios turísticos en inglés, con el objetivo de identificar fortalezas y fricciones operativas en atracciones y rubros del sector turismo en Chile.

El sistema procesa reseñas de TripAdvisor a través de tres etapas principales:

1. **Extracción y Limpieza** — Preprocesamiento de datos crudos con validación de idioma mediante `xlm-roberta-base`.
2. **Inferencia NLP** — Minería de aspectos y análisis de sentimiento con modelos locales (PyABSA + SpaCy) o en la nube (Azure Text Analytics).
3. **Agregación y Visualización** — Consolidación de métricas por atracción, rubro y país, expuestas a través de una API REST y un dashboard interactivo en Next.js.

---

## Arquitectura del Sistema

```
CSV TripAdvisor
      │
      ▼
┌─────────────────────┐
│   Data Prep (ETL)   │  script_limpieza.py · csv_a_sqlite.py
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   Inferencia NLP    │  azure_model.py · aspect_miner.py (local)
│   (Patron Strategy) │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Base de Datos      │  SQLite (analisis_crudo + metricas_consolidadas)
│  SQLite             │
└────────┬────────────┘
         │
      ┌──┴──┐
      ▼      ▼
┌─────────┐  ┌──────────────────┐
│ FastAPI │  │ Generador LLM    │  generador_resumenes.py (Ollama/qwen2.5)
│  REST   │  │ Resúmenes Ejec.  │
└────┬────┘  └──────────────────┘
     │
     ▼
┌─────────────────────┐
│  Next.js Dashboard  │  React · Recharts · shadcn/ui · Tailwind CSS
└─────────────────────┘
```

---

## Estructura del Proyecto

```
Seminario-Proyecto-2025-2026/
│
├── backend/
│   ├── api.py                        # FastAPI — endpoints REST
│   ├── main_pipeline.py              # Orquestador ETL (CSV → SQLite → Métricas)
│   ├── requirements.txt
│   └── src/
│       ├── analitica/
│       │   └── agregador.py          # Motor de consolidación de métricas por vista
│       ├── config/
│       │   └── database_init.py      # Esquema SQLite y migraciones
│       ├── data_prep/
│       │   ├── csv_a_sqlite.py       # Ingesta de CSV del LLM a SQLite
│       │   ├── generador_resumenes.py# Generación de resúmenes ejecutivos con Ollama
│       │   ├── procesamiento_semantico.py # Clustering + clasificación por categoría oficial
│       │   └── script_limpieza.py    # Pipeline de limpieza del dataset original
│       ├── models/
│       │   ├── aspect_miner.py       # Modelo local (PyABSA + SpaCy, arquitectura híbrida)
│       │   ├── azure_client.py       # Cliente Azure Text Analytics
│       │   └── azure_model.py        # Adaptador del modelo Azure
│       └── utils/
│           ├── database.py           # DBManager (conexión y operaciones SQLite)
│           ├── analysis.py           # Análisis y exportación a Excel
│           ├── convertir_a_csv.py    # Conversión Excel → CSV
│           └── eliminar_atracciones_pequeñas.py  # Filtro de atracciones con pocas reseñas
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── components/
│   │   └── dashboard/
│   │       ├── dashboard-client.tsx  # Componente raíz con manejo de estado y fetching
│   │       ├── aspect-analysis.tsx   # Gráfico de fortalezas y alertas
│   │       ├── executive-summary.tsx # Panel de resumen generado por IA
│   │       ├── macro-categorias-chart.tsx  # Gráfico de categorías oficiales
│   │       ├── sentiment-kpis.tsx    # KPIs de polaridad (positivo/neutro/negativo)
│   │       ├── summary-overview-panel.tsx  # Panel resumen nacional
│   │       ├── top-attractions-list.tsx    # Ranking de atracciones
│   │       └── tx-dimensions-chart.tsx     # Gráfico radar de dimensiones TX
│   ├── lib/
│   │   ├── backend-api.ts            # Funciones de fetching contra la API
│   │   └── dashboard-data.ts         # Datos fallback para desarrollo
│   └── package.json
│
├── data/                             # ⚠️ No subir a GitHub (.gitignore)
│   ├── raw/                          # Excel original de TripAdvisor
│   ├── processed/                    # Datasets limpios
│   └── outputs/                      # CSV del modelo LLM + SQLite
│
└── README.md
```

---

## Tecnologías Utilizadas

### Backend

| Tecnología | Uso |
|---|---|
| **Python 3.10+** | Lenguaje principal |
| **FastAPI** | API REST |
| **SQLite** | Base de datos embebida |
| **Pandas** | Manipulación de datos |
| **PyABSA** | Extracción de aspectos (ATEPC / DeBERTa) |
| **SpaCy** | Análisis gramatical y extracción de opiniones |
| **Sentence-Transformers** | Embeddings semánticos para clustering |
| **scikit-learn** | Clustering MiniBatchKMeans |
| **Azure AI Text Analytics** | Análisis de sentimiento en la nube |
| **Ollama / qwen2.5:3b** | Generación de resúmenes ejecutivos |
| **xlm-roberta-base** | Validación de idioma en limpieza |

### Frontend

| Tecnología | Uso |
|---|---|
| **Next.js 16** | Framework React con App Router |
| **TypeScript** | Tipado estático |
| **Tailwind CSS 4** | Estilos utilitarios |
| **shadcn/ui** | Componentes de interfaz |
| **Recharts** | Gráficos (radar, barras apiladas, barras horizontales) |
| **Radix UI** | Primitivas accesibles (select, popover, tabs) |

---

## Instalación y Configuración

### Prerrequisitos

- Python 3.10+
- Node.js 18+
- Ollama instalado localmente (para generación de resúmenes)

### Backend

```bash
# 1. Clonar el repositorio e ingresar al directorio
git clone <url-del-repositorio>
cd Seminario-Proyecto-2025-2026/backend

# 2. Crear y activar entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Descargar modelos de SpaCy
python -m spacy download en_core_web_sm    # Requerido
python -m spacy download es_core_news_sm   # Opcional

# 5. Configurar variables de entorno
cp .env.example .env
# Editar .env con las credenciales de Azure si se usará ese modelo
```

### Frontend

```bash
cd ../frontend
npm install
```

---

## Ejecución del Pipeline

### Paso 1 — Limpieza del Dataset Original (una sola vez)

```bash
# Desde backend/
python src/data_prep/script_limpieza.py
```

Genera `data/processed/Dataset_Limpio_Final.csv` con comentarios en inglés validados.

### Paso 2 — Inferencia NLP (modelo local o Azure)

```bash
# Modelo local (PyABSA + SpaCy) — Todo el dataset
python main.py --model local

# Modelo Azure con límite de prueba
python main.py --model azure --limit 500
```

Genera `data/outputs/output_llm.csv` con los aspectos, opiniones y sentimientos extraídos.

### Paso 3 — Procesamiento Semántico (clustering + clasificación de categorías)

```bash
python src/data_prep/procesamiento_semantico.py --database data/turismo.sqlite
```

### Paso 4 — ETL a SQLite y Agregación de Métricas

```bash
# Carga el CSV e ingesta a SQLite, luego agrega todas las vistas
python main_pipeline.py --input data/outputs/output_llm.csv --database data/turismo.sqlite

# Solo recalcular métricas (sin recargar el CSV)
python main_pipeline.py --skip-load
```

### Paso 5 — Generación de Resúmenes Ejecutivos con IA

> Requiere Ollama corriendo localmente con el modelo `qwen2.5:3b`.

```bash
ollama pull qwen2.5:3b
python src/data_prep/generador_resumenes.py
```

### Paso 6 — Levantar la API y el Dashboard

```bash
# Terminal 1 — Backend (desde backend/)
uvicorn api:app --reload --port 8000

# Terminal 2 — Frontend (desde frontend/)
npm run dev
```

El dashboard estará disponible en `http://localhost:3000`.

---

## API REST

La API expone los datos procesados almacenados en SQLite.

**Base URL:** `http://localhost:8000`

### Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/health` | Estado del servicio y ruta de la base de datos activa |
| `GET` | `/metricas` | Lista de todas las vistas disponibles (atracciones, rubros, país) |
| `GET` | `/metricas/disponibles` | Alias de `/metricas` |
| `GET` | `/metricas/{identificador_vista}` | JSON completo de métricas para una vista específica |

### Parámetros de Query

| Parámetro | Descripción | Ejemplo |
|---|---|---|
| `tipo_vista` | Filtra por tipo: `atraccion`, `rubro`, `pais` | `?tipo_vista=rubro` |
| `database` | Ruta alternativa a la base de datos SQLite | `?database=/ruta/custom.sqlite` |

### Ejemplo de Respuesta — `/metricas/{id}`

```json
{
  "identificador_vista": "cerro_san_cristobal",
  "nombre_vista": "Cerro San Cristóbal",
  "tipo_vista": "atraccion",
  "ultima_actualizacion": "2025-06-01T12:00:00Z",
  "vistaInfo": {
    "totalReviews": 342,
    "sentimentRatio": { "positive": 78, "neutral": 14, "negative": 8 }
  },
  "executiveSummary": "Con 342 opiniones y un 78% de valoraciones positivas...",
  "txDimensions": [...],
  "aspectAnalysis": {
    "strengths": [...],
    "alerts": [...]
  },
  "macroCategories": [...],
  "summaryOverview": {...}
}
```

---

## Dashboard Frontend

El dashboard presenta tres niveles de análisis accesibles mediante pestañas:

### Visión Global y Rubros

- **Panorama Nacional** — KPIs consolidados de todas las atracciones del país, ranking de top rubros y atracciones, y gráfico de dimensiones turísticas apiladas.
- **Análisis por Rubro** — Selector dinámico de rubros con resumen ejecutivo, distribución de sentimiento, categorías por impacto y fortalezas/alertas del sector.

### Análisis por Atracción

- Buscador con autocompletado sobre todas las atracciones disponibles.
- Gráfico radar de dimensiones de experiencia (positivo vs. fricciones).
- Análisis de aspectos con barras horizontales y keywords asociadas.
- Resumen ejecutivo generado por IA.

---

## Modelos de Análisis

### Modelo Local — Arquitectura Híbrida (PyABSA + SpaCy)

Implementado en `src/models/aspect_miner.py`. Combina:

- **DeBERTa (PyABSA/ATEPC)** — Detección probabilística de aspectos y su polaridad.
- **SpaCy (`en_core_web_sm`)** — Análisis de dependencias sintácticas para extracción precisa de opiniones (adjetivos y sus negaciones).
- **Red de Seguridad por Reglas** — Captura entidades críticas del dominio turístico que el modelo puede omitir (`tour`, `guide`, `wine`, `telescope`, etc.).
- **Clustering Semántico** — `MiniBatchKMeans` sobre embeddings `all-MiniLM-L6-v2` para consolidar aspectos similares.

### Modelo Azure — Azure Text Analytics

Implementado en `src/models/azure_model.py`. Utiliza:

- **Opinion Mining** — Extracción de pares `(aspecto, opinión, sentimiento)` a nivel de oración.
- **Clasificación Multietiqueta** — Asignación de dimensiones TX mediante un modelo custom desplegado en Azure Language Studio.

### Categorías Oficiales de Análisis

Los aspectos se clasifican en 13 categorías estandarizadas para el análisis turístico:

`Local Culture and History` · `Variety of Activities` · `Hospitality` · `Infrastructure` · `Environment Management` · `Accessibility` · `Quality of Service` · `Physiography` · `Price` · `Visitor Management` · `Weather` · `Food` · `Safety`

---

## Esquema de Base de Datos

### Tabla `analisis_crudo`

Almacena cada aspecto extraído por el modelo, desagregado por comentario.

| Columna | Tipo | Descripción |
|---|---|---|
| `id_registro` | INTEGER PK | Identificador único autoincremental |
| `id_comentario` | TEXT | ID original del comentario fuente |
| `atraccion` | TEXT | Nombre de la atracción turística |
| `rubro` | TEXT | Categoría comercial de la atracción |
| `texto_original` | TEXT | Texto completo de la reseña |
| `modelo_usado` | TEXT | Modelo NLP utilizado (`azure`, `local`, etc.) |
| `polaridad_general_comentario` | TEXT | Sentimiento global del comentario |
| `aspecto_detectado` | TEXT | Aspecto extraído (ej. `guide`, `view`) |
| `opinion_detectada` | TEXT | Adjetivo asociado al aspecto |
| `polaridad_aspecto` | TEXT | Sentimiento del aspecto (`positive`, `negative`) |
| `dimension_tx` | TEXT | Dimensiones TX asignadas (lista serializada) |

### Tabla `metricas_consolidadas`

Almacena el JSON de métricas precalculadas por vista (atracción, rubro o país).

| Columna | Tipo | Descripción |
|---|---|---|
| `identificador_vista` | TEXT PK | Slug normalizado (ej. `cerro_san_cristobal`) |
| `nombre_vista` | TEXT | Nombre legible para el dashboard |
| `tipo_vista` | TEXT | `atraccion` · `rubro` · `pais` |
| `json_completo` | TEXT | Payload JSON completo para el frontend |
| `ultima_actualizacion` | TIMESTAMP | Fecha de último cálculo |

---

## Variables de Entorno

Crear un archivo `.env` en `backend/` basándose en `.env.example`:

```env
# Azure Language Service (requerido solo para --model azure)
AZURE_LANGUAGE_ENDPOINT=https://<tu-recurso>.cognitiveservices.azure.com/
AZURE_LANGUAGE_KEY=<tu-clave-secreta>

# Backend API (opcional)
BACKEND_DB_PATH=data/turismo.sqlite
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

---

> **Nota:** La carpeta `data/` y el archivo `.env` están excluidos del repositorio via `.gitignore`. Nunca subas datos sensibles ni credenciales de API a Git.
