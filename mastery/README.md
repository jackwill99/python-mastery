# Python Mastery: The Senior Architect's Playbook 🐍

### From NestJS/Flutter to Enterprise Python 3.12+

This repository is a comprehensive, 20-file curriculum designed for Senior Developers transitioning from **TypeScript (NestJS)** or **Dart (Flutter)** to the Python ecosystem. It bypasses the "basics" and focuses on high-performance, resource-efficient, and scalable architectural patterns.

---

## 🏗️ Architectural Philosophy

In this curriculum, we move away from the "Opinionated Framework" mindset of NestJS and embrace Python's "Explicit is better than Implicit" philosophy. Key focus areas include:

- **Type Safety:** Leveraging `Protocols` (Structural Typing) and `Pydantic V2` for runtime validation.
- **Concurrency:** Navigating the GIL using `AsyncIO` for I/O-bound tasks and `ProcessPoolExecutor` for CPU-bound loads.
- **Memory Efficiency:** Using `__slots__` and specialized data structures to optimize RAM in high-throughput services.
- **Decoupling:** Implementing the **Repository Pattern** and **Dependency Injection** to ensure the core logic is framework-agnostic.

---

## 🗺️ Curriculum Roadmap

| Module    | Topic              | Key Senior Concept                                                               |
| :-------- | :----------------- | :------------------------------------------------------------------------------- |
| **01-03** | **Core Mastery**   | EAFP vs LBYL, Structural Typing (Protocols), Metaprogramming.                    |
| **04-05** | **Performance**    | Bypassing the GIL, Pydantic V2 internals, Memory optimization.                   |
| **06-07** | **System Design**  | FastAPI Standards, Dependency Injection Containers.                              |
| **08-10** | **Data & Tasks**   | SQLAlchemy 2.0 (Async), Advanced Decorators, Distributed Task Queues.            |
| **11-14** | **Reliability**    | Pytest Fixtures, Structured Logging (JSON), OAuth2/RBAC, Config Management.      |
| **15-20** | **Infrastructure** | Packaging (UV/Poetry), CI/CD (Ruff/Mypy), Distributed Tracing, Event-Driven EDA. |

---

## 🚀 Getting Started

This project uses **Python 3.12** features. It is recommended to use `uv` or `poetry` for dependency management.

1. **Clone the repo:**
   ```bash
   git clone [https://github.com/jackwill99/python-mastery.git](https://github.com/jackwill99/python-mastery.git)
   ```
