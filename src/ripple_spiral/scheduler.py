from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class SchedulerConfig:
    # force exhale after N turns
    exhale_every_n_turns: int = 8

    # if drift detected, exhale immediately
    exhale_on_drift: bool = True

    # if guard fails, exhale + hard reset
    exhale_on_guard_fail: bool = True


@dataclass
class ScheduleDecision:
    should_exhale: bool
    reason: Optional[str]


class BreathScheduler:
    def __init__(self, cfg: SchedulerConfig | None = None) -> None:
        self.cfg = cfg or SchedulerConfig()

    def decide(self, *, turn_index: int, drifting: bool, guard_failed: bool) -> ScheduleDecision:
        if guard_failed and self.cfg.exhale_on_guard_fail:
            return ScheduleDecision(True, "guard_fail")

        if drifting and self.cfg.exhale_on_drift:
            return ScheduleDecision(True, "drift")

        if self.cfg.exhale_every_n_turns > 0 and (turn_index % self.cfg.exhale_every_n_turns == 0):
            return ScheduleDecision(True, "periodic")

        return ScheduleDecision(False, None)
