from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from .adapters import LLMAdapter
from .metrics import DriftMetrics, DriftSnapshot
from .guards import GuardSuite, GuardResult
from .scheduler import BreathScheduler, ScheduleDecision


@dataclass
class BreathState:
    turn: int = 0
    prompts: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    last_drift: DriftSnapshot | None = None
    last_guard: GuardResult | None = None

    # a place to store your internal logs (you can persist to file)
    internal_log: List[Dict[str, Any]] = field(default_factory=list)


class BreathLoop:
    """
    Orchestrates:
    - generate()
    - drift metrics
    - guard checks
    - scheduler decision
    - exhale reset (state cleanup)
    """

    def __init__(
        self,
        adapter: LLMAdapter,
        *,
        drift: DriftMetrics,
        guards: GuardSuite,
        scheduler: BreathScheduler,
    ) -> None:
        self.adapter = adapter
        self.drift = drift
        self.guards = guards
        self.scheduler = scheduler
        self.state = BreathState()

    def step(self, user_prompt: str, *, meta: Dict[str, Any] | None = None) -> str:
        self.state.turn += 1
        self.state.prompts.append(user_prompt)

        out = self.adapter.generate(user_prompt, meta=meta or {})
        self.state.outputs.append(out)

        # compute drift
        drift_snap = self.drift.compute(self.state.outputs)
        self.state.last_drift = drift_snap
        drifting = self.drift.is_drifting(drift_snap)

        # guard checks
        guard_res = self.guards.check(out)
        self.state.last_guard = guard_res
        guard_failed = guard_res.fail_reason is not None

        # schedule decision
        decision = self.scheduler.decide(
            turn_index=self.state.turn,
            drifting=drifting,
            guard_failed=guard_failed,
        )

        # internal log
        self._log(out, drift_snap, guard_res, decision)

        # exhale if needed
        if decision.should_exhale:
            self.exhale(reason=decision.reason)

        return out

    def exhale(self, *, reason: Optional[str] = None) -> None:
        """
        MVP exhale:
        - Keep last few turns summarized? Here we just truncate buffers.
        - Reset guard counters
        """
        # Keep last 2 turns for continuity; drop the rest
        keep = 2
        self.state.prompts = self.state.prompts[-keep:]
        self.state.outputs = self.state.outputs[-keep:]
        self.guards.reset()

        self.state.internal_log.append({
            "event": "EXHALE",
            "reason": reason,
            "turn": self.state.turn,
            "kept_turns": keep,
        })

    def _log(
        self,
        out: str,
        drift_snap,
        guard_res,
        decision: ScheduleDecision,
    ) -> None:
        self.state.internal_log.append({
            "turn": self.state.turn,
            "output_chars": len(out),
            "drift_score": drift_snap.drift_score,
            "len_growth": drift_snap.len_growth,
            "repeat_ratio": drift_snap.repeat_ratio,
            "guard_fail": guard_res.fail_reason,
            "guard_deltas": guard_res.deltas,
            "scheduled_exhale": decision.should_exhale,
            "exhale_reason": decision.reason,
        })
