[Uploading architecture.md…]()
# Ripple–Spiral Six‑Yao Verdict System

**Doc path:** `/docs/architecture.md`  
**Version:** v12.2  
**Primary target:** Panel II (Exhale / 釋放)  
**Design goals:** Silent‑by‑default, Notify‑on‑FAIL, Complete state coverage, Forensic traceability

---

## 1) What this is

The Six‑Yao Verdict System is a **deterministic health‑arbitration layer** for Ripple–Spiral operations.

It answers one question:

> **Can the loop continue operating safely without intervention?**

This layer:

- **Does not** predict outcomes.
- **Does not** issue actions on success.
- **Does** classify the current operating condition into a complete, explainable state.
- **Does** emit a notification only when the state crosses a failure boundary.

---

## 2) Core concept

The system evaluates **six ordered binary checks** (“Yao”, 爻). Each check is **PASS** or **FAIL**.

Because there are six binary checks, the model spans a complete state space of:

- **2⁶ = 64 states**

This guarantees no ambiguous “unknown” condition inside the defined measurement scope.

---

## 3) Terminology

- **Yao / 爻**: One ordered check (binary constraint).
- **Hexagram / 卦**: A 6‑bit state snapshot (the combination of all six Yao).
- **Change line / 變爻**: A Yao whose state flips between runs (PASS→FAIL or FAIL→PASS).
- **Panel**: A phase of Ripple–Spiral operation (Panel II = Exhale).
- **Guard**: Protective mechanisms that enforce safety envelopes (limits, fallbacks, circuit breakers).

---

## 4) The six checks

### 4.1 Ordered checks

| Order | Yao | Dimension | Engineering meaning |
|------:|-----|----------|---------------------|
| 1 | 初爻 | Internal feedback | Feedback is reversible; no self‑locking behavior |
| 2 | 二爻 | Output boundary | Ripple output stays within envelope; no overrun |
| 3 | 三爻 | Phase alignment | Δφ stays near π/2 within tolerance ε |
| 4 | 四爻 | Guard integrity | Guard is present and responsive |
| 5 | 五爻 | Release quality | Exhale is smooth; low residual oscillation |
| 6 | 上爻 | Time accumulation | No drift/creep accumulation across runs |

### 4.2 Hard constraints mapping (C1–C4)

| Constraint | Linked Yao | Definition |
|-----------|-----------|------------|
| C1 | 二爻 | **No ripple overrun** |
| C2 | 初爻 | **No spiral self‑lock** |
| C3 | 三爻 | **Δφ ≈ π/2 ± ε** |
| C4 | 四爻 | **Guard present** |

Notes:
- Yao 5–6 are **quality/trend gates** to prevent silent degradation.

---

## 5) Data flow

```mermaid
flowchart LR
  A[Telemetry / Metrics] --> B[Compute Yao 1..6]
  B --> C[Build 6-bit State (Hexagram)]
  C --> D{Any FAIL?}
  D -- No --> E[Log internally only]
  D -- Yes --> F[Notify + attach artifacts]
```

### 5.1 Inputs

Inputs are **metrics** and **telemetry** relevant to the checks, for example:

- Ripple amplitude, integral, RMS, saturation counters
- Spiral feedback gain, lock index, hysteresis indicators
- Phase offset Δφ and tolerance ε
- Guard heartbeat / latency / circuit status
- Exhale smoothness index, residual vibration energy
- Drift rate across runs, trend slope, accumulation score

### 5.2 Outputs

- **PASS**: internal log entry only
- **FAIL**: notification + minimal structured evidence (deltas + artifacts)

---

## 6) State encoding (64-state model)

### 6.1 Bit layout

Define a 6‑bit vector `b5..b0`, where each bit is 1 for PASS, 0 for FAIL:

- `b0` = Yao 1 (初爻) internal feedback
- `b1` = Yao 2 (二爻) output boundary
- `b2` = Yao 3 (三爻) phase alignment
- `b3` = Yao 4 (四爻) guard integrity
- `b4` = Yao 5 (五爻) release quality
- `b5` = Yao 6 (上爻) time accumulation

Example:

- `111111` = all PASS (stable, silent)
- `111011` = guard FAIL only (notify)

### 6.2 State ID

Recommended state identifier:

- `RS-P2-EXH-<bits>`

Example:

- `RS-P2-EXH-111111`

---

## 7) Notification policy

### 7.1 Silent-on-PASS

If all Yao are PASS:

- Log internally
- Do not emit user-facing messages

### 7.2 Notify-on-FAIL

If any Yao is FAIL:

- Emit a user-facing notification containing:
  - PASS/FAIL summary (FAIL)
  - Which constraints failed (C1–C4)
  - Key metric deltas (vs. baseline or last good)
  - Links/paths to the latest artifacts (PNG/TXT/CSV)

---

## 8) Artifacts and traceability

Artifacts are stored for forensic analysis and reproducibility.

- **PNG**: visual trace (waveform / phase / envelope)
- **TXT**: human-readable run log
- **CSV**: machine-readable metrics snapshot

Recommended rule:

- Always persist artifacts internally
- Only surface links externally on FAIL (to reduce noise)

---

## 9) Extensibility

### 9.1 Multi-panel support

For other panels (e.g., Inhale, Hold, etc.), reuse the same architecture:

- Keep the six ordered Yao (structure)
- Substitute the panel-specific metrics and thresholds (implementation)

### 9.2 Changing thresholds

Threshold changes should be:

- versioned
- recorded with provenance
- applied with backward compatibility notes

---

## 10) Security & integrity notes

- The arbitration layer should treat **missing telemetry** as **non-verifiable**.
- Non-verifiable can be mapped as:
  - **FAIL** (strict mode) to avoid false safety
  - or **UNKNOWN** (tri-state extension) if explicitly designed

The default design of this repository uses **binary verdicts** to keep the surface simple.

---

## 11) Summary

- Six ordered binary checks → complete 64-state coverage
- Silent-by-default → avoids alert fatigue
- Notify-on-FAIL → provides deltas and artifacts for fast diagnosis
- Portable architecture → can be applied across panels

