Type: task
Status: resolved
Blocked by: 40

# Correction pass: subscript edge cases (phase 2)

Target cluster: residual `unknown_character` / `syntax_other` rules that still carry Index subscripts after [phase-1 positional/identity compile expansion](40-correction-pass-positional-identity-subscripts.md).

## Scope (from ticket 40 residual + research §6.3)

1. **Matrix-attached identity** — `V₀[+nas]V₀[-nas] → V₀[+nas]` → `V:[+nas]=0 V:[-nas]=0 > 0:[+nas]`
2. **Matrix-attached positional** — `V₁[+high]_V₂`, `{ʔ,h} → ∅ / V₁[+high]_V₂`
3. **Inter-slot diacritics** — `C₁ˤC₂ → C₁C₂ˤ` (line 1478)
4. **Identity compounds** — `mV₀nV₀`, `CʔV₀`, `C₀VC₀` (segment literal + `V₀` / `C₀`)
5. **Optional + positional** — `(C₃)C₄` chains (line 7317)
6. **Uppercase / section-local `S₁`, `B₁`** — Athabaskan-style; distinguish from positional slots
7. **Prose env / exception** — e.g. `… / if C₂ was a plosive`, `V₀ = U` exception gloss

## Out of scope

- Correspondence-series `s₁` on lowercase segments (ticket 27 / series backlog)
- Meta-notation superscripts (`V₀³`)
- Brassica compile path

## Acceptance criteria

- [x] Each sub-pattern above has a handler or documented `status: skipped` with owner rationale
- [x] Full inventory re-run; before/after for remaining `₀`/`₁`/`₂` error tokens
- [x] Tests per shipped handler; no regression on phase-1 happy paths

## Answer

**Phase 2 — 2026-08-12**

Extended `expand_index_subscript_references()` in `src/conlanger/tools/compile/asca/subscript_references.py`; ref length `0ː` → `0:[+long]` in `length_marks.py`. Field bind order is now input → env → exception → output (ASCA ref order).

| Sub-pattern | Disposition |
| --- | --- |
| Matrix-attached identity | Handler — `V₀[+nas]` → `V:[+nas]=0` / `0:[+nas]` (input re-declares identity matrices with base) |
| Matrix-attached positional | Handler — `C₁[+high]`, `CV:[+stress]₂` → `C:[+high]=1`, `CV:[+stress]=2` |
| Inter-slot `ˤ` | Handler — `C₁ˤ` → `C:[+pharyn]=1` / `2:[+pharyn]` |
| Identity compounds | Handler — bare-slot scan covers `mV₀`, `CʔV₀`, `C₀VC₀`; length on refs via length-marks |
| Optional + positional | Handler — `(C₃)` → `{3}` after slot expand (ASCA structure optional; avoids meta `{34,4}` glue) |
| Uppercase `S₁` / `B₁` | Treat as positional when bare `Xₙ`; **hold-out** `Bʱ₁` (diacritic between letter and subscript; PIE breathy ≠ `group_mappings` `B`→back vowel) — leave failing until section-local mapping |
| Prose env / exception | **Hold-out** — leave Index subscripts unexpanded in prose fields (`if`/`was`/`=`/…); still fail ASCA (honest fail vs prior false-ok when digits were rewritten inside prose, e.g. 17.5). Owner may later `status: skipped` / comment capture. No YAML skips shipped this pass. |
| Meta superscripts (`V₀³`, `…₀3_`) | Out of scope (unchanged) |

**Inventory (ASCA 0.10.2):**

| Metric | Before | After |
| --- | ---: | ---: |
| OK / total | 7963 / 9638 (82.6%) | **7977 / 9638 (82.8%)** |
| Sections all OK | 263 / 714 (36.8%) | **265 / 714 (37.1%)** |
| `error_token` `₀` | 3 | **1** |
| `error_token` `₁` | 1 | **2** |
| `error_token` `₂` | 6 | **5** |

+14 ok rules. Residual digit fails are prose env/exception tails + `Bʱ₁` (+ one `U₁U₂` prose syllable gloss).
