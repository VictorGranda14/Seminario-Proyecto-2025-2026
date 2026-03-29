import json
from pathlib import Path

# rutas
JSONL_PATH = "C:\\Users\\ramiro\\Seminario-Proyecto-2025-2026\\data\\comentarios_etiquetados\\datos_etiquetados.jsonl"      # tu archivo original
TXT_DIR = Path("C:\\Users\\ramiro\\Seminario-Proyecto-2025-2026\\data\\comentarios_txt")            # carpeta local donde se generarán los .txt
OUTPUT_JSON = "labels.json"           # archivo que Azure va a importar

TXT_DIR.mkdir(exist_ok=True)

all_classes = set()
documents = []

with open(JSONL_PATH, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        obj = json.loads(line)

        doc_id = str(obj["id"])
        text = obj["text"]
        labels = obj["labels"]  # lista de strings

        # 1) crear archivo .txt
        filename = f"{doc_id}.txt"
        with open(TXT_DIR / filename, "w", encoding="utf-8") as out:
            out.write(text)

        # acumular clases
        for lab in labels:
            all_classes.add(lab)

        # 2) entrada para 'documents'
        documents.append({
            "location": filename,
            "language": "es",
            "dataset": "Train",
            "classes": [{"category": lab} for lab in labels]
        })

# armar estructura final para Azure
labels_json = {
    "projectFileVersion": "2022-05-01",
    "stringIndexType": "Utf16CodeUnit",
    "metadata": {
        "projectKind": "CustomMultiLabelClassification",
        "storageInputContainerName": "datos-etiquetados",  # NOMBRE del contenedor en Azure
        "projectName": "ClasificadorTesis",
        "multilingual": False,
        "description": "Clasificador multietiqueta de reseñas",
        "language": "es"
    },
    "assets": {
        "projectKind": "CustomMultiLabelClassification",
        "classes": [{"category": c} for c in sorted(all_classes)],
        "documents": documents
    }
}

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(labels_json, f, ensure_ascii=False, indent=2)

print("Listo. Generados .txt en", TXT_DIR, "y labels.json para importar en Azure.")
