Type: grilling
Status: claimed
Blocked by:

# Grill: `! Host =` env-slot exception compile (suffix policy + residuals)

Owner context (2026-10-17): ~38 Index rules use `! Host = RHS` as a **grouping exclusion** (any class letter, not only `C`). Two surface forms:

1. **Env-bound** — the host letter appears only in `env` (e.g. `r → ʔ / C_{t,w,j}# ! C = {ɡ,m,n,r,w,ʃ,x}`).
2. **I/O-bound** — the host appears in `stages` and/or env (e.g. `w → ∅ / C_ ! C = K`, `{B,E} → ∅ / … ! B = ɒ`).

Form 1 should compile by **substituting the excluded material into the env slot** (Family A in [128](128-correction-pass-index-identity-exceptions.md)). Owner asks whether exception emission can simplify from full slot suffix copy to trailing `_` only (e.g. `// {ɡ,m,n,r,w,ʃ,x}_` instead of `// {ɡ,m,n,r,w,ʃ,x}_{t,w,j}#`).

## Question

Lock compile policy for **env-slot identity exclusions** (`! Host = RHS`): when is full env-slot suffix inheritance required vs when is `// RHS_` (or `// {set}_`) sufficient; how does this relate to existing Family A/B in ticket 128; what follow-on work remains for rules still hitting `expected_number`?

## Comments

- Session opened from `/wayfinder` on [map.md](../map.md) with owner technical note (2026-10-17).
- **Paused 2026-10-17** — owner will return to finish grill; partial rounds recorded below (draft, not final policy).

### Grill progress (draft)

**Terms:** **RHS** = right-hand side of `! Host = …` (the excluded segment/set/class letter, e.g. `j`, `{ɡ,…}`, `r`).

| Round | Topic | Owner position |
| --- | --- | --- |
| Q2 | Compile-only; `! Host = RHS` is valid **applier-neutral** syntax | **Yes** |
| Q1 | Underscore simplification on Family A `//` tail | If the class letter is **not** on both sides of `_`, the “other side” of `_` can probably be discarded in the compiled exception (differs from ticket 128 full-suffix default — **unsettled**) |
| Q3 | Precedence when host in env **and** input | **Unsure** — asked for HTML examples |
| Q4 | Host on changed segment, env without host (`_# ! C = t`) | **Cannot handle** (and broadly skeptical of compile when host appears in stages/I/O) — **conflicts with ticket 128 Family B** unless rescoped |

**Corpus (38 clean `Host =` rows):** 9 env-host only, 16 stage-host only, 1 both, 1 prose garbage.

**Q3 fact — only “both” rule:** `Tocharian-A-V` (`index_diachronica.html:8297`) — `V → j / V_nʲtʲ ! V = E`. Implemented today via **Family A** in `identity_exceptions.py` (`_compile_family_a_exception` on env token `V_nʲtʲ` → `// V:[+front]_nʲtʲ`); see `pipeline.py` step calling `resolve_index_identity_exceptions` **before** Family B narrowing.

**Inventory vs compile mismatch (West-Germanic-C):** `compile_rules` writes correct `rule:` line `{C,-r} > C:[+long] / _j` with `exception.compiled: null`, but `validate_rules` deserializes via `compiled_target_serde._field_model` and sets `compiled = raw` when `compiled is None`, so `SoundChangeRule.__str__` re-attaches `// C = r` for ASCA validate. **Not** a compile transform bug; validation should not round-trip `DiachronicSeries` from YAML — tracked in [169](169-task-validate-compiled-yaml-without-series-roundtrip.md).

### Open (next grill session)

- Q5–Q8 from agent round 2 (suffix rule formalization vs `V_nʲtʲ`, rescope Family B, 16 hold-outs).
- Reconcile owner Q4 with ticket 128 (+20 ok) and serde fix for validation.

## Answer (2026-10-17, superseded — do not treat as resolved until grill completes)

### Vocabulary (align with ticket 128)

| Owner “form” | Ticket 128 family | Compile behaviour |
| --- | --- | --- |
| Host only in **env** | **A — env slot binding** | Leave `compiled_env` unchanged; replace `exception` with an ASCA `//` tail built from RHS **spliced onto the matching env slot’s suffix** (subscripts, correspondence indices, `#` / `_` anchors). |
| Host in **input/stages** (and optionally env) | **B — input narrowing** | Narrow the matching input token (`{Host,-RHS}` or set member); **`compiled_exception = None`**; output unchanged. RHS class letters expand via `group_mappings` before splice/narrow. |

SoT stays Index-shaped `! Host = RHS` in YAML ([ADR-0010](../../../docs/adr/0010-historical-fidelity-class-first-status.md)); rewrite remains **compile-only** (`resolve_index_identity_exceptions`).

### Env-slot splice (Family A)

Mechanical rule (already implemented): for each env token, if a slot host matches exception LHS, emit `compiled_exception = expand(RHS) + suffix`, where `suffix` is everything after the host on that token (e.g. `C_{t,w,j}#` → host `C`, suffix `_{t,w,j}#`).

**Worked example (owner):**

- Index: `r → ʔ / C_{t,w,j}# ! C = {ɡ,m,n,r,w,ʃ,x}`
- Compiled: `r > ʔ / C_{t,w,j}# // {ɡ,m,n,r,w,ʃ,x}_{t,w,j}#` (ticket 128 table)

### Trailing `_` simplification (`// {set}_`)

**Do not** adopt `{RHS}_` as the default when the bound env slot carries more than a bare underscore after the host.

- `// {ɡ,m,n,r,w,ʃ,x}_` is **not** equivalent to `// {ɡ,m,n,r,w,ʃ,x}_{t,w,j}#` — it drops correspondence subscripts and word-edge `#` tied to that slot.
- `// j_` is **not** equivalent to `// j_#` for `C_#` env slots.

**When `// RHS_` is correct:** only when the inherited suffix from the matched env token is exactly `_` (e.g. `w → ∅ / C_ ! C = K` → expand `K` to feature matrix, then `// C:[…]_` — not a braced set case).

Policy: **keep full suffix inheritance** (current code path). Treat owner’s `{set}_` note as a readability shortcut **only** where validation proves equivalence to the full-suffix form for that slot shape (typically bare `Host_` only).

### Corpus scale

- ~**46** rules in `index_diachronica.yml` with a `! … =` exception substring; ~**52** lines containing `C =` (includes prose tails and non-identity `!`).
- Ticket 128 cleared **23** `expected_number` rows (+20 ok). **~20** rows remain in `diagnostics/inventory/error_clusters/expected_number_errors.csv` (2026-10-17 inventory): prose/disjunction (`or when reduplicated`, `CC = NC or one C = …`), compound hosts (`Cn` with env `V_V`), identity subscripts (`C=0`), env without a bindable host (`_C#` vs `C = r`), exception-only rows, and **Family B rows where input narrowed but Index `Host = RHS` still appears in the compiled exception string** (e.g. Anejom-C — follow-on bug, not a policy change).

### Follow-on

Implementation task [168](168-task-index-identity-exception-residuals.md): clear Family B compiled exceptions, extend/env-infer hosts where safe, inventory-driven prose hold-outs unchanged from 128 out-of-scope unless a new grill says otherwise.
