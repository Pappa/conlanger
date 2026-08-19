Type: task
Status: needs-triage
Blocked by: None

# Correction pass: flatten nested sets in stages I/O

Target cluster: `nested_brackets` — true nested `{…}` in **stages** (~9 inventory rows at 2026-08-12 baseline).

Spawned from [spike 67](67-spike-nested-sets.md). Findings: [nested-sets-inventory.md](../research/nested-sets-inventory.md) §4.1. **Placement:** [spike 85](85-spike-nested-set-flatten-prototype.md) — **parse-time at slot P4**, union flatten of YAML-nested I/O. Parallel-column / optional-prefix shapes remain [71](71-grill-paren-and-parallel-set-notation.md) (**out of scope here** — naive flatten does not fix them).

Examples:

| source | YAML / Index shape | Spike 85 |
|--------|--------------------|----------|
| `index_diachronica_original.html:998` | HTML `{ʔ,hₓ}` → YAML `{ʔ,h₁,h₂,h₃}` (already flat via series expansions) | no-op |
| `index_diachronica_original.html:5048` | `{{∅,∅}s,s{∅,∅}}` / `{{h₁,h₃}s,s{h₁,h₃}}` | union → **`ok`** |
| `index_diachronica_original.html:1398` | `{{s,z}(ˤ),ʒ}ʃ` | needs **union_paren** → **`ok`** |
| `index_diachronica_original.html:6193` | `{e,w{æ,i}}` | union → **`ok`** |
| `index_diachronica_original.html:2398` | `(h)ə{p,b}` (depth 1) | **unchanged** — #71 |

ASCA: `NestedBrackets` in I/O when YAML (or compile parentheticals) actually nests.

## What to build

1. Classify: union-flatten (this ticket) vs #71 parallel columns vs `manual_mappings` / skip.
2. Parse-time flatten of **stages** (each string independently) at **P4**, sharing the helper with [69](69-correction-pass-flatten-nested-context-sets.md). Preserve `raw`. Mode **union**; include **union_paren** for `:1398` `{s,z}(ˤ)` if 69’s helper already has that mode.
3. Do **not** flatten `(h)ə{p,b}`, `e(C){V[…]}`, `a(C){o,e}` — YAML depth 1; NestedBrackets comes from compile parentheticals (#71).
4. Chain malformation (`4654`, unbalanced `2173`) → parse/chain fix or skip, not nested flatten.

## Policy

- ADR-0010 / ADR-0002: parse-time class-first flatten into applier-neutral flat sets; `raw` unchanged. Do not compile-flatten after parentheticals (would rewrite D).
- Spike 85: 0 `ok` regressions; `:8439` union → `syntax_other` (slash members) — residual, not a success metric.

## Acceptance criteria

- [ ] Taxonomy + handler(s) + tests (`:5048`, `:6193`, `:1398`; negative tests `:2398` / `:3124` unchanged)
- [ ] Inventory re-baseline; metrics in **Answer**
- [ ] Complex residuals routed to `manual_mappings` or skip (`:8439`, `:2173`, `:4654`)

## Agent Brief

**Category:** enhancement  
**Summary:** Parse-time union-flatten of true nested `{…}` in **stages** (P4). Optional-prefix parallel columns stay ticket 71.

**Desired behavior:** Reuse #69’s `flatten_nested_sets` on each stage string. TDD. Full regen.

**Out of scope:** env/exception ([69](69-correction-pass-flatten-nested-context-sets.md)); #71 D shapes; compile-created nesting (`:1149` `{x₁,x₂}` → group-mapping NestedBrackets).

**Blocker cleared:** Spike [85](85-spike-nested-set-flatten-prototype.md) resolved; #71 no longer blocks the union-flatten slice (D is excluded, not deferred).
