Type: task
Status: ready-for-agent
Blocked by: 87, 88

# Field-isolation inventory sidecar

## Fate (2026-08-19)

**Blocked** on native asca validation. After [Implement `validate` + `validate_part` on the private asca fork](87-implement-asca-fork-validate.md) and [Wire conlanger to forked asca `validate`](88-wire-conlanger-forked-asca-validate.md), this ticket may be **rewritten** (sidecar CSV + `blame` via `validate_part`, drop stubs), **deleted**, or **closed** — depending on what that work actually enables. Do not implement the stub engine until then.

Whole-rule inventory `ok` stays `asca run` + probe words (grill Q3 A).

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

- [Implement `validate` + `validate_part` on the private asca fork](87-implement-asca-fork-validate.md)
- [Wire conlanger to forked asca `validate`](88-wire-conlanger-forked-asca-validate.md)
- ~~[Inventory success/error CSV splits and ok-change changelog](34-inventory-success-error-splits-and-ok-changelog.md)~~ done

## Comments

- 2026-08-19: Owner hesitant to start stubs; alternative is native asca per-field validation. Spike: [Native ASCA per-field validation effort](86-spike-asca-native-per-field-validation.md). Findings: [research/asca-native-per-field-validation.md](../research/asca-native-per-field-validation.md).
- 2026-08-19 grill: **Q3 A** keep `ok` as `asca run` + probes. **Q4** block this ticket; it may be rewritten, deleted, or closed after 87/88. **Q5 A** chart those tasks; private fork only (`/home/pappa/Projects/Pappa/asca-rust`).

## Acceptance criteria

- [ ] Sidecar CSV produced by regen (fails-only by default; flag documented if broader)
- [ ] Stub table + shape-aware selection implemented per research §4
- [ ] `blame` column derived; whole-rule `ok` unchanged
- [ ] Tests: known Tier 1–2 field faults attribute correctly; at least one documented cross_field / false-fail case
- [ ] Notes or docstring lists disagreement cases and ticket-10 boundary
