# Structured rule conditioning — session exploration (2026-09-07)

Exported from agent session on the [Cleaned rule index SoT](../map.md). Companion grilling tickets: [122 — proximity conditions](../issues/122-grill-proximity-conditions-yaml.md), [123 — applicability, dialect, sporadic, and phased rollout](../issues/123-grill-applicability-dialect-sporadic-conditions-yaml.md).

---

## Part 1 — Parse-time vs compile-time data models (reference)

### Parse-time representation (YAML SoT)

The parse-time model is an **applier-neutral rule index**: opaque Index-shaped strings in YAML, not an ASCA AST.

**Document shape**

| Level | Fields |
|-------|--------|
| **Top-level** | `sections` array (top-level `abbreviations` retired from parse output) |
| **Sound-change section** | Required: `section` (title), `index` (dotted ancestry key). Optional: `citation`, section-level `comments`, `rules`, `status: skipped` |
| **Corpus rule** | Required: `stages`, `raw`, `rule id`, `source`. Optional: `env`, `exception`, `status`, `sporadic`, `comment` |

**`stages` spine**

- Length 2 — single change (`stages[0]` → `stages[1]`)
- Length ≥ 3 — chain; compile expands adjacent pairs (one HTML line stays one corpus rule)
- Length 1 — missing arrow; compile supplies empty output
- `stages: []` + `status: skipped` — hold-out

`env` / `exception` are rule-level (at most one each), not per-stage. Field values in `stages`, `env`, and `exception` are **opaque Index-shaped strings**.

**Documentation references**

| Topic | File | Lines |
|-------|------|-------|
| Full schema table (corpus rule fields) | [issues/03-yaml-schema-cleaned-rule-index.md](../issues/03-yaml-schema-cleaned-rule-index.md) | 33–46 |
| Spec “Corpus schema and source of truth” | [spec.md](../spec.md) | 95–107 |
| `stages` replaces `input`/`output` | [docs/adr/0011-index-rule-stages.md](../../docs/adr/0011-index-rule-stages.md) | 1–15 |
| Applier-neutral principle | [docs/adr/0002-applier-neutral-yaml-rule-index.md](../../docs/adr/0002-applier-neutral-yaml-rule-index.md) | 1–18 |
| Glossary: Corpus rule, Stages | [CONTEXT.md](../../CONTEXT.md) | 66–72 |
| Parse pipeline | [docs/system/index-diachronica-parser.md](../../docs/system/index-diachronica-parser.md) | 1–8, 92–97 |

### Compile-time representation (`DiachronicSeries` + `SoundChangeRule`)

Compile is separate from YAML. YAML `stages` expand into compile fields; transforms run on those fields.

**`DiachronicSeries`** — one HTML `<h2>` section → `.rsca` parts: title, citation, comment, then `SoundChangeRule` per corpus rule (after chain expansion). Never detects optional outputs.

**`SoundChangeRule`** — four compile fields (`RuleInput`, `RuleOutput`, `RuleEnv`; exception reuses `RuleEnv`), each holding `raw` + field-token `tokens` + `compiled` ASCA string. `alternatives` for optional outputs / parallel-∅. Join at `__str__`.

**Field-token IR** (`FieldToken = str | tuple[str, ...] | OptionalLengthNode`):

- Singleton opaque string, ordered brace-set tuple, or `OptionalLengthNode` for `(ː)`
- Parallel tokens: multiple field tokens per compile field, zipped at rule level

**Documentation references**

| Topic | File | Lines |
|-------|------|-------|
| Section assembly + compile pipeline | [docs/system/sound-change-applier.md](../../docs/system/sound-change-applier.md) | 28–56 |
| Per-field compile | [docs/adr/0014-per-field-asca-compile.md](../../docs/adr/0014-per-field-asca-compile.md) | 1–16 |
| Field-token IR | [docs/adr/0015-compile-field-intermediate-representation.md](../../docs/adr/0015-compile-field-intermediate-representation.md) | 1–25 |
| Glossary | [CONTEXT.md](../../CONTEXT.md) | 74–88, 190–192 |
| Implementation | `src/conlanger/tools/rules.py`, `compile/compile_fields.py`, `compile/field_tokens.py` | — |

### Future richer representations (tickets 92, 94)

- **Ticket 92** — pydantic compile boundaries; per-field transforms; alternatives on `SoundChangeRule`; chains on `DiachronicSeries`; deferred structured IR to ticket 94.
- **Ticket 94** — field-token v1 (chosen); full syntax tree deferred to v2; ticket 71 shapes stay on string layer until v2.
- **Related deferrals** — structured segment arrays in YAML (ticket 45 Q4, rejected); parse-time inter-segment whitespace (ticket 45/46, rejected); distinctive features in env/exception (ticket 119, in progress).

---

## Part 2 — Problem statement

Several distinct Index semantics are collapsed today into `config/parser/manual_mappings.yml` string rewrites and the boolean `sporadic` flag.

### Current mechanisms

| Mechanism | When | Role |
|-----------|------|------|
| `manual_mappings.yml` (A½3) | Before structural split | Substring rewrites — including proximity and `sporadic ;` injections |
| Prose env passes (D/F) | After field split | `apply_prose_position_env_conditions`, `apply_double_slash_env_conditions`, etc. |
| `apply_sporadic_qualifier` (D1) | After split | Strips `_UNCERTAINTY_WORDS` → `sporadic: true` (`src/conlanger/utils/gloss.py`) |

### Example manual mappings (proximity — wrong for `near`)

| From | To | Issue |
|------|-----|-------|
| ` / adjacent to short u` | ` / u[-long]_, _u[-long]` | Bakes ASCA into parse; loses “adjacent” as a relation |
| ` / near emphatics` | ` / _[+ emphatic], [+ emphatic]_ ; near emphatics` | Treats **near** ≡ **adjacent** |
| ` / near consonants` | ` / C_, _C ; near consonants` | Same |
| ` / near nasals` | ` / [+nasal]_, _[+nasal] ; near nasals` | Same |

### Example manual mappings (dialect → sporadic hack)

Phrases like `in northern dialects`, `in Queensland`, `! in Queensland` are rewritten to inject `sporadic` so `apply_sporadic_qualifier` fires — conflating dialect/region conditioning with uncertainty (`sporadic`, `sometimes`).

Morphological qualifiers (`in nouns`, `in monosyllables`) overlap with ticket 107 (`strip_trailing_position_qualifiers`) and are hard to separate from geographic scope without a classifier.

---

## Part 3 — Design principle: claim, relation, resolution

```
Index prose  →  structured claim (YAML)  →  ASCA env/exception (compile, config-driven)
```

| Layer | Responsibility | Example |
|-------|----------------|---------|
| **Claim** | What Index said | “near consonants”, “in northern dialects” |
| **Relation / scope** | Kind of conditioning | `proximity: near`, `dialect_subset: northern` |
| **Target** | Segment / class / feature | `class: C`, `feature: [+emphatic]` |
| **Resolution** | ASCA projection | User config: `near` → `same_syllable` vs `adjacent` vs `within_3_segments` |

Aligns with ADR-0002 (applier-neutral YAML), ADR-0010 (historical fidelity — preserve Index claims), ADR-0011 (opaque `stages`).

---

## Part 4 — Proposed YAML additions (additive, Phase 0)

Add optional fields to **corpus rules** without changing `stages`, `env`, `exception`, or compile. Populate in parallel for validation; compile ignores until Phase 2.

### 4.1 `conditions` — phonological context atoms

```yaml
conditions:
  - id: c1                    # optional stable id
    scope: env                # env | exception
    relation: proximity       # proximity | position | stress | morphological | ...
    proximity: adjacent       # adjacent | near | same_syllable | same_word | within_segments
    target:
      kind: class             # class | feature | segment | set | prose
      value: C
    source_text: "near consonants"
    source_field: env         # env | exception | comment
```

Examples:

- `adjacent to short u` → `proximity: adjacent`, `target: { kind: segment, value: "u[-long]" }`
- `near emphatics` → `proximity: near` (not collapsed to adjacent), `target: { kind: feature, value: "[+ emphatic]" }`

### 4.2 `applicability` — when/where the rule holds

```yaml
applicability:
  kind: dialect_subset        # universal | dialect_subset | region | probabilistic | unknown
  include:
    dialects: ["northern"]
    regions: ["Queensland", "Béarn", "Gascon"]
  exclude:
    regions: ["Queensland"]
  source_text: "in northern dialects"
  confidence: attested        # attested | uncertain | editorial
```

**Classifier sketch**

| Index phrase | Suggested kind | Not |
|--------------|----------------|-----|
| `sporadic`, `sometimes`, `(?)` | `probabilistic` / `sporadic: true` | dialect |
| `in … dialect(s)`, northern/southern | `dialect_subset` | `sporadic: true` |
| Toponym (`Queensland`, `Béarn`) | `region` | sporadic |
| `in nouns`, `diminutives`, `monosyllables` | `morphological` | dialect |
| `in certain situations` | `unknown` + `comment` | forced ASCA `_` |

Distinct from ticket 68 sporadic sampling (50% apply/skip) — dialect gating is deterministic filter by user config.

### 4.3 `lexical_targets` — config-driven segment class vocabulary

Parse recognizes prose terms via `config/parser/lexical_targets.yml` (proposed):

```yaml
consonants:  { kind: class, value: C }
emphatics:   { kind: feature, value: "[+ emphatic]" }
nasals:      { kind: feature, value: "[+nasal]" }
```

Extractor emits `conditions` entries referencing config rows instead of rewriting env strings.

---

## Part 5 — Compile-time resolution config (Phase 2+)

```yaml
# config/compile/context_resolution.yml (proposed)
proximity:
  adjacent:
    strategy: immediate_neighbor    # → C_, _C
  near:
    strategy: immediate_neighbor    # legacy default (acknowledged wrong)
    # alternatives: same_syllable | within_segments: 3 | same_word

dialect:
  active: northern          # or "*"
  on_mismatch: skip         # skip | comment | apply_anyway
```

Compile: if `conditions` present → resolve via config → build compiled env/exception; else legacy opaque fields.

---

## Part 6 — Phased implementation

### Phase 0 — Extract only (low risk)

1. Document schema + `CONTEXT.md` glossary.
2. Post-parse extractor on `raw`, `env`, `exception`, `comment` → `conditions` / `applicability`.
3. Do **not** remove manual mappings; run in parallel.
4. Diagnostic report: `.scratch/rule-index/parse/structured-conditions.csv` (extracted vs current env/sporadic).
5. Compile/inventory ignore new fields.

### Phase 1 — Stop growing manual mappings

New patterns → extraction only. Remove manual rows when parity proven. Dialect phrases → `applicability`, not `sporadic ;` injection.

### Phase 2 — Compile reads structured fields

Resolvers emit into `RuleEnv` / field tokens. Applicability gating before or at render (like sporadic skip).

### Phase 3 — Retire string rewrites

Remove proximity/dialect rows from `manual_mappings.yml`; shrink prose env passes 107/108.

---

## Part 7 — Parse ordering

**Problem:** Manual mappings run at A½3 **before** split — `near consonants` becomes `C_, _C` before any extractor sees original prose.

**Phase 0:** Extract from **`raw`** and **`comment`** (manual mappings often park prose in comment tails).

**Phase 1:** New Phase **C¾** after structural split, before D transforms:

```
B½  comment peel
C   structural split
C¾  structured constraint extraction  ← NEW
D   existing transforms (skip already-extracted patterns)
```

---

## Part 8 — Relationship to in-flight work

| Effort | Fit |
|--------|-----|
| Ticket 119 (env/exception features) | `conditions[].target.kind: feature`; compile bracket→colon |
| Tickets 107/108 (prose env) | Feed extractor or become `relation: position` resolvers |
| Ticket 68 (sporadic sampling) | True uncertainty only; dialect is separate gate |
| ADR-0015 field-token IR | Resolvers emit into `RuleEnv` tokens |
| Ticket 121 (I/O bracket→colon) | Orthogonal; env/exception compile pass separate |

---

## Part 9 — Risks

| Risk | Mitigation |
|------|------------|
| Dual truth (`env` vs `conditions`) | Phase 0: compile ignores `conditions`; diff report |
| Parse order regressions | Extract from `raw` first; keep manual mappings until parity |
| Over-normalizing dialect names | Store `source_text` + optional tokens |
| Schema creep | List of small atoms; no full AST in YAML (cf. ticket 94 v2 deferral) |
| Historical fidelity | Never silently map `near` → `adjacent` in structured layer |

---

## Part 10 — Open questions (split across grilling tickets)

See [ticket 122](../issues/122-grill-proximity-conditions-yaml.md) (proximity) and [ticket 123](../issues/123-grill-applicability-dialect-sporadic-conditions-yaml.md) (everything else).
