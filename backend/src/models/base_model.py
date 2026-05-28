from __future__ import annotations

from abc import ABC, abstractmethod


class BaseAnalysisModel(ABC):
    name = "base"

    @abstractmethod
    def extract_aspects(self, text: str):
        raise NotImplementedError
