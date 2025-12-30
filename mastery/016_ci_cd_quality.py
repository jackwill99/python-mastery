github_actions_yaml = """\
name: ci

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install ruff mypy pytest pytest-asyncio
          pip install -e .
      - name: Ruff
        run: ruff check .
      - name: MyPy
        run: mypy .
      - name: Pytest
        run: pytest -q
"""

# Senior Pro-Tip: Similar to GitHub Actions for Node (eslint/jest), but pin the Python version and cache deps if runs slow; keep CI steps minimal and fail-fast.

if __name__ == "__main__":
    print(github_actions_yaml)

