"""Lectura centralizada de configuración declarativa JSON."""
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Settings:
    project_root: Path
    config: dict[str, Any]
    months: list[dict[str, Any]]
    category_rules: dict[str, Any]

    @classmethod
    def load(cls, project_root: Path, config_dir: Path, data_dir: Path) -> "Settings":
        def read_json(path: Path):
            with path.open(encoding="utf-8") as handle:
                return json.load(handle)

        config = read_json(config_dir / "etl.json")
        months = read_json(data_dir / "months.json")
        category_rules = read_json(data_dir / "category_rules.json")
        return cls(project_root.resolve(), config, months, category_rules)

    def project_path(self, relative: str) -> Path:
        return self.project_root / relative
