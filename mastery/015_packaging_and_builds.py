from __future__ import annotations

pyproject_poetry = """\
[tool.poetry]
name = "python-service"
version = "0.1.0"
description = "Example production service"
authors = ["You <you@example.com>"]
readme = "README.md"
packages = [{ include = "python_service" }]

[tool.poetry.dependencies]
python = "^3.12"
fastapi = "^0.110"
uvicorn = { extras = ["standard"], version = "^0.29" }

[tool.poetry.group.dev.dependencies]
ruff = "^0.5"
mypy = "^1.10"
pytest = "^8.0"
pytest-asyncio = "^0.23"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""

pyproject_uv = """\
[project]
name = "python-service"
version = "0.1.0"
description = "Example production service"
requires-python = ">=3.12"
dependencies = [
  "fastapi>=0.110",
  "uvicorn[standard]>=0.29",
]

[tool.uv]
dev-dependencies = [
  "ruff>=0.5",
  "mypy>=1.10",
  "pytest>=8.0",
  "pytest-asyncio>=0.23",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""

# Senior Pro-Tip: Poetry/uv group deps mirror npm/yarn workspaces dev/prod split; wheels (bdist_wheel) are the Python equivalent of npm pack artifacts.

if __name__ == "__main__":
    print("Poetry template:\n", pyproject_poetry)
    print("\nuv template:\n", pyproject_uv)

