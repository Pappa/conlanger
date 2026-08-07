Type: task
Status: ready-for-agent
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

- [ ] Each sub-pattern above has a handler or documented `status: skipped` with owner rationale
- [ ] Full inventory re-run; before/after for remaining `₀`/`₁`/`₂` error tokens
- [ ] Tests per shipped handler; no regression on phase-1 happy paths
