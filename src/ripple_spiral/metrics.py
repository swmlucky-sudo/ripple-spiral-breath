from __future__ import annotations
from dataclasses import dataclass
import math
from typing import List


@dataclass
class DriftConfig:
    # How many recent turns to inspect
    window: int = 8

    # Weighting for drift score
    w_len_growth: float = 0.6
    w_repeat: float = 0.4

    # Threshold above which we consider the system “drifting”
    drift_threshold: float = 1.2


@dataclass
class DriftSnapshot:
    drift_score: float
    len_growth: float
    repeat_ratio: float


class DriftMetrics:
    """
    Lightweight drift scoring using only text.
    No embeddings, no external deps.
    """

    def __init__(self, cfg: DriftConfig | None = None) -> None:
        self.cfg = cfg or DriftConfig()

    def compute(self, outputs: List[str]) -> DriftSnapshot:
        outs = outputs[-self.cfg.window :]
        if len(outs) < 2:
            return DriftSnapshot(drift_score=0.0, len_growth=0.0, repeat_ratio=0.0)

        lengths = [max(1, len(x)) for x in outs]
        # simple growth ratio: last / median
        median = sorted(lengths)[len(lengths)//2]
        len_growth = lengths[-1] / max(1, median)

        # repetition heuristic: token overlap with previous
        prev = outs[-2]
        cur = outs[-1]
        repeat_ratio = self._repeat_ratio(prev, cur)

        drift_score = (
            self.cfg.w_len_growth * math.log(max(1e-6, len_growth))
            + self.cfg.w_repeat * repeat_ratio
        )

        return DriftSnapshot(
            drift_score=drift_score,
            len_growth=len_growth,
            repeat_ratio=repeat_ratio,
        )

    def is_drifting(self, snap: DriftSnapshot) -> bool:
        return snap.drift_score >= self.cfg.drift_threshold

    @staticmethod
    def _repeat_ratio(a: str, b: str) -> float:
        # word-level overlap (cheap, language-agnostic-ish)
        aw = set(a.split())
        bw = set(b.split())
        if not aw or not bw:
            return 0.0
        inter = len(aw & bw)
        return inter / max(1, len(bw))
