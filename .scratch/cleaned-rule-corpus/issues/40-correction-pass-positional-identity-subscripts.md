Type: task
Status: resolved
Blocked by: 38

# Correction pass: positional slots and identity subscripts (compile-time)

Target cluster: `unknown_character` — error tokens **`₀`** (49 rules), **`₁`** (37 rules) — **86** failing corpus rules in [asca-rule-inventory-error.csv](../inventory/asca-rule-inventory-error.csv) (2026-08-07 baseline: **6395 / 9201 ok**).

Related: correspondence-series **`₁`** on lowercase segments may overlap with [series-mappings coverage backlog](../series-mappings-coverage-backlog.md); this ticket is **positional slots** (`C₁`, `V₂`, …) and **identity subscripts** (`V₀`) only — see `classify_subscript_token()` in `series_mappings.py`.

## What to build

Implement **`expand_index_subscript_references`** at **compile time** per [positional-slots-and-identity-subscripts.md](../research/positional-slots-and-identity-subscripts.md) and [asca-compile-transform-order.md](../research/asca-compile-transform-order.md) (**Order 3**, before group mappings and length marks).

1. Map Unicode subscripts on **class letters** → ASCA reference declarations + bare refs (`C₁C₂ → C₂` → `C=1 C=2 > 2`).
2. Map **`₀` identity** on class letters → `V=0` / bare `0` (`V₀V₀ → V₀` → `V=0 0 > 0`).
3. Whole-rule pass: declare refs in input before use in output/env; env co-reference may need `_` focus insertion.
4. Bracket-safe: do not rewrite inside `[...]` feature matrices except where research documents feature-attached identity (`V₀[+nas]`).
5. Corpus YAML and **`raw`** unchanged; transform in `RuleChange` / `asca_compile/` pipeline only.
6. Re-run `uv run regenerate_corpus`; record before/after for `₀` / `₁` error tokens and overall ok count.

## Policy

- Class-first mechanical transform (ADR-0010) — not `status: skipped`.
- Do **not** expand correspondence-series tokens here (ticket 27 / parse-time).
- Residual hard cases (compounds `mV₀`, `C₁ˤC₂`, uppercase `S₁` section-local) — document in **Answer**; separate tickets or skip after class-first pass.

## Acceptance criteria

- [x] Compile step wired at documented order (spike 38)
- [x] Unit tests on happy-path examples from research §1 table
- [x] ASCA integration tests where `asca` on PATH
- [x] Full inventory re-run; before/after in **Answer**
- [x] No imports from `legacy/`

## Answer

**Phase 1 (easy wins) — 2026-08-07**

- `expand_index_subscript_references()` in `src/conlanger/tools/asca_compile/subscript_references.py`; wired via `planned.py` / compile pipeline order 3.
- Whole-rule pass: input → output → env → exception; shared declared-ref set; prepend `_ ` to env when refs expanded and no focus present.
- Bracket interiors `[...]` left untouched (matrix-attached subscripts deferred).

**Inventory (ASCA 0.10.2):**

| Metric | Before | After |
| --- | ---: | ---: |
| OK / total | 6527 / 9201 (70.9%) | **6578 / 9201 (71.5%)** |
| `error_token` `₀` | 49 | **3** |
| `error_token` `₁` | 37 | **4** |
| `error_token` `₂` | (in mix) | **10** |

+51 ok rules. Residual subscript failures → [Correction pass: subscript edge cases (phase 2)](41-correction-pass-subscript-edge-cases.md).

## References

- [Spike: ASCA compile transform ordering](38-spike-asca-compile-transform-order.md)
- [Refactor DiachronicSeries and compile subcomponents](39-refactor-sound-change-ruleset.md) — `asca_compile/` package is the landing zone
- Map fog: **Subscript notation** — positional + identity → compile-time
