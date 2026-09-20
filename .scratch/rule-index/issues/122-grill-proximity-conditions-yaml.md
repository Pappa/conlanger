Type: grilling
Status: resolved
Blocked by: None

**Superseded (2026-09-20):** YAML / parse schema for position → [Grill: parse-time IndexRule model](139-grill-parse-indexrule-model-and-surface-normalization.md) + [ADR structured env/exception](141-adr-structured-env-exception-indexcontext.md). Keep corpus inventory and manual_mapping retirement lists below as input to [index rule normalisation](143-implement-index-rule-normalisation-passes.md) / [compile resolver](144-implement-indexcontext-compile-resolution.md).

# Grill: position relations in the rule index YAML

Spawned from agent session 2026-09-07. Background: [structured-rule-conditioning-exploration.md](../research/structured-rule-conditioning-exploration.md) (Parts 2–4.1, 5–7, 9–10 proximity items).

Grill started 2026-09-13 (`/grill-with-docs`). **Paused 2026-09-13** — resume to close out compile config, Phase 0 acceptance, and open questions below.

## Question

How should Index **position** prose (neighbour relations like `adjacent to` / `near`, and placement relations like `medial` / `penult`, …) be represented in the **applier-neutral** rule index YAML, and how should **compile-time resolution** project those claims to ASCA env/exception — without collapsing distinct Index relations (especially **near** ≠ **adjacent**)?

Originally scoped as `conditions[]` proximity atoms; grill converged on a separate **`position`** field with a nested map schema (see **Decisions**).

## Facts (do not re-litigate without new evidence)

- Today `manual_mappings.yml` rewrites e.g. ` / near consonants` → ` / C_, _C` (treating near as immediate neighbor) and ` / adjacent to short u` → ` / u[-long]_, _u[-long]` — ASCA shapes baked in at parse ([exploration doc](../research/structured-rule-conditioning-exploration.md) Part 2).
- [prose_position_env.py](../../../src/conlanger/tools/ingest/prose_position_env.py) already normalizes some **adjacent** / **next to** phrases (`_,{set}`, `_,u` for `typically near *u`) but not the full manual-mapping set.
- [double_slash_env.py](../../../src/conlanger/tools/ingest/double_slash_env.py) handles `adjacent to another consonant` → `C_,_C` on exception tails (ticket 108); bare `penult` → `%_` (likely **wrong** — `%` is syllable boundary, not penultimate position).
- Ticket [119](119-grill-distinctive-features-env-exception.md) + [131](131-correction-pass-env-exception-feature-matrices.md) lock segment-at-focus feature policy; bare matrices compile to input colon; neighbour host matrices bracket→colon in env/exception at compile.
- Ticket [55](55-correction-pass-prose-env-medial.md) currently writes ASCA-specific `: {#_, _#}:` into `exception` at parse — **must change** (see Q1 decision).
- ADR-0002 / ADR-0010: YAML stays Index-shaped claims; ASCA projection is compile; `raw` preserves Index wording.
- Parser env vs exception asymmetry: `apply_medial_env_conditions` and `apply_prose_position_env_conditions` only rewrite `env` (medial pass **defers entirely** when `exception` already present — loses medial semantics e.g. `b → h / medially, ! {r(ʲ),l(ʲ)}_ or _ɡ`). `apply_double_slash_env_conditions` normalizes prose on both fields.

---

## Decisions (settled — do not re-open without new evidence)

### Concept and naming

- Unified concept: **position** (covers both neighbour proximity and syllable/word placement). Avoid separate `proximity` glossary term in schema.
- **near** and **adjacent** remain **distinct** stored relations; compile may default `near` → same projection as `adjacent`.
- Standardize Index surface: **`next to` → `adjacent`** at parse.
- Drop `!` in applier-neutral form — blocking is implied by `exception` field / `position.exception` scope.

### SoT schema — `position` field (v1)

Separate optional YAML field on corpus rules. **Not** embedded in `env`/`exception` strings. **Not** `conditions[]`.

```yaml
position:
  env: <relation>        # optional
  exception: <relation>  # optional
```

- At most **one relation per scope** in v1 (`env` and `exception` each optional).
- **Targets live in `env` / `exception`**, not on `position`. `position` is the relation modifier only.
- When Index line is position-only (e.g. `t → r / medially`), **omit `env`** — compile derives structural env from `position`.

**Relation enum (v1):**

| Stored value | Index surface forms (normalize to stored) |
|---|---|
| `medial` | `medial`, `medially`, `when medial` |
| `pretonic` | `pretonic` |
| `posttonic` | `posttonic` |
| `penult` | `penult`, `in the penult`, `penultimate syllables` |
| `monosyllables` | `monosyllables`, `in monosyllables` |
| `polysyllables` | `polysyllables`, `in polysyllables` |
| `near` | `near`, `typically near` (see qualifiers) |
| `adjacent` | `adjacent to`, `next to`, `unless adjacent to` (scope via field) |

**Three kinds of `env` content:**

| Kind | Example | `position`? |
|---|---|---|
| Pure structural | `_k`, `V_C`, `U#` | No |
| Target only | `C`, `{S,s,l̥}`, `[+emphatic]` | Yes — `position.env: near` or `adjacent` |
| Qualifier only | `[-stress]` | Yes — `position.env: penult` |

Compile **derives** neighbour templates (`_,{S}`, `C_, _C`, `_[+rtr], [+rtr]_`) from `(relation, env-target)` — applier-neutral env never stores `_,` wrappers or bilateral patterns for position-modified rules.

### Worked examples

```yaml
# Bare medial — t → r / medially
stages: [t, r]
position:
  env: medial

# Neighbour + set — C[+voice] → C[-voice] / next to {S,s,l̥}
stages: [C[+voice], C[-voice]]
env: {S,s,l̥}
position:
  env: adjacent

# Near class — near consonants
env: C
position:
  env: near
# compile default → C_, _C

# Near feature — near emphatics
env: [+emphatic]
position:
  env: near
# compile → _[+rtr], [+rtr]_ (feature rename at compile — see follow-on ticket)

# Unstressed penult — V → ∅ / in the unstressed penult
stages: [V, ∅]
env: [-stress]
position:
  env: penult

# Structural + exception position — k → ∅ / V_C ! penult
stages: [k, ∅]
env: V_C
position:
  exception: penult

# Blocking neighbour — b → w / ! adjacent to another consonant
stages: [b, w]
exception: C
position:
  exception: adjacent

# Structural + medial — m → β / C[-voice]_n, when medial
stages: [m, β]
env: C[-voice]_n
position:
  env: medial

# Medial + opaque exception (or deferred) — b → h / medially, ! {r(ʲ),l(ʲ)}_ or _ɡ
stages: [b, h]
position:
  env: medial
exception: '{r(ʲ),l(ʲ)}_ or _ɡ'
```

### Parser vs compiler split

| Layer | Handles |
|---|---|
| **Parser** | Extract position labels; standardize `next to` → `adjacent`; split prose into `env`/`exception` targets + `position` relations; qualifiers → `comment`; `typically` → `sporadic` + `comment` |
| **Parser relations** | `near`, `adjacent`, `medial`, `pretonic`, `posttonic`, `penult`, `monosyllables`, `polysyllables` |
| **Compiler (configurable)** | `near`, `adjacent` only — via `config/compile/context_resolution.yml` (proposed); default `near` strategy = same as `adjacent` (`immediate_neighbor`) |
| **Compiler (fixed v1)** | `medial` → `_` env + `: {#_, _#}:` exception; `penult`, `monosyllables`, `polysyllables`, `pretonic`, `posttonic` → hardcoded table (TBD at implementation) |

### Target resolution

- **`lexical_targets.yml`** (proposed) for prose keys (`consonants`, `emphatics`, `nasals`, `gutturals`, …).
- **Manual mappings run before** lexical_targets resolution at parse.
- Store prose keys at parse when mapped via config; store resolved Index tokens (`C`, `[+emphatic]`, `{S,s,l̥}`) when extractor parses directly.

### Ticket 55 / medial (change from current implementation)

- Parser output for medial: `position.env: medial` (or `position.exception` if ever attested), **not** `exception: :{#_, _#}:` in YAML.
- Compile projects medial to ASCA boundary env-set.

### Passes to retire (after Phase 1)

- [107](107-correction-pass-prose-env-positions.md) and [108](108-correction-pass-double-slash-env.md): stop ASCA rewrites for shapes that become `position` + target split.
- [55](55-correction-pass-prose-env-medial.md): stop writing `: {#_, _#}:` at parse.
- **Keep** structural Index rewrites that are not position labels (`U#`, `V_V`, `_ %[-stress]`, `#_#` for final syllables / between vowels / unstressed syllables / monosyllables structural encoding — **or** re-evaluate whether some become `position` labels at resume).

### Qualifiers

- Trailing `, in monosyllables|polysyllables|nouns` on structural env → strip to `comment`.
- `typically` on neighbour rules → `sporadic: true` + `comment`.

### Interim — imprecise non-local conditioning (2026-09-19)

This grill does **not** yet model claims like “**if s or z occur somewhere else in the word**” (co-occurrence elsewhere in the domain, not neighbour `position`).

Until `position` / broader conditioning schema ships, the project uses the same **temporary** approach as dialect applicability rows in `manual_mappings.yml`:

| Index substring | Manual `to` | Parse effect |
|-----------------|-------------|--------------|
| ` / if s or z occur` | ` / sporadic ; if s or z occur` | First `;` → rule comment; `sporadic: true`; remainder of phrase preserved in comment |

Implementation ticket: [137 correction pass — co-occurrence env manual mapping](137-correction-pass-manual-mapping-co-occurrence-env.md). **Phase 2 retirement:** when structured fields express non-local conditioning, remove this row and re-parse (alongside other `sporadic ;` injections per [123](123-grill-applicability-dialect-sporadic-conditions-yaml.md) Q6).

### Phasing (agreed direction)

1. **Phase 0** — Parser extracts `position` from `raw` in parallel; does **not** change `env`/`exception`/compile; parity report vs current output.
2. **Phase 1** — Compile reads `position`; retire parse-time ASCA rewrites for extracted shapes.
3. **Phase 2** — Remove `manual_mappings.yml` proximity rows; re-parse corpus.

---

## Deferred (explicitly out of v1)

- **Syllable distance:** `adjacent syllable`, `next syllable` (6 Biblical Hebrew + Anglo-Frisian skipped rules) — defer completely.
- **`or` in exceptions:** ~15 rules with `exception: … or …` (e.g. `{r(ʲ),l(ʲ)}_ or _ɡ`) — separate ticket.
- **`feature_mappings.yml` parse vs compile split:** e.g. `[+emphatic]` → `[+rtr]` at compile not parse — separate ticket (noted during `near emphatics` discussion).
- **Applicability / dialect** (ticket [123](123-grill-applicability-dialect-sporadic-conditions-yaml.md)) — unchanged.

---

## Corpus inventory (2026-09-13 grill)

### manual_mappings.yml proximity rows to retire (Phase 2)

- `adjacent to short u`, `unless adjacent to another consonant`, `adjacent to {`, `! adjacent to {`, `adjacent to a vowel`
- `near emphatics`, `near consonants`, `near nasals`, `when not near emphatics`, `near gutturals`

### Rules still carrying position prose in `env` (priority extract candidates)

1. `near ħ ʕ` — Moroccan-Arabic-ə
2. Six `… in an adjacent syllable` — Biblical Hebrew (deferred)
3. `_{m,ŋ} when posttonic … or when pretonic` — Hittite-e
4. `_n in U[+lo +posttonic]` — Hittite-e_2
5. `the unstressed penult` — French-V → `env: [-stress]`, `position.env: penult`
6. `when pretonic and immediately adjacent to a back vowel` — Old-Provençal-β_6

### Known bad rewrite

- `penult` → `%_` in ticket 108 — `%` is Index syllable boundary (→ ASCA `$`), not penultimate position. Replace with `position.exception: penult` (Muskogean-k: `env: V_C`, `position.exception: penult`).

---

## Open questions (resume grill here)

### Schema (mostly settled — confirm on resume)

- [x] Nested `position: {env?, exception?}` map — **proposed locked; confirm on resume**
- [x] Targets in `env`/`exception`; compile derives neighbour templates — **proposed locked**
- [ ] Final list: which current pass-107 structural encodings (`U#`, `#_#`, `V_V`, `_ %[-stress]`) stay as structural `env` vs become `position` labels

### Compile (not grilled to completion)

- [ ] **Q5** — Full resolver strategy catalog beyond `immediate_neighbor` (defer all except default?)
- [ ] **Q7** — ASCA emission edge cases (symmetric vs `_,{set}`) — document in compile table
- [ ] **Q14** — Hold-out policy when compile cannot express Index intent
- [ ] `penult` / `pretonic` / `posttonic` / `monosyllables` fixed compile table contents

### Parse and migration

- [ ] **Q9** — Extraction source: `raw` first (required to recover manual_mapping-destroyed prose); confirm Phase 0 extract order relative to manual mappings
- [ ] **Q10** — Parse order: extract `position` after split, **before** passes 55/107/108; extracted shapes suppress later ASCA rewrites
- [ ] **Q12** — Phase 0 parity threshold for removing each manual_mapping row
- [ ] **Q13** — Validation: position resolution affects `validate_asca` once Phase 1 lands

### Original grill questions — disposition

| # | Topic | Status |
|---|---|---|
| Q1 | Atom shape | **Superseded** — `position` nested map, not `conditions[]` |
| Q2 | Vocabulary | **Settled** — see relation enum table |
| Q3 | Target typing | **Settled** — targets in env/exception; lexical_targets + manual mappings |
| Q4 | Exception scope | **Settled** — `position.exception` + structural `exception` field |
| Q5 | Resolver catalog | **Open** — v1 likely `immediate_neighbor` only |
| Q6 | Default for `near` | **Settled** — same as `adjacent` |
| Q7 | ASCA emission | **Partial** — derive templates; details open |
| Q8 | Multiple atoms | **Settled** — one relation per scope in v1 |
| Q9–Q12 | Parse/migration | **Open** |
| Q13–Q14 | Validation/fidelity | **Open** |

---

## Outcomes (partial — grill paused)

- [x] Schema direction locked — `position` nested map (`env` / `exception` keys)
- [x] Relation enum + Index phrase mapping table (v1)
- [x] Parser vs compiler split (which relations where)
- [x] `near` default = `adjacent` at compile
- [x] Target resolution order (manual mappings → lexical_targets)
- [x] Ticket 55 medial policy change (parse label, compile ASCA)
- [x] Deferrals documented (syllable distance, `or`, feature_mappings split)
- [ ] Compile resolver config shape finalized (`context_resolution.yml`)
- [ ] Extraction source and parse-order decision
- [ ] Phase 0 acceptance criteria
- [ ] Migration plan with per-row manual_mapping retirement checklist
- [ ] CONTEXT.md glossary update (`position` field, retire position prose in Environment entry)
- [ ] Follow-on tickets filed

### Proposed follow-on tickets (file on close-out)

1. **Phase 0** — Extract `position` from `raw`; parity report; no compile change
2. **Phase 1 compile** — Read `position`; medial + neighbour projections; retire passes 55/107/108 rewrites
3. **`lexical_targets.yml`** — seed rows + parser hook
4. **`context_resolution.yml`** — `near` / `adjacent` strategies
5. **`or` in exceptions** — disjunction parsing (~15 rules)
6. **feature_mappings parse/compile split** — standardize vs ASCA projection

---

## Related

- [Grill: distinctive features in env and exception](119-grill-distinctive-features-env-exception.md)
- [Correction pass: env/exception feature matrices](131-correction-pass-env-exception-feature-matrices.md)
- [Correction pass: prose env medial](55-correction-pass-prose-env-medial.md)
- [Correction pass: prose env positions](107-correction-pass-prose-env-positions.md)
- [Correction pass: double-slash env](108-correction-pass-double-slash-env.md)
- [Grill: applicability, dialect, sporadic](123-grill-applicability-dialect-sporadic-conditions-yaml.md)
- `config/parser/manual_mappings.yml` — proximity / near rows (~lines 48–74, 265+)

## Comments

- 2026-09-07: Ticket filed from structured-conditioning exploration session. See [research/structured-rule-conditioning-exploration.md](../research/structured-rule-conditioning-exploration.md).
- 2026-09-13: Grill session (`/grill-with-docs`). Converged on `position` field (nested map), unified neighbour + placement concept, targets in env/exception. Paused before compile config finalization, Phase 0 acceptance, and CONTEXT.md update. Resume from **Open questions**.
