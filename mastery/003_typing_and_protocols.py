from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

# Pro-Tip: Like TS `interface` + NestJS providers, Protocols give structural typing; metaclasses enforce constraints at class creation (think NestJS decorators or Dart annotations but executed at import).


class PluginMeta(type):
    """Metaclass that enforces plugin contract at definition time and registers implementations."""

    registry: dict[str, type["BasePlugin"]] = {}

    def __new__(mcls, name: str, bases: tuple[type, ...], ns: dict[str, object]):
        cls = super().__new__(mcls, name, bases, ns)
        plugin_name = getattr(cls, "plugin_name", None)
        if plugin_name and plugin_name in mcls.registry:
            raise ValueError(f"Duplicate plugin_name '{plugin_name}' for {name}")
        if plugin_name:
            mcls.registry[plugin_name] = cls  # register for dynamic lookup
        return cls


@runtime_checkable
class BasePlugin(Protocol):
    plugin_name: str

    def render(self, payload: dict[str, object]) -> str: ...


@dataclass
class MarkdownPlugin(metaclass=PluginMeta):
    plugin_name: str = "markdown"

    def render(self, payload: dict[str, object]) -> str:
        title = payload.get("title", "Untitled")
        body = payload.get("body", "")
        return f"# {title}\n\n{body}"


@dataclass
class HtmlPlugin(metaclass=PluginMeta):
    plugin_name: str = "html"

    def render(self, payload: dict[str, object]) -> str:
        title = payload.get("title", "Untitled")
        body = payload.get("body", "")
        return f"<h1>{title}</h1><p>{body}</p>"


def render_with_plugin(name: str, payload: dict[str, object]) -> str:
    cls = PluginMeta.registry[name]
    plugin: BasePlugin = cls()  # satisfies Protocol structurally
    return plugin.render(payload)


def discover_plugins() -> list[str]:
    return sorted(PluginMeta.registry.keys())


if __name__ == "__main__":
    print("Plugins registered:", discover_plugins())
    print(render_with_plugin("markdown", {"title": "Hello", "body": "from metaclasses"}))
    print(render_with_plugin("html", {"title": "Hello", "body": "from Protocols"}))
