Type: task
Status: resolved
Blocked by: 12

# Correction pass: Index tilde notation

Target cluster: `syntax_other` — Index **`~`** notation — **233** rules at current inventory baseline ([summary](../inventory/asca-rule-inventory-summary.md)); largest residual `syntax_other` cluster.

Spawned from [correction pass template](13-correction-pass-template.md) prioritisation (2026-08-08).

## Problem

Rules fail with tilde-related syntax errors across two bucket shapes:

| Bucket | count | example message |
|--------|------:|-----------------|
| `Expected … received '~'` | 112 | `ʃ(~ʃ:[+long]) ʒ > sʲ sʲ` |
| `Expected end of line, received '~'` | 82 | `{β,w} > bj~vj~v` |
| other `~` in description | ~39 | mixed |

Index uses `~` for optional segments, repetition, and output-chain glue. ASCA 0.10.2 rejects bare `~` in I/O segments.

## What to build

1. Identify dominant Index `~` patterns in the cluster (optional wrapper, chained outputs, env-adjacent repetition).
2. Implement a **class-first** compile and/or parse normaliser per [edit ladder](04-historical-fidelity-vs-validity.md) and ADR-0010 — expand toward ASCA-valid sets, optionals in env/structures, or compile-time chain splits where the phonological claim is preserved.
3. Hold out rules that cannot be expressed without meaning change (`status: skipped` + validation report reason).
4. Full inventory re-run; record before/after for `syntax_other` rows whose description contains `~`.

**Expected impact:** ~**81** ok uplift at ~35% recoverability (upper bound; overlaps with other clusters possible).

## Policy

- `raw` and `source` unchanged; transforms are mechanical class rewrites.
- Do not silently drop optional/repetition semantics — prefer env/structure placement or documented skip.
- One ticket for all `~` surface notation (do not split received-`~` vs EOL-`~` unless residual cluster forces Phase 2).

## Acceptance criteria

- [x] Dominant `~` patterns documented with before/after compile examples
- [x] Class-first handler(s) implemented with unit tests on representative inventory lines
- [x] Full inventory re-baseline; ok/fail delta and residual `~` cluster size in **Answer**
- [x] Fixtures updated for rules whose validation outcome changed

## Answer

### Pattern taxonomy (compile before → after)

| Pattern | Example (Index) | After compile | Handler |
|---------|-----------------|---------------|---------|
| Two-part alternation | `ɣ~ɡ`, `d~ð`, `h > j~ʔ` | `{ɣ,ɡ}`, `{d,ð}`, `{j,ʔ}` | `expand_index_tilde_notation` token split |
| Spaced tilde | `!ɡ ~ !̃` | `{!ɡ,!̃}` | `_SPACED_TILDE_RE` normalize |
| Set-member chain | `{ts~tsʰ,ts,s}`, `{~ɛ,ẽ}` | `{ts,tsʰ,ts,s}`, `{ɛ,ẽ}` | set member expansion |
| Paren optional wrapper | `ʃ(~ʃ:[+long])` | `{ʃ,ʃ:[+long]}` | `X(~Y)` → `{X,Y}` |
| Per-segment output alt | `dzʲ~zʲ tʃ:[+cg] dʒ~ʒ` | `{dzʲ,zʲ} tʃ:[+cg] {dʒ,ʒ}` | token alternation (multi-segment output) |
| Three+ segment alt | `t~ɾ~n`, `d~n~l`, `k~x~ɡ~ɣ` | `{t,ɾ,n}`, `{d,n,l}`, `{k,x,ɡ,ɣ}` | 3+ → set (not chain) |
| Multigraph output chain | `{β,w} > bj~vj~v` (sole output token) | `{β,w} > bj` … `vj > v` | `_expand_output_tilde_field` + chain split |
| Input alternation | `q:[+long]~qχ` | `{q:[+long],qχ}` | token alternation |

**Wiring:** `normalize_index_rule_tilde_fields()` on index `input`/`output` before `expand_chained_index_rule()`; `expand_index_tilde_notation()` via pipeline step 10 (`expand_meta_notation`).

**Hold-outs:** Parenthetical segments without tilde (`(s)`, `Cw_{(d)l,f3}`) remain for ticket 48. One inventory row still mentions `~` in the error string (`!` click-letter input; tilde in output is expanded but rule fails on `ǃ`).

### Inventory (ASCA 0.10.2, `create_index` 2026-08-08)

| Metric | Before | After |
| --- | ---: | ---: |
| OK / total | 6696 / 9201 (72.8%) | **6792 / 9201 (73.8%)** |
| `syntax_other` | 1114 | **919** |
| Fail rows with `~` in description | ~236 | **1** (click-letter `!` rule; not tilde syntax) |

**+96 ok** rules. Residual parenthetical / click-letter failures out of scope for this ticket.

### Implementation

- `src/conlanger/tools/asca_compile/tilde.py` — `expand_index_tilde_notation`, `normalize_index_rule_tilde_fields`
- `src/conlanger/tools/asca_compile/planned.py` — `expand_meta_notation` delegates to tilde expander
- `src/conlanger/tools/rules.py` — tilde field normalize before chain expansion
- Tests: `tests/conlanger/tools/test_asca_compile_tilde.py`, `test_sound_change_ruleset_validates_tilde_notation_fixtures` in `test_SoundChangeRule.py`

## References

- [Correction pass template](13-correction-pass-template.md)
- [Correction pass: chain split](18-correction-pass-chain-split.md) — related multi-segment output handling
- [Inventory summary](../inventory/asca-rule-inventory-summary.md)
