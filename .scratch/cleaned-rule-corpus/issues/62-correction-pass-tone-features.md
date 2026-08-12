Type: task
Status: resolved
Blocked by:

# Correction pass: Index tone features → ASCA `[tone: N]`

Target cluster: `unknown_feature` tone tokens — **`lowtone`** (11), **`hightone`** (8), **`fallingtone`** (3), **`lowfallingtone`** (2), **`highrisingtone`** (2) ≈ **26** rules ([inventory summary](../inventory/asca-rule-inventory-summary.md)).

Priority: **first** under the 2026-08-12 section-completeness re-prioritisation (then [63](63-correction-pass-near-miss-unknown-character.md), then re-review).

## Decision inputs (grill 2026-08-12)

- Use **global Chinese-style** defaults (ASCA doc convention): high=`5`, low=`1`, falling=`51`, low-falling=`21`, high-rising=`35`.
- Override via `manual_mappings` / section comment when a citation disagrees.
- ASCA tone syntax is **`[tone: N]`** — **no** `±`; cannot be negated. Index `V[-tone]` (at least one rule) needs a separate rewrite (drop / manual map), not a CSV rename.

## Open before coding (short probe, ~15–30 min)

ASCA docs do not spell out how `[tone: N]` composes with other matrix features on the same segment/syllable (e.g. `V:[+long][+falling tone]` → ?). **Probe ASCA 0.10.2** with mixed matrices before locking transform shape; record examples on this ticket.

### Composition probe (ASCA 0.10.2, 2026-08-12)

Docs: `[tone: X]` only; **cannot** be ± / negated ([Tone](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#tone-1)).

| Form | Result |
| --- | --- |
| `V > V:[tone: 5]` | OK |
| `V > [tone: 5]` | OK (bare matrix replace) |
| `V > V:[+long, tone: 5]` / `V:[+long,tone: 5]` | OK — tone **inside** same matrix |
| `V > V:[+stress, tone: 51]` | OK |
| `V > V[tone: 5]` (no `:`) | **Runtime:** incomplete matrix cannot be inserted |
| `V > V:[+long][tone: 5]` (adjacent matrices) | **Runtime:** incomplete matrix |
| `V > V:[tone: 5][+long]` | **Runtime:** incomplete matrix |
| `V > V[-tone]` / `V:[+long][-tone]` | **Syntax:** tones cannot be ± |
| `%:[tone: 214] > [tone:35] / _%[tone: 214]` | OK (doc sandhi) |

**Transform shape locked:** Index `[+… tone]` → `[tone: N]`; after length (`Vː` → `V:[+long]`), **merge** adjacent `[tone: N]` into the preceding matrix (`V:[+long][tone: 51]` → `V:[+long, tone: 51]`) and ensure `seg[tone:` → `seg:[tone:`. Leave `[-tone]` / `[-falling tone]` literal (hold-out / manual map).

## What to build

1. Probe composition of `[tone: N]` with length/stress/other features; note legal forms.
2. Ingest or compile normaliser: Index `[+high tone]` / `[+low tone]` / … (and collapsed `hightone` tokens) → ASCA `[tone: N]` per global table.
3. Handle `[-tone]` hold-out or manual map (do not invent `[-tone: N]`).
4. Re-run full inventory; record section-complete delta (≤3-fail near-misses preferred) and residual tone tokens.

## Acceptance criteria

- [x] Composition probe recorded (legal / illegal examples)
- [x] Global tone table applied; residuals listed
- [x] Full inventory re-run; before/after ok **and** sections-all-OK counts
- [x] Fixtures updated for intentionally changed outcomes

## Answer

**Shipped 2026-08-12.**

- **Parse:** `mapping_kind=tone` in `feature_mappings.csv` — `high tone→5`, `low tone→1`, `falling tone→51`, `low falling tone→21`, `high rising tone→35`. Only `+` polarity rewritten; `[-tone]` / `[-falling tone]` left literal.
- **Compile:** `normalize_asca_tone_matrices` after length (merge adjacent `[tone: N]`; `seg[tone:` → `seg:[tone:`). Length also merges inter-matrix `]ː[` → `, +long][`.
- **Inventory:** OK **7447 → 7456 (+9)**; sections all-OK **247 → 248 / 714** (`41.5.1.8` Proto-Gorokan to Move newly complete). `unknown_feature` **115 → 91**; collapsed `+` tone tokens (`hightone`/`lowtone`/`lowfallingtone`/`highrisingtone`) cleared — residual `fallingtone` ×2 are intentional `[-falling tone]` hold-outs.
- **Residuals (tone cluster):** ~14 Athabaskan `Vˀ > V:[tone: N]` now fail on `ˀ` (not tone); 1× `V[-tone]` (Upper Koyukon); 2× `[-falling tone]` (Oneida); Gros Ventre parallel `∅` after tone-OK matrix; Oneida `̊` / env `R`; Index `[+píng tone]` (not in global table).

## References

- [Spike: Index feature matrices → ASCA targets](29-spike-index-feature-matrices-to-asca-targets.md) — Kind 4 defer; `[tone: N]`
- ASCA 0.10.2 Tone / Suprasegmental features
- [Correction pass template](13-correction-pass-template.md)
