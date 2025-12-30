from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

# Pro-Tip: Instead of dotenv + process.env (Node) or const String.fromEnvironment (Dart),
# use tomllib + os.environ with typed fallbacks for safer config.

Stage = Literal["dev", "staging", "prod"]


@dataclass(frozen=True)
class AppConfig:
    stage: Stage
    app_name: str
    version: str
    db_url: str
    debug: bool


def load_pyproject_version(pyproject_path: Path = Path("pyproject.toml")) -> str:
    if not pyproject_path.exists():
        return "0.0.0"
    data = tomllib.loads(pyproject_path.read_text())
    return data.get("project", {}).get("version", "0.0.0")


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    return raw.lower() in {"1", "true", "yes"} if raw else default


def resolve_config(stage: Stage | None = None) -> AppConfig:
    stage = stage or os.environ.get("APP_STAGE", "dev")  # type: ignore[assignment]
    db_url = os.environ.get("DATABASE_URL", "postgresql://localhost/app")
    return AppConfig(
        stage=stage,  # type: ignore[arg-type]
        app_name=os.environ.get("APP_NAME", "python-service"),
        version=load_pyproject_version(),
        db_url=db_url,
        debug=env_bool("APP_DEBUG", default=stage == "dev"),
    )


if __name__ == "__main__":
    cfg = resolve_config()
    print(cfg)

