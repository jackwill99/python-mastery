from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

# Senior Pro-Tip: Like NestJS ConfigService or Dart const environments, pydantic-settings gives typed env parsing; cache a singleton to avoid repeated parsing.


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__")

    app_name: str = "python-service"
    stage: str = "dev"
    database_url: str = "postgresql://localhost/app"
    secrets_path: str | None = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # cached singleton


def main() -> None:
    settings = get_settings()
    print(settings)


if __name__ == "__main__":
    main()

