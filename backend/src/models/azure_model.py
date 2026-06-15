from __future__ import annotations

from typing import List, Dict

from src.models.base_model import BaseAnalysisModel
from src.models import azure_client


class AzureAnalysisModel(BaseAnalysisModel):
    name = "azure"

    def __init__(self):
        # No heavy initialization: el cliente de Azure se crea por llamada
        pass

    def extract_aspects(self, text: str) -> List[Dict[str, str]]:
        """
        Usa la API de Azure Text Analytics para extraer aspectos, opiniones y sentimientos.
        Devuelve una lista de dicts con las claves: `aspect`, `opinion`, `sentiment`.
        """
        if not isinstance(text, str) or not text.strip():
            return []

        # Llamamos al analizador de Azure. La función espera una lista de documentos.
        results = azure_client.analyze_sentiments_and_opinions([text])
        if not results:
            return []

        overall_sentiment, mined = results[0]

        parsed: List[Dict[str, str]] = []
        if mined and mined != "":
            # mined tiene formato: "aspect(opinion|sentiment), aspect2(opinion2|sentiment2)"
            parts = [p.strip() for p in mined.split(",") if p.strip()]
            for part in parts:
                # Buscar 'aspect(opinion|sentiment)'
                try:
                    before_paren, inside = part.split("(", 1)
                    inside = inside.rstrip(")")
                    if "|" in inside:
                        opinion_text, senti = inside.rsplit("|", 1)
                    else:
                        opinion_text, senti = inside, overall_sentiment

                    aspect_text = before_paren.strip()
                    parsed.append({
                        "aspect": aspect_text,
                        "opinion": opinion_text.strip(),
                        "sentiment": senti.strip()
                    })
                except Exception:
                    # Si el parse falla, lo tratamos como mención general
                    parsed.append({"aspect": "general", "opinion": mined, "sentiment": overall_sentiment})
        else:
            # Si no hay aspectos minados, devolvemos la polaridad general como mención
            parsed.append({"aspect": "general", "opinion": "", "sentiment": overall_sentiment})

        return parsed
