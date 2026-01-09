from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class GuardConfig:
    # C1: output overrun (character based MVP)
    max_output_chars: int = 4000

    # C2: spiral self-lock heuristic (self-reference loop)
    max_self_ref_hits: int = 3

    # C3: Δφ ≈ π/2 ± ε (MVP proxy: balance between “analysis” and “answer” sections)
    # Here we approximate by ratio of bracketed/meta lines vs normal lines.
    phase_ratio_target: float = 0.5
    phase_ratio_epsilon: float = 0.35

    # C4: guard present -> always True if GuardSuite is used
    guard_present_required: bool = True


@dataclass
class GuardResult:
    c1_ok: bool
    c2_ok: bool
    c3_ok: bool
    c4_ok: bool
    fail_reason: Optional[str]
    deltas: Dict[str, Any]


class GuardSuite:
    """
    Implements C1–C4 checks in a model-agnostic way (text-only MVP).
    """

    def __init__(self, cfg: GuardConfig | None = None) -> None:
        self.cfg = cfg or GuardConfig()
        self._self_ref_hits = 0

    def reset(self) -> None:
        self._self_ref_hits = 0

    def check(self, output: str) -> GuardResult:
        deltas: Dict[str, Any] = {}

        # C1: no ripple overrun
        c1_ok = len(output) <= self.cfg.max_output_chars
        deltas["output_chars"] = len(output)
        deltas["max_output_chars"] = self.cfg.max_output_chars

        # C2: no spiral self-lock (cheap heuristic: “as I said” / “I already told”)
        self_ref = self._is_self_reference(output)
        if self_ref:
            self._self_ref_hits += 1
        deltas["self_ref_hits"] = self._self_ref_hits
        deltas["max_self_ref_hits"] = self.cfg.max_self_ref_hits
        c2_ok = self._self_ref_hits <= self.cfg.max_self_ref_hits

        # C3: Δφ ≈ π/2 ± ε (proxy)
        phase_ratio = self._phase_proxy_ratio(output)
        deltas["phase_ratio"] = phase_ratio
        deltas["phase_ratio_target"] = self.cfg.phase_ratio_target
        deltas["phase_ratio_epsilon"] = self.cfg.phase_ratio_epsilon
        c3_ok = abs(phase_ratio - self.cfg.phase_ratio_target) <= self.cfg.phase_ratio_epsilon

        # C4: guard present
        c4_ok = True if self.cfg.guard_present_required else True
        deltas["guard_present"] = True

        fail_reason = None
        if not c1_ok:
            fail_reason = "C1_FAIL_output_overrun"
        elif not c2_ok:
            fail_reason = "C2_FAIL_spiral_self_lock"
        elif not c3_ok:
            fail_reason = "C3_FAIL_phase_out_of_band"
        elif not c4_ok:
            fail_reason = "C4_FAIL_guard_missing"

        return GuardResult(
            c1_ok=c1_ok,
            c2_ok=c2_ok,
            c3_ok=c3_ok,
            c4_ok=c4_ok,
            fail_reason=fail_reason,
            deltas=deltas,
        )

    @staticmethod
    def _is_self_reference(text: str) -> bool:
        t = text.lower()
        needles = [
            "as i said",
            "as i mentioned",
            "i already told",
            "i have said",
            "如我所說",
            "如我提到",
            "我剛剛說過",
        ]
        return any(n in t for n in needles)

    @staticmethod
    def _phase_proxy_ratio(text: str) -> float:
        lines = [ln for ln in text.splitlines() if ln.strip()]
        if not lines:
            return 0.0
        meta = sum(1 for ln in lines if ln.strip().startswith("[") or ln.strip().startswith("（"))
        return meta / max(1, len(lines))
