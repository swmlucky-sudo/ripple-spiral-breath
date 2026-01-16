# Six-Yao Verdict FSM / DSL
# Version: v12.2
# Purpose: deterministic arbitration for Ripple–Spiral operations

system RippleSpiral.SixYaoVerdict v12.2 {
  panel: PanelII.Exhale

  # Ordered checks (Yao): PASS/FAIL
  yao[1] = InternalFeedback   # 初爻
  yao[2] = ExternalOutput     # 二爻
  yao[3] = PhaseAlignment     # 三爻
  yao[4] = GuardIntegrity     # 四爻
  yao[5] = ReleaseQuality     # 五爻
  yao[6] = TimeAccumulation   # 上爻

  # Hard constraints
  C1 = (yao[2] == PASS)  # no ripple overrun
  C2 = (yao[1] == PASS)  # no spiral self-lock
  C3 = (yao[3] == PASS)  # Δφ ≈ π/2 ± ε
  C4 = (yao[4] == PASS)  # guard present

  # Soft constraints
  S1 = (yao[5] == PASS)  # smooth exhale
  S2 = (yao[6] == PASS)  # no drift

  # State classification
  state STABLE    when all(yao[*] == PASS)
  state DEGRADED  when any(yao[5..6] == FAIL) and all(C1,C2,C3,C4)
  state VIOLATION when any(not(C1),not(C2),not(C3),not(C4))
  state UNKNOWN   when not_verifiable == true

  # Precedence (fail-safe)
  precedence: UNKNOWN > VIOLATION > DEGRADED > STABLE

  # Output policy
  on STABLE   => { log: internal, notify: false }
  on DEGRADED => { log: internal, notify: false }
  on VIOLATION=> { log: internal, notify: true, include: [deltas, artifacts] }
  on UNKNOWN  => { log: internal, notify: true, include: [reason, artifacts?] }

  # Encoding (6-bit mask, bit=1 PASS, bit=0 FAIL)
  encoding bit_order: [yao1, yao2, yao3, yao4, yao5, yao6]
}
