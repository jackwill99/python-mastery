from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Generic, Literal, TypedDict, TypeVar

# Pro-Tip: In NestJS/Flutter you might wire dotenv + const-from-environment; Python leans on pyproject.toml as a single manifest (build, deps, settings) instead of a loose requirements.txt.

Stage = Literal["dev", "staging", "prod"]
TStage = TypeVar("TStage", bound=Stage)


class RawAppConfig(TypedDict, total=False):
    stage: Stage
    app_name: str
    version: str
    db_url: str
    debug: bool
    payment_gateway_url: str


@dataclass(frozen=True)
class AppConfig(Generic[TStage]):
    stage: TStage
    app_name: str
    version: str
    db_url: str
    debug: bool
    payment_gateway_url: str


def load_pyproject(pyproject_path: Path = Path("pyproject.toml")) -> dict:
    if not pyproject_path.exists():
        return {}
    return tomllib.loads(pyproject_path.read_text())


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    return raw.lower() in {"1", "true", "yes"} if raw else default


def resolve_config(stage: Stage | None = None, *, pyproject_path: Path = Path("pyproject.toml")) -> AppConfig[Stage]:
    stage_value: Stage = stage or os.environ.get("APP_STAGE", "dev")  # type: ignore[assignment]
    pyproject = load_pyproject(pyproject_path)
    project_meta = pyproject.get("project", {})
    tool_cfg: RawAppConfig = (
        pyproject.get("tool", {}).get("app", {}).get("env", {}).get(stage_value, {})  # type: ignore[assignment]
    )

    raw: RawAppConfig = {
        "stage": stage_value,
        "app_name": os.environ.get("APP_NAME", project_meta.get("name", "python-service")),
        "version": project_meta.get("version", "0.0.0"),
        "db_url": os.environ.get("DATABASE_URL", tool_cfg.get("db_url", "postgresql://localhost/app")),
        "debug": env_bool("APP_DEBUG", default=tool_cfg.get("debug", stage_value == "dev")),
        "payment_gateway_url": os.environ.get(
            "PAYMENT_GATEWAY_URL", tool_cfg.get("payment_gateway_url", "https://sandbox.payments.local")
        ),
    }

    return AppConfig(
        stage=raw["stage"],
        app_name=raw["app_name"],
        version=raw["version"],
        db_url=raw["db_url"],
        debug=raw["debug"],
        payment_gateway_url=raw["payment_gateway_url"],
    )


def main() -> None:
    cfg = resolve_config()
    print(cfg)
    print("Tip: pyproject.toml centralizes metadata + deps; requirements.txt cannot express build backends or tool settings.")


if __name__ == "__main__":
    main()
