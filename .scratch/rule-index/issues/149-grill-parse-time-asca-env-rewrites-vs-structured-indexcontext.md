Type: grilling
Status: resolved
Blocked by: None

# Grill: parse-time ASCA env/exception strings vs structured `IndexContext`

Spawned from wayfinder session 2026-10-17. Owner input: **ASCA environment sets** (boundary templates, feature matrices in env, `//` exception tails, prose-position encodings) are still created or rewritten during **parse**; they should move to **compile-time** where possible, which may require new **parse-time representations** (structured `position`, relation templates, exception scopes) instead of ASCA literals in `context`.

## Question

Which parse passes must stop emitting **ASCA env/exception strings** into applier-neutral YAML, and what **Index-shaped or structured** representation replaces each shape until [144](144-implement-indexcontext-compile-resolution.md) projects to ASCA?

## Anchors in current code

- Prose position → ASCA literals (`U#`, `%[-stress]`, `#_[+stress]`, `V_V`, …): `ingest/utils/prose_position_env.py` (ticket 107).
- `//` env shorthand and exception tails: `ingest/utils/double_slash_env.py` (ticket 108).
- Medial pairing → `#_, _#` exception: `resolve_rule_env_exception_for_compile` + `MEDIAL_BOUNDARY_EXCEPTION` in `ingest/models/index_models.py` (compile hook today, constant lives in parse utils).
- Stress env prose → `_ when stressed` patterns: `transform_fields.normalize_stress_conditions` (ticket 22).
- Syllable-position editorial strip importing **compile** module: `ingest/utils/transforms.py` → `compile.tools.asca.syllable_position`.

## Depends on

[Grill: ASCA-shaped syntax in the applier-neutral rule index](148-grill-asca-shaped-syntax-in-applier-neutral-sot.md) — without a SoT syntax policy, “move to compile” is ambiguous.

## Deliverable

Per-pass **keep at parse / defer to compile / retire** with target schema; ordered migration notes (inventory regression strategy, `raw` unchanged per ADR-0010).

## Comments

### Code audit (2026-10-17; wayfinder session)

**Policy anchor:** [148 Answer](148-grill-asca-shaped-syntax-in-applier-neutral-sot.md#answer) — Tier C ASCA env (`U#`, `%[-stress]`, `#_[+stress]`, `//` tails, colon matrices) must not remain in SoT `context` strings; prefer `IndexContext.position` + compile projection ([144](144-implement-indexcontext-compile-resolution.md), [156](156-task-indexcontext-position-in-relation.md)).

**Parse order today** (`parser.py` after `init()`): stress (22) → prose conditional (134) → **prose position (107)** → **double-slash (108)** → syllable editorial strip (imports compile) → feature/IPA → **position extraction (143)** → dialects. Passes **107/108 run before 143**, so they still emit ASCA literals into `context` before neighbour/medial/`in` extraction can run on Index prose.

| Pass | Module | Typical SoT output today | 148 tier |
| --- | --- | --- | --- |
| 107 | `prose_position_env.py` | `U#`, `%[-stress]`, `#_[+stress]`, `V_V` | C → structured `position` + compile |
| 108 | `double_slash_env.py` | ` // ` splits, ASCA exception tails | C → structured exception + compile |
| 55/143 medial | `index_context_position.py` + compile hook | `position.medial`; compile adds `#_, _#` | B/C boundary — exception must be compile-only |
| 22 | `transform_fields.normalize_stress_conditions` | postfix `[±stress]` on hosts | B (keep at parse) |
| 119 family | feature/IPA on context | postfix matrices, not colon-on-`_` | B at parse; colon at compile ([131](131-correction-pass-env-exception-feature-matrices.md)) |

**Medial (superseded by Answer Q5 amendment):** compile merges `#_, _#` with any existing exception when `position.medial` — see Answer.

## Answer

**Resolved 2026-10-17** (owner grill). Amends the strict “no `#_, _#` in SoT” read of [148](148-grill-asca-shaped-syntax-in-applier-neutral-sot.md) for **medial** (see Q5). Spawns [Grill: syllable-structure env resolution](162-grill-syllable-structure-env-resolution.md) before fixing 107 mappings that fail compile.

### Confirmed (Q1, Q3, Q4, Q6)

| # | Decision |
| --- | --- |
| Q1 | **Regen-breaking** passes, one cluster at a time; inventory/changelog notes; no long-lived dual SoT schema. |
| Q3 | **108:** parse splits ` // ` and holds **structured** env/exception (`IndexContext`); **compile** emits ASCA `//` / exception grammar. |
| Q4 | **Reorder parse** so structured capture (143 neighbour/medial/`in`, 108 split) is not undermined by earlier passes; **retire ASCA-only** literals at parse (`%[-stress]`, `#_[+stress]`, colon matrices, ASCA `//` tails). |
| Q6 | **Keep** ticket **22** and **119** family at parse (postfix stress/features); no broad retirement in this chart. |

### Ticket 107 — keep parse rewrite, fix targets (Q2)

**Owner confirmed:** **yes** — implement the mapping fixes below (follow-on **task** after **[162](162-grill-syllable-structure-env-resolution.md)** for compile/`_` policy).

**Policy:** Continue **parse-time** prose → **Index/project env strings** in `env.context` (not a wholesale move to `position` only for these phrases). Correct wrong mappings:

| Index prose | Was (code today) | Owner target SoT string |
| --- | --- | --- |
| `unstressed syllables` | `%[-stress]` | **`U[-stress]`** |
| stressed syllable (inventory phrasing TBD) | — | **`U[+stress]`** |
| `accented or stressed monosyllables` | `#_[+stress]` | **`#U[+stress]#`** |
| `final syllables` / syllable-final variants | `U#` | **keep `U#`** |
| `between two vowels …` | `V_V` | keep until inventory says otherwise |
| `not universal?` | `_` + `sporadic` | **keep** |

**Compile gap:** many of these envs **lack `_`** and fail ASCA validation today. **Do not** block closing 149 on that — grill and implement under **[162](162-grill-syllable-structure-env-resolution.md)** first, then a **task** to apply 107 string fixes + compile projection.

### Medial and `#_, _#` (Q5)

**Policy:** **Both** representations are allowed in SoT:

1. **`position.medial: true`** (structured) — valid Index conditioning at parse.
2. **`exception: "#_, _#"`** (or equivalent in `IndexContext.context`) — valid **Index** word-boundary notation in SoT.

**Compile (owner amendment 2026-10-17):** Medial is resolved **only at compile**, in `resolve_rule_env_exception_for_compile` (or successor in `compile/` per **150**).

- When **`position.medial`** is set, compile **always** applies medial boundary material **`#_, _#`** (`MEDIAL_BOUNDARY_EXCEPTION`), including when an **exception already exists**.
- **Merge** `#_, _#` with the existing exception string (mechanical combine — exact join operator TBD in implementation; prefer Index-faithful `//` or comma join per rule shape).
- **Do not** skip medial synthesis because `exception` is non-empty.
- **Accepted risk:** merged exceptions may **duplicate** `#_, _#`, produce invalid ASCA, or disagree with HTML — likelihood treated as **low**; fix with targeted overlays or parse tweaks **only when attested examples** appear in `index_diachronica.html` / inventory.

**148 medial bullet:** do not **require** literal `#_, _#` **instead of** parsing `medial` prose; explicit `#_, _#` in source or YAML remains allowed.

### Per-pass table (migration)

| Pass | Parse | Compile | Notes |
| --- | --- | --- | --- |
| **107** prose position | **Keep** rewrite to Index env **strings**; fix table above | Project syllable env → ASCA per **162** + **156** | Blocked on **162** for underscore/focus rules |
| **108** double-slash | **Split** env/exception structure; no ASCA tails in YAML | Build `//` + exception strings | Task after 149 |
| **143** position | **Keep** medial / neighbour / `in` extraction; run **after** 107 phrase rewrite **or** merge 107 phrases into extraction (Q4 order) | Uses **144** / **156** | Reorder with 108 |
| **22**, **119** | **Keep** | Colon/bracket compile per **131** | — |
| **Medial `#_, _#`** | Optional in YAML **or** `position.medial` | **Merge** `#_, _#` into exception at compile when `position.medial` | Q5 — even if exception present |

### Follow-on tickets (Q7, revised)

| Order | Ticket | Type | Scope |
| --- | --- | --- | --- |
| 1 | **[162](162-grill-syllable-structure-env-resolution.md)** | grilling | `_` / focus / valid ASCA for `U[-stress]`, `U[+stress]`, `#U[+stress]#`, `U#`; parse vs compile split. **Blocks** 107 mapping implementation. |
| 2 | *Task (file after 162)* | task | Implement owner 107 string targets + tests; regen inventory delta. |
| 3 | *Task (file after 162 or parallel)* | task | **108** structured split + compile projection (Q3). |
| 4 | *Task* | task | **Parser reorder** (Q4): single ordered env pipeline; no Tier C ASCA at parse. |
| 5 | **[156](156-task-indexcontext-position-in-relation.md)** | task (existing) | `position.in` compile; overlaps syllable env — coordinate with **162**. |

**Not in this wave:** **153** (`%`/`$`), **150** (package seams — unblocked now that **149** is resolved).

### Regression

`raw` unchanged (ADR-0010). Accept `ok` churn on regen when 107/108/mappings change; document in correction summary.
