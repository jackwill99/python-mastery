from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

# Pro-Tip: In Node/Dart you'd stream/pipe or await file reads; Python favors context managers + iterators with match-case for clarity.

@dataclass(frozen=True)
class Event:
    kind: str
    user_id: str
    payload: dict[str, str]


def parse_log_line(line: str) -> Event | None:
    match line.strip().split(","):
        case [kind, user_id, raw_payload] if kind and user_id:
            payload = dict(kv.split("=") for kv in raw_payload.split(";") if "=" in kv)
            return Event(kind=kind, user_id=user_id, payload=payload)
        case _:
            return None


def load_events(path: Path) -> Iterable[Event]:
    with path.open() as fh:
        for line in fh:
            if event := parse_log_line(line):
                yield event


def summarize_events(events: Iterable[Event]) -> Counter[str]:
    return Counter(event.kind for event in events)


def top_active_users(events: Iterable[Event], *, limit: int = 3) -> list[str]:
    counts = Counter(event.user_id for event in events)
    return [user for user, _ in counts.most_common(limit)]


def main(log_path: Path) -> None:
    events = list(load_events(log_path))
    summary = summarize_events(events)
    print("Event mix:", dict(summary))
    print("Top users:", top_active_users(events))


if __name__ == "__main__":
    sample = Path("audit.log")
    if sample.exists():
        main(sample)
    else:
        print("Place a CSV-like audit.log with lines like 'LOGIN,u123,ip=1.1.1.1;device=web'")
