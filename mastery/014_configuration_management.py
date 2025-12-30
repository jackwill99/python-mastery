from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Pro-Tip: Like NestJS ConfigService or Dart's const-from-environment, prefer typed config objects sourced from env + TOML/YAML with overrides per stage.


@dataclass(frozen=True)
class Settings:
    stage: str
    db_url: str
    api_host: str
    secret_key: str
    extra: dict[str, Any]

    @classmethod
    def load(cls, *, stage: str | None = None, pyproject: Path = Path("pyproject.toml")) -> "Settings":
        stage = stage or os.getenv("APP_STAGE", "dev")
        db_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
        api_host = os.getenv("API_HOST", "http://localhost:8000")
        secret_key = os.getenv("APP_SECRET", "dev-secret")
        extra = {}
        if pyproject.exists():
            data = tomllib.loads(pyproject.read_text())
            extra = data.get("tool", {}).get("app", {}).get("overrides", {}).get(stage, {})
        return cls(stage=stage, db_url=db_url, api_host=api_host, secret_key=secret_key, extra=extra)


def main() -> None:
    settings = Settings.load()
    print("Settings:", settings)


if __name__ == "__main__":
    main()

# Pythonic backend problem solved: Single source of truth for config with environment overrides; easy to inject into FastAPI/CLIs without globals.
