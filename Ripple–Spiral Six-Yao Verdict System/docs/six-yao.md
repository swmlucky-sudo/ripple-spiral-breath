Six-Yao Verdict Layer
Purpose

The Six-Yao Verdict Layer provides a state-accumulating decision mechanism for long-running Ripple–Spiral operations.
Instead of evaluating stability from a single snapshot, it observes six consecutive evaluation phases (yao) to determine whether the system remains coherent over time.

Position in Architecture
Ripple / Spiral metrics
        ↓
   Breath Phase Model
        ↓
  Six-Yao Verdict FSM
        ↓
 PASS / FAIL decision
        ↓
 Notify / Observe / Log


The verdict layer does not control system behavior.
It only observes, evaluates, and reports.

Why Six States?

Each “yao” represents a temporal consistency check, not a symbolic unit.

Yao	Engineering Meaning
1	Initial signal validity
2	Ripple containment
3	Spiral continuity
4	Phase coherence (Δφ)
5	Guard persistence
6	Overall stability

A verdict is only produced after all six checks are resolved.

Verdict Rules

PASS

All six yao are valid

No constraint violations

FAIL

Any yao invalid

Or telemetry missing beyond tolerance

SILENT

PASS produces no external notification

FAIL triggers full diagnostic output

Constraint Mapping
Constraint	Source
C1 — No ripple overrun	Ripple metrics
C2 — No spiral self-lock	Spiral dynamics
C3 — Δφ ≈ π/2 ± ε	Breath phase
C4 — Guard present	System heartbeat
Artifacts on FAIL

A FAIL verdict must include:

PNG (visual snapshot)

TXT (plain log)

CSV (numeric metrics)

This requirement is enforced via JSON Schema.
