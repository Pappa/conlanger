Type: task
Status: resolved
Blocked by:

# Correction pass: Index identity exceptions (`! Host = seg`)

Target cluster: **`expected_number`** — Index `! X = Y` where ASCA parses `=` as reference assignment (`V=1`), not Index identity (“unless this slot equals *y*”). **~35** rows in [expected_number_errors.csv](../inventory/error_clusters/expected_number_errors.csv); grill 2026-09-09 estimates **~15–20** mechanical ok-flips in v1.

Spawned from grill session on [map.md](../map.md) (2026-09-09). Related: [Grill: distinctive features in env and exception](119-grill-distinctive-features-env-exception.md) (identity bucket deferred there; bare-matrix polarity **out of scope** for this ticket).

## Context

Index Diachronica uses `! Host = segment` (or `! Host = {set}`) for **identity / grouping exceptions**. ASCA 0.10.2 treats `=` in env/exception as **reference declaration** (`C=1`), causing `Expected number` syntax errors.

**SoT policy (grill):** keep `exception: C = j` in YAML unchanged ([ADR-0010](../../../docs/adr/0010-historical-fidelity-class-first-status.md)); compile-only rewrite at ASCA emission.

### Two compile families

| Family | Index claim | Compile |
|--------|-------------|---------|
| **A — env slot binding** | Env names a class slot; exception binds that slot to a segment/set | Replace `Host` in the env token with RHS; emit as `compiled_exception`; env unchanged |
| **B — input narrowing** | Exception names the **changed** segment (focus/input host) | Append `-seg` to input (set or host token); **output unchanged**; `compiled_exception = None` |

**Do not** move negation to output. ASCA negation is input/env only.

### Worked examples (validated via `validate_asca`)

| Index | Compiled |
|-------|----------|
| `V → e / C_# ! C = j` | `V > e / C_# // j_#` |
| `r → ʔ / C_{t,w,j}# ! C = {ɡ,m,n,r,w,ʃ,x}` | `r > ʔ / C_{t,w,j}# // {ɡ,m,n,r,w,ʃ,x}_{t,w,j}#` |
| `w → ∅ / C_ ! C = K` | `w > ∅ / C_ // C:[-front,+back,+hi,-lo]_` (RHS `K` through `group_mappings`) |
| `V[-long] → ∅ / _# ! V = u` | `{V:[-long],-u} > ∅ / _#` |
| `F → F[+voice] / #_ ! F = ʍ` | `{F,-ʍ} > F:[+voice] / #_` |
| `{B,E} → ∅ / CC_{ʀ,s,t,θ}# ! B = ɒ` | `{V:[+back],V:[+front],-ɒ} > ∅ / CC_{ʀ,s,t,θ}#` (after B/E group mapping) |
| `s → z / {#,V}_{V,[+son,-syll]} ! [+son,-syll] = j` | `s > z / {#,V}_{V,[+son,-syll]} // j_{V,[+son,-syll]}` |

**Family A subscript rule:** copy the env slot’s full token suffix (subscripts, correspondence indices, trailing `#`/`_`) onto the substituted RHS — token-level splice, not bare string replace on `C`.

**Family B parallel input:** when input is a set or parallel tokens and exception targets one host (e.g. `B = ɒ` on `{B,E}`), narrow **only that member** — append `-seg` to the set or replace that token with `{Host,-seg}`.

## What to build

1. **Compile transform** `resolve_index_identity_exceptions` (name TBD) in `src/conlanger/tools/compile/asca/` — cross-field, wired in [`pipeline.py`](../../../src/conlanger/tools/compile/asca/pipeline.py).
2. **Pipeline order:** after per-field **pre-subscript** (ellipsis → series → abbreviations → superscripts → **group mappings** on all four fields), **before** `expand_subscript_references_across_fields`. Family B may need a second input touch **after** `normalize_asca_host_bracket_matrices` if narrowing runs on bracket form first.
3. **Detector (v1 — naive):** parse exception field for `Host = RHS` (optional whitespace around `=`). `Host` = class letter or postfix matrix host (`V:[+back]`, `[+son,-syll]`). `RHS` = segment literal, braced set, or class letter (expand via group mappings before splice/narrow). **No prose guard in v1** — attempt transform on all matches; record validation outcomes in **Answer**.
4. **Family A:** find env field token whose host matches exception LHS; splice RHS (+ inherited suffix) → `compiled_exception`; leave `compiled_env` as-is.
5. **Family B:** when exception LHS matches input host (including set members after mapping), append `-RHS` to input set or replace host token; set `compiled_exception = None`; do not modify output.
6. **Unit tests** from worked examples above + `validate_asca` integration where `asca` on PATH.
7. **Full inventory re-run** (`uv run create_index && uv run validate_rules`); before/after ok count, `expected_number` cluster delta, and per-rule changelog in **Answer**. List rules that still fail (prose tails, disjunction, no env) for follow-on tickets.

## Out of scope

- Bare feature-matrix exceptions (`// [-stress]`) — [ticket 119](119-grill-distinctive-features-env-exception.md); not grilled / not implemented here
- Prose / disjunction tails (`and/or`, `or one C =`, `, or when reduplicated`, `unless …`, `C = syllabic`) — acceptable v1 failures; follow-on if cluster remains
- Exception with no env and no bindable input host (e.g. `CVʕ > ħʔ ! C = ɡw`)
- Parse-time rewrite of `exception` in YAML
- `legacy/` imports

## Acceptance criteria

- [x] Cross-field compile step at documented pipeline order
- [x] Family A + Family B detectors with worked examples passing `validate_asca`
- [x] RHS class letters expanded via `group_mappings` before emission (`K` not literal `K_`)
- [x] Matrix-host splice (Mohawk) and set input narrowing (Old Norse `B = ɒ`) covered
- [x] Index `raw` / YAML `exception` unchanged (ADR-0010)
- [x] Inventory re-run with before/after + list of remaining `expected_number` failures
- [x] Docs: one row in [sound-change-applier.md](../../../docs/system/sound-change-applier.md) compile table
- [x] No imports from `legacy/`

## Comments

- 2026-09-09: Ticket filed from `/grill-with-docs` session on Index `! Host = seg` → ASCA compile (Families A/B, pipeline step 7½, naive v1 without prose guard).

## Answer

Implemented `resolve_index_identity_exceptions` in `src/conlanger/tools/compile/asca/identity_exceptions.py`, wired in `pipeline.py` after per-field pre-subscript (step 7½) with deferred Family B input narrowing after `normalize_asca_host_bracket_matrices`.

### Inventory re-run (`uv run create_index && uv run validate_rules`, 2026-09-09)

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| OK rules (`rule-inventory-success.csv`) | 8,861 | 8,881 | **+20** |
| `expected_number` cluster rows | 35 | 12 | **−23** |

20 mechanical ok-flips in changelog (timestamp `2026-09-09T19:12:09Z`).

### Per-rule changelog (ok flips)

| section | rule_id |
|---------|---------|
| 6.2.2.1.2 | Egypto-Berber-r_2 |
| 7.1 | Kennebec-River-Abenaki-w_2 |
| 7.2 | St.-Francis-Abenaki-w_2 |
| 10.3.7 | Shark-Bay-V |
| 10.3.11.1 | Anejom-C |
| 17.5.1 | Old-Irish-V |
| 17.7.1 | Gothic-—-V-long |
| 17.7.1 | Gothic-—-V-long_2 |
| 17.7.2 | West-Germanic-C |
| 17.7.2.1.13 | Yola-F |
| 17.7.3.1 | Old-Norse-B,E |
| 17.7.3.1 | Old-Norse-B,E_2 |
| 17.7.3.1 | Old-Norse-B,E_3 |
| 17.12.1.1.3 | French-V_3 |
| 17.13 | Proto-Tocharian-Kʷ |
| 17.13.1 | Tocharian-A-V |
| 30.3.1.1.8 | Adángbe-V+-nas |
| 36.1.1 | Old-Mandarin-o |
| 36.1.1 | Old-Mandarin-∅_2 |
| 37.1.2.4.1 | Mohawk-—-s_2 |

### Remaining `expected_number` failures (12 — follow-on / out of scope)

| rule_id | Reason |
|---------|--------|
| Egypto-Berber-CVʕ | No env; exception-only (`CVʕ > ħʔ ! C = ɡw`) |
| Munsee-Delaware-ʔ | Prose tail (`C = l, or when reduplicated`) |
| Proto-Norse-wuː-iː | Disjunction (`CC = NC or one C = {ʀ,j}`) |
| Central/Eastern/Northwestern/Western-Middle-Indo-Aryan-Cn (×4) | Compound host `Cn` + env `V_V` (no C slot) |
| Portuguese-N, Portuguese-C0C0 | Env matrix host `V[+nas]`, identity subscript `C=0` |
| Proto-Tocharian-H | Prose (`when [+son,-syll] = syllabic`) |
| Proto-Southern-Athabaskan-VnC | Prose (`unless C = ʔ`) |
| Modern-Pekingese-î | No env slot for `C = r` (env `_C#`) |
