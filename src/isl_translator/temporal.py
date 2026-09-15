"""Temporal smoothing for noisy frame-level sign detections."""
from __future__ import annotations

import time
from collections import defaultdict


class TemporalSignBuffer:
    def __init__(self, interval: float = 1.0, max_signs: int = 5, min_votes: int = 2) -> None:
        self.interval = interval
        self.max_signs = max_signs
        self.min_votes = min_votes
        self.reset()

    def reset(self) -> None:
        self._started = time.monotonic()
        self._votes: dict[str, float] = defaultdict(float)
        self._counts: dict[str, int] = defaultdict(int)
        self.sequence: list[str] = []

    def add(self, label: str, confidence: float = 1.0) -> None:
        self._votes[label] += max(0.0, float(confidence))
        self._counts[label] += 1

    def ready(self, now: float | None = None) -> bool:
        return (now or time.monotonic()) - self._started >= self.interval

    def commit(self, now: float | None = None) -> str | None:
        if not self.ready(now):
            return None
        selected = None
        if self._votes:
            candidates = sorted(self._votes, key=lambda k: (self._votes[k], self._counts[k]), reverse=True)
            for label in candidates:
                if self._counts[label] >= self.min_votes or len(self._votes) == 1:
                    selected = label
                    break
        self._votes.clear()
        self._counts.clear()
        self._started = now or time.monotonic()
        if selected and (not self.sequence or self.sequence[-1] != selected):
            self.sequence.append(selected)
            self.sequence = self.sequence[-self.max_signs :]
        return selected

    def snapshot(self) -> list[str]:
        return list(self.sequence)
