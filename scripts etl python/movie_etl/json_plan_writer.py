"""Publica el conjunto de datos JSON consultado por la aplicación React."""
import json
import math
from pathlib import Path


class JsonPlanWriter:
    def write(self, plan: list[dict], destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", encoding="utf-8") as handle:
            json.dump(self._normalize(plan), handle, ensure_ascii=False, indent=2, allow_nan=False)

    @staticmethod
    def _normalize(value):
        if hasattr(value, "item"):
            value = value.item()
        if isinstance(value, float) and math.isnan(value):
            return None
        if isinstance(value, dict):
            return {key: JsonPlanWriter._normalize(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [JsonPlanWriter._normalize(item) for item in value]
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        raise TypeError(f"Tipo no serializable en JSON: {type(value).__name__}")
