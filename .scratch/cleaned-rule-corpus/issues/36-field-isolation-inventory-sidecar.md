Type: task
Status: ready-for-agent
Blocked by: 34

# Field-isolation inventory sidecar

## Question

How should regen attach **per-field** ASCA diagnostics for failing corpus rules so correction triage can blame `input` / `output` / `env` / `exception` — without changing whole-rule `ok` or reviving probe synthesis?

## Decision (from spike)

Adopt **go-with-limits** from [Spike: field-isolation compile validation](35-spike-field-isolation-compile-validation.md):

Findings: [research/field-isolation-compile-validation.md](../research/field-isolation-compile-validation.md).

### Build

1. Optional inventory enrichment (default: **fails-only** — rows where whole-rule `ok` is false).
2. For each isolated field, build a rule from the **real** field + **canned/shape-aware stubs** (§4 of the research); run existing `validate_asca` + baseline wordlist.
3. Write sidecar CSV e.g. `inventory/asca-field-isolation.csv` with join keys, per-field ok/class, and derived `blame` (`sole field` | `multi` | `cross_field` | `none`).
4. Keep main inventory `ok` as the SoT success metric; do not redefine it from isolation.
5. Document known false pass/fail cases in module/docs so agents do not “fix” them with probe synthesis ([ticket 10](10-rule-derived-probe-synthesis.md) remains wontfix).

### Stub policy (summary)

- Defaults: input `a`, output `e`, omit env/exception.
- Shape-aware: insert → stub env `#_`; delete → stub input `x`; metathesis → `ab`; sets → cardinality-matched pair stubs (best-effort).
- Never stub exception as `| _`.
- Pre-ASCA handle bare `#` I/O render/comment hazard (`format_error`).

### Out of scope

- Per-rule probe-word synthesis
- Replacing whole-rule inventory metrics
- Bare I/O “transform-exempt” tagging (still map fog)

## Blocked by

- [Inventory success/error CSV splits and ok-change changelog](34-inventory-success-error-splits-and-ok-changelog.md) — ship filtered CSVs + changelog first; wire isolation into the same regen pass or behind a flag once 34 lands.

## Comments

- 2026-08-19: Owner hesitant to start stubs; alternative is native asca per-field validation. Spike: [Native ASCA per-field validation effort](86-spike-asca-native-per-field-validation.md). Findings: [research/asca-native-per-field-validation.md](../research/asca-native-per-field-validation.md). Hold implementation until that path is accepted or declined; if accepted, retarget this ticket (sidecar CSV + `blame`, drop stub engine).

## Acceptance criteria

- [ ] Sidecar CSV produced by regen (fails-only by default; flag documented if broader)
- [ ] Stub table + shape-aware selection implemented per research §4
- [ ] `blame` column derived; whole-rule `ok` unchanged
- [ ] Tests: known Tier 1–2 field faults attribute correctly; at least one documented cross_field / false-fail case
- [ ] Notes or docstring lists disagreement cases and ticket-10 boundary
