from __future__ import annotations

import subprocess
from pathlib import Path

# Pro-Tip: Similar to `npm pack` or Flutter build, Python packages are defined in pyproject.toml; build wheels via `python -m build` or `hatch build`.


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def ensure_pyproject() -> None:
    pyproject = Path("pyproject.toml")
    if not pyproject.exists():
        pyproject.write_text(
            "[project]\nname = 'python-service'\nversion = '0.1.0'\ndescription = 'Example service'\nrequires-python = '>=3.12'\n"
        )


def build() -> None:
    ensure_pyproject()
    run(["python", "-m", "pip", "install", "--upgrade", "build"])
    run(["python", "-m", "build"])


if __name__ == "__main__":
    print("Building sdist and wheel...")
    try:
        build()
    except subprocess.CalledProcessError as exc:
        print("Build failed:", exc)

# Pythonic backend problem solved: Reproducible builds via wheels/sdists; swap backend (hatchling/poetry) by editing pyproject, no code changes.
