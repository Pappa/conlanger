Type: spike
Status: resolved
Blocked by:

# Spike: field-isolation compile validation

## Question

Can we raise confidence in **compile validation** by validating **individual corpus-rule fields** (`input`, `output`, `env`, `exception`) against ASCA when the other fields are replaced by known-valid stubs — without reviving [Rule-derived probe synthesis](10-rule-derived-probe-synthesis.md) (wontfix)?

## Context

Today inventory validates the **whole** compiled rule via `validate_asca` + baseline wordlist ([Full-corpus validation inventory](12-full-corpus-validation-inventory.md)). When a rule fails, it is often unclear *which field* is at fault. Owner intent (map grill Q4): explore **syntax/shape isolation** with canned stubs, still using ASCA — but design is unclear; this spike must recommend whether to proceed, and how.

## What to investigate (primary sources)

1. Current compile path: corpus rule dict → `RuleChange` / `PhonologicalRuleSet` → `validate_asca` (`src/conlanger/tools/`).
2. ASCA 0.10.2 constraints on env/exception (e.g. single `_` focus, `#` periphery, optionals env-only) — [research/asca-rule-validity.md](../research/asca-rule-validity.md) + ASCA docs.
3. Concrete stub candidates: what minimal always-valid `input`/`output`/`env`/`exception` combinations let a *real* field be the only variable?
4. False positives/negatives: when would a field pass in isolation but fail in the full rule (or the reverse)?
5. How results would be recorded (extra inventory columns vs separate CSV) if adopted — recommendation only, no implementation required.
6. Explicit boundary vs ticket 10: stubs + baseline wordlist only; no per-rule probe synthesis.

## Deliverable

Findings markdown under `.scratch/cleaned-rule-corpus/research/` (e.g. `field-isolation-compile-validation.md`) with a clear **go / no-go / go-with-limits** recommendation and open questions for a follow-on task ticket.

## Acceptance criteria

- [x] Research file written with cited primary sources
- [x] Stub strategy table per field (`input` / `output` / `env` / `exception`)
- [x] Explicit comparison to ticket 10 wontfix boundary
- [x] Recommendation suitable to graduate or kill a follow-on implementation ticket

## Answer

**go-with-limits.** Field isolation with canned stubs + existing `validate_asca` / baseline wordlist can attribute most Tier 1–2 syntax failures to a field; it must not replace whole-rule `ok`, and cross-field cases (sets, condensed balance, insertion+env, deletion-vs-lexicon) will disagree. Stay inside ticket 10: no probe synthesis — only fixed/shape-aware stubs. Record as a fails-only sidecar CSV with a derived `blame` column.

Findings: [research/field-isolation-compile-validation.md](../research/field-isolation-compile-validation.md).
