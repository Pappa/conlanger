Type: grilling
Status: resolved
Blocked by: None

# Grill: distinctive features in env and exception blocks

Spawned from wayfinder session on [Cleaned rule index SoT](map.md) (2026-09-05). Owner is revising `config/parser/manual_mappings.yml` and `config/parser/index_diachronica_corrections.yml` before this grill runs.

## Question

How should **distinctive-feature matrices** in Index **`env`** and **`exception`** fields be represented in the **applier-neutral** rule index, and how should compile rewrite them to valid ASCA?

Decide policy for bare matrices (`/[+stress]`, `// [+stress]`), segment-at-focus stress/length (`/ unstressed`, `/ stressed`), interim `_:[+feature]` placeholders, and related shapes — **before** a compile correction pass or wholesale manual-mapping rollout.

## Facts (from ASCA 0.10.2 + local validation; do not re-litigate without new evidence)

- ASCA `=` in env/exception is **reference assignment** (`V=1`), not Index identity (`V = a`) — see prior map session on Spanish-V_5.
- Colon in **env** attaches to **segment tokens** adjacent to `_` (e.g. `V:[+long]_#` in compensatory lengthening), **not** to `_` itself. `_:[-stress]` is a **parse error**.
- Without colon, a matrix adjacent to `_` is a **separate segment** in that slot: `_[-stress]` = focus then an unstressed segment **after** `_`; `[-stress]_` = matrix **before** `_` (different from “feature on the matched input segment”).
- Feature on the **changing segment at `_`** is idiomatically expressed on **input** with colon: `a:[-stress, -long] > ə`, `V:[-stress] > ∅ / _`.
- **Syllable-level** unstressed is distinct from segment-level: [Correction pass: prose env positions](107-correction-pass-prose-env-positions.md) maps `unstressed syllables` → `_ %[-stress]`.
- [Correction pass: when stressed / when unstressed env conditions](22-correction-pass-stress-conditions.md) handles `when stressed` / `when unstressed` prose tails on structural envs — orthogonal to bare `/ [+stress]` env-only rows.
- [What counts as a valid ASCA rule string?](01-valid-asca-rule-string.md) / [asca-rule-validity.md](../research/asca-rule-validity.md) — segment+matrix checklist.

## Answer (core policy — grill session 2026-09-07)

### Q1 — SoT shape for env/exception feature constraints → **A**

**Applier-neutral SoT** keeps Index-style postfix brackets on hosts (`C[+voice]_`, `V[-long]`) and standalone bare matrices where the claim is clearly about the changed segment (`[-stress]`, `[+stress]`). No colon-on-`_` (`_:[+feature]`) and no ASCA colon syntax in stored YAML.

### Q2 — Segment-level vs syllable-level for `/ unstressed` and `/ stressed` → **A**

Bare **`/ unstressed`** and **`/ stressed`** (no “syllable(s)”, no `%`) are **segment-level**: the **changed segment at `_`** must be unstressed or stressed. Parse maps them to standalone `[-stress]` / `[+stress]` in `env` (as in current `manual_mappings.yml`). Syllable-level prose (**`unstressed syllables`**, etc.) remains `_ %[-stress]` per ticket 107.

### Q3 — Env-only bare matrix meaning → **A**

A standalone matrix in `env` with no `_` and no neighbour template (e.g. Palauan `V → ə / unstressed` → `env: '[-stress]'`) means the **input segment at the change site** must carry that feature.

**Compile target:** move the matrix to the **input** compile field with colon form (e.g. `V:[-stress] > ə`). Distinct from neighbour-host postfix in env (Q5), which stays in env with bracket→colon on that host.

### Q4 — Exception-only bare matrix meaning → **inverse polarity on input** (owner)

A standalone matrix in `exception` blocks when the **changed segment at `_`** carries that feature — the complement of the same matrix in `env`.

**Compile target:** flip polarity and apply to **input** (e.g. `// [+stress]` → require `input:[-stress]` on the compiled rule, not a bare `// [+stress]` exception). This matches ASCA’s segment-at-focus idiom and avoids invalid `_:` exception syntax. **Identity / grouping exceptions** (`// [+son,-syll] = j`, `V = a`) remain a separate bucket (edge case 6 below).

### Immediate resolutions from Q1–Q4

| Item | Resolution |
|------|------------|
| `/ unstressed` → `[-stress]`, `/ stressed` → `[+stress]` in manual mappings | **Confirmed** — segment-at-focus; keep |
| `_:[-long]#`, `_:[+stress, -long]%` in manual mappings | **Retire from SoT** — not Index notation; replace targets with applier-neutral encodings (structural env + segment-at-focus matrix, or bare `[-long]` / `[+stress, -long]` in `env` as appropriate) before next parse regen |
| Bare `env: '[±stress]'` in parsed index | **Valid SoT** — segment-at-focus; compile rewrites to input colon |
| Bare `exception: '[±feature]'` | **Valid SoT** — blocks focus segment with that feature; compile = inverse polarity on input |
| Ticket 121 I/O bracket→colon pass | **Unblocked for env/exception policy** on segment-at-focus cases; follow-on compile pass needed for env/exception rewrites (separate from ticket 121 v1) |

Glossary updated: `CONTEXT.md` — **Environment**, **Exception**, **Feature matrix**.

### Q5 — Class-letter postfix in `env` / `exception` → **A** (grill 2026-09-13)

When a matrix is postfix on a **class letter or segment host inside a structural env/exception** (e.g. `C[+voice]_`, `V[-long]_#`, `V[-long]C_`, `! V[-long]C_#`), the matrix qualifies **that neighbour host**, not the changed segment at `_`.

**SoT:** keep Index postfix on the host (`C[+voice]_`).

**Compile target:** bracket→colon on that host **in the same field** (`C[+voice]_` → `C:[+voice]_` in compiled env/exception). Do **not** move to input (unlike Q3 bare matrices).

### Q6 — Bundled / neighbour-template envs → **A** (grill 2026-09-13)

Multi-token env strings (`_ [+rtr], [+rtr]_`, `%`-boundary templates) are **neighbour segment predicates** on the tokens they attach to — not segment-at-focus bare matrices.

**SoT:** keep Index-shaped strings unchanged (e.g. `_ [+rtr], [+rtr]_` stays `_ [+rtr], [+rtr]_` in YAML; no colon-on-`_`).

**Compile target:** bracket→colon per host token where a matrix qualifies that host; positional templates that ASCA already accepts may pass through unchanged (e.g. Egyptian-Arabic-aː validates today as `_ [+rtr], [+rtr]_`).

Retired `_:[+feature]` manual-mapping targets remain **invalid SoT** — separate cleanup, not a policy fork.

### Q7 — Validation split → **confirmed** (grill 2026-09-13)

Three pipeline stages: **Index raw** → **parsed YAML (SoT)** → **compiled ASCA**. Two validity checks: SoT schema (parse) vs applier acceptance (compile validation).

| Bucket | SoT | Compile pass | Examples |
|--------|-----|--------------|----------|
| **Invalid SoT** | Reject at parse | — | `_:[+feature]`, ASCA colon syntax in index fields |
| **Valid SoT; compile pass required** | Accept in YAML | Expected fail or wrong semantics until env/exception matrix pass | bare `env: '[-stress]'` → input colon; bare `exception: '[-stress]'` → inverse on input; `C[+voice]_` → `C:[+voice]_` in env for fidelity |
| **Valid SoT; no matrix pass needed** | Accept | OK today or structural only | `VC_CV`, `_#`; neighbour templates like `_ [+rtr], [+rtr]_` when ASCA accepts as-is |
| **Out of scope (ticket 119)** | Accept | Separate compile bucket | alpha/co-ref (`_C[α PLACE]`); identity `! Host = seg` → [128](128-correction-pass-index-identity-exceptions.md) **resolved** |

**No parse-time rewrite** into ASCA shapes — only compile changes stage 3; stage 2 stays Index-shaped per Q1 ([ADR-0010](../../../docs/adr/0010-historical-fidelity-class-first-status.md): `raw` / YAML unchanged).

#### Worked three-state examples (Q7)

| Rule | Index raw | Parsed YAML | Compiled ASCA (target) |
|------|-----------|-------------|------------------------|
| Palauan-V | `V → ə / unstressed` | `env: '[-stress]'` | `V:[-stress] > ə / _` |
| Old-Irish-s | `s → z / C[+voice]_` | `env: 'C[+voice]_'` | `s > z / C:[+voice]_` |
| Old-Irish-V_3 | `… / unstressed` | `exception: '[-stress]'` | `V:[+stress] > ∅ / …` (inverse on input) |
| Egyptian-Arabic-aː | `… / near emphatics` | `env: '_[+rtr], [+rtr]_'` | unchanged or minor host colons only |
| (retired) | — | ~~`env: '_:[-long]#'~~ | **invalid SoT** — never store |

## Follow-on (implementation — not grilled here)

1. **Compile correction pass** — [131](131-correction-pass-env-exception-feature-matrices.md) (bare → input colon; bare exception → inverse input; host postfix → env/exception colon).
2. **Manual-mapping / corrections cleanup** — retire `_:[+feature]` targets; replace with applier-neutral encodings before next parse regen (parse config; no ticket yet).
3. **Alpha / co-reference env matrices** (`_C[α PLACE]`) — separate cluster; out of scope for ticket 119.

## Related tickets / artifacts

- [Correction pass: when stressed / when unstressed env conditions](22-correction-pass-stress-conditions.md)
- [Correction pass: prose env positions](107-correction-pass-prose-env-positions.md)
- [Spike: Index feature matrices → ASCA targets](29-spike-index-feature-matrices-to-asca-targets.md) + [research](../research/index-feature-matrices-to-asca-targets.md)
- [Normalise segment feature matrices for appliers](07-normalise-segment-features.md)
- [Correction pass: I/O matrix bracket→colon](121-correction-pass-io-matrix-bracket-to-colon.md)
- `config/parser/manual_mappings.yml` — `/ unstressed`, `/ stressed`, `_:[-long]#`, `_:[+stress, -long]%`, `_[+ emphatic]`, …
- `config/parser/index_diachronica_corrections.yml` — section-local env shapes (e.g. `VC_:[-stress, -long]CV`)

## Notes

- Skills: `/grill`, `/domain-modeling` (wayfinder default for grilling tickets).
- Follow-on (after deferred items close): compile correction pass for env/exception matrix rewrites + manual-mapping / corrections cleanup for `_:[+feature]` retirement.

## Comments

- 2026-09-05: Ticket filed from map session (ASCA env colon semantics, Spanish-V_5, owner manual-mapping edits). Grill not yet run.
- 2026-09-07: Grill session (round 1). Owner confirmed Q1–Q3 (A); Q4 = inverse polarity on input at compile. Core policy recorded; edge cases deferred to round 2. `CONTEXT.md` updated.
- 2026-09-13: Grill session (round 2). Owner confirmed Q5–Q7 (A / A / validation split). Identity bucket closed by [128](128-correction-pass-index-identity-exceptions.md). Grill complete; follow-on compile pass + manual-mapping cleanup remain. `CONTEXT.md` updated.

## Grill session summary (2026-09-07)

**Round 1** asked four frontier questions on SoT encoding, segment vs syllable stress, env-only bare matrices, and exception-only bare matrices.

| Q | Topic | Owner answer | Compile consequence |
|---|-------|--------------|---------------------|
| Q1 | SoT shape | **A** — Index postfix + bare matrices; no `_:[+feature]` | Env/exception stay bracket-shaped in YAML; colon only at compile |
| Q2 | `/ unstressed` / `/ stressed` | **A** — segment-at-focus | `[-stress]` / `[+stress]` in env (not `_ %…`) |
| Q3 | Env-only bare matrix | **A** — qualifies changed segment | Move matrix to **input** with colon |
| Q4 | Exception-only bare matrix | Inverse on **input** | `// [+F]` → input with `[-F]` (polarity flip) |

**Owner Q4 rationale:** blocking “when stressed” is equivalent to requiring “unstressed” on the input segment — cleaner than invalid ASCA exception syntax and consistent with Q3’s input-side idiom.

**Not reached in round 1:** class-letter env matrices, identity exceptions, alpha/bundled features, validation split — all closed in round 2 (2026-09-13).

## Grill session summary (2026-09-13)

**Round 2** closed the deferred frontier: neighbour vs focus for class-letter postfix, neighbour-template envs, and the SoT vs compile-validation split.

| Q | Topic | Owner answer | Compile consequence |
|---|-------|--------------|---------------------|
| Q5 | Class-letter postfix in env | **A** — neighbour qualification | Bracket→colon on host **in env/exception** (`C[+voice]_` → `C:[+voice]_`) |
| Q6 | Neighbour templates (`_ [+rtr], …`) | **A** — per-host neighbour predicates | SoT unchanged; compile colons per host where needed |
| Q7 | Validation split | **Yes** — A/B/C/D buckets | Invalid: `_:[+feature]`; valid SoT compile failures expected until pass; no parse-time ASCA rewrite |
