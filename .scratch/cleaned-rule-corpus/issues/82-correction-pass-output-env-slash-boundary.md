Type: task
Status: resolved
Blocked by:

# Correction pass: output/env slash boundary (residual)

Target cluster: `syntax_other` — **`Expected end of line… Did you forget a '/' between the output and environment?`** — **23** rules in ≤3-fail sections (**9** mono-class sections would complete if cleared). Full-corpus count at claim: **68** ([inventory summary](../inventory/asca-rule-inventory-summary.md)).

Spawned from [64 syntax_other near-miss spike](../issues/64-spike-syntax-other-near-miss-sections.md) (2026-08-19).

## Context

Residual output/environment boundary failures after [48 parenthetical](48-correction-pass-parenthetical-segment-notation.md) and [51 input optionals](51-correction-pass-input-optionals-to-env.md).

| Received token | near-miss count | typical shape |
|---------------:|----------------:|---------------|
| `(` | 12 | output/env glue with unclosed paren |
| `∅` | 3 | deletion concat before `/` |
| `#` | 2 | env anchor in wrong position |
| other | 6 | `&`, `ʲ`, `:`, `̥`, `ˀ`, `_` |

## What to build

1. Sample failing rules; group by fix pattern (insert missing `/`, move paren to env, split output).
2. Parse/compile rewrite for dominant patterns.
3. Full inventory re-run; record before/after for rows matching the exact error message.
4. Unit tests.

## Policy

- Class-first mechanical transforms per edit ladder.
- Do not re-open resolved 48/51 clusters — only residual shapes.

## Acceptance criteria

- [x] Dominant patterns documented
- [x] Transform implemented for ≥60% of near-miss cluster
- [x] Full inventory re-run; before/after in **Answer**
- [x] Fixtures updated where validation outcomes change

## Answer

**Shipped 2026-08-19.**

### Patterns

| Pattern | Index example | Transform |
|---------|---------------|-----------|
| Unclosed paren gloss on output | `d ɡ → t k (may have been part of a more sweeping merger` | parse: strip to `comment` |
| Pronunciation gloss | `e (= /ə/?)` | parse: strip `(= …)` |
| Missing `/` before env | `χ → h #_`, `ə → ∅ VC_CV`, `s → c& _` | parse: `peel_glued_env_from_output` |
| Glued `/` without space | `ʔ → ∅/ _#` | parse: strip leftover `/` on output |
| Env-shaped last chain stage | `∅ → dz → î_V` (siblings `∅ → dz / î_V`) | parse: last stage → `env` |
| Spaced parallel parenthetical | `eː ow → ej (əw)` | compile: unwrap `(əw)` → `əw` |
| Concatenated deletion column | `{C}∅` | compile: drop glued `}∅` (ticket 60 mixed-null policy) |

Unclosed paren strip applies to **stages only**. Env/exception keep unclosed `(` so compile `_strip_editorial_parentheticals` can still drop a gloss Index split across `except` / `!` (Shetland `(! K = w ?)`). Set and feature-matrix parentheticals (`({C,#}V[-long])`, `V[+high -ATR]`) stay in stages; `=` still marks equation/pronunciation glosses.

### Inventory

Claim baseline: **8186 / 9685 ok (84.5%)**; sections all OK **310 / 712**; `forget a '/'` **68**; `syntax_other` **447**.

| Metric | Before | After | Δ |
|--------|-------:|------:|--:|
| OK / total | 8186 / 9685 (84.5%) | **8225 / 9689 (84.9%)** | **+39 ok** (+4 rows) |
| Sections all OK | 310 / 712 (43.5%) | **318 / 712 (44.7%)** | **+8** |
| `syntax_other` | 447 | **426** | **−21** |
| `forget a '/'` residual | 68 | **47** | **−21** |
| Near-miss cluster (23) | 0 ok | **14 / 23 (61%)** | ≥60% |

**Recovered near-miss:** unclosed/editorial `(` (Batak, Franconian, Dutch, Vandalic, Tutchone, Iroquoian, Lists 2–3, Turkic, Sakha), glued `#_` (Quito, Riobamba), chain env (Eritai), GVS `ej (əw)`.

**Residual near-miss (9):** `c&` metathesis (Karamiananen); ellipsis `r…∅`; palatal `Cʲ`; glottal `Vˀ`; voiceless `l̥`; stacked `:[+stress]`; Arapaho and Gros Ventre `{C,#}` word-boundary in I/O (compile drops glued `}∅` but ASCA still rejects `#` in I/O); Rhaeto prose env `final syllables` (left this error class → `expected_underscore`).

No `asca_guess` fixture updates — tests assert guess-row count only; html_extract outcomes for those rows unchanged.

**Code:** `peel_glued_env_from_output` in `parsing.py`; unclosed/`=` glosses in `gloss.py`; `drop_concatenated_deletion_column` in `slash_boundary.py`; spaced `(əw)` unwrap in `parenthetical.py`; `SoundChangeRule` peels glued env when `env` is absent.

## References

- [Spike: syntax_other near-miss sections](64-spike-syntax-other-near-miss-sections.md)
- [Correction pass: parenthetical segment notation](48-correction-pass-parenthetical-segment-notation.md)
- [Correction pass: input optionals to env](51-correction-pass-input-optionals-to-env.md)
- [Correction pass template](13-correction-pass-template.md)
