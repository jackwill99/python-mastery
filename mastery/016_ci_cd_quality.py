from __future__ import annotations

import subprocess

# Pro-Tip: Like GitHub Actions or GitLab CI running eslint+tests, wire Ruff/pytest/mypy as fast feedback; fail-fast keeps pipelines lean.


def run_step(name: str, cmd: list[str]) -> None:
    print(f":: Running {name}")
    subprocess.run(cmd, check=True)


def main() -> None:
    steps = [
        ("format-check", ["ruff", "format", "--check", "."]),
        ("lint", ["ruff", "check", "."]),
        ("types", ["python", "-m", "mypy", "."]),
        ("tests", ["python", "-m", "pytest", "-q"]),
    ]
    for name, cmd in steps:
        run_step(name, cmd)
    print("CI pipeline succeeded")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"Pipeline failed at step: {exc.cmd}")

# Pythonic backend problem solved: Single script to mirror CI locally; swap tools/flags easily without editing YAML pipelines.
