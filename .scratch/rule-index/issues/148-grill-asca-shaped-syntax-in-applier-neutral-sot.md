Type: grilling
Status: resolved
Blocked by: None

# Grill: ASCA-shaped syntax in the applier-neutral rule index

Spawned from wayfinder session 2026-10-17 on [Cleaned rule index SoT](../map.md). Owner input: Index Diachronica **Symbol** normalisation and other parse-time surface cleanup have introduced **ASCA-specific** tokens into YAML and working-line transforms; some may be defensible as **applier-agnostic canonical** surface, others are ASCA-only and belong at compile.

## Question

For each class of non-Index surface in parsed YAML (`stages`, structured `env`/`exception` `context`, and working-line-only transforms), decide whether it may remain in the **applier-neutral SoT**, must stay **Index-shaped** until compile, or should become **structured fields** (no applier syntax in strings). Lock policy for **`normalize_symbols()`** / **`normalize_stress_marks()`** in `conlanger.utils.symbols` (Index `%` → `$`, syllable vs stem `$`, stress `”` → `segment:[+stress]`, etc.).

## Scope for the grill

| Area | Examples in tree today | Tension |
| --- | --- | --- |
| Boundary / stress symbols | `%` → `$`, `[+stress]` on segments | ADR-0013 applier-neutral YAML vs ASCA env vocabulary |
| Working line vs persisted fields | `IndexRule.update_rule(normalize_symbols(...))` before split | SoT may not match `raw` or Index HTML |
| “Canonical” cross-applier forms | `∅`, `#`, `_` already shared with ASCA | vs Brassica / future appliers |
| Historical passes | Tickets 22, 55, 107, 108 wrote ASCA env strings at parse | Retrofit vs grandfather |

## Out of grill scope (separate tickets)

- **Module placement** → [150](150-grill-parse-compile-module-seams.md).
- **Compile diagnostic dump** → [151](151-grill-validate-rules-asca-rules-yaml-diagnostic.md).
- **Inventory `ok` encoding** → [152](152-grill-inventory-ok-column-string-enum.md).
- **Structured `IndexContext` compile projection** — baseline already decided in [139](139-grill-parse-indexrule-model-and-surface-normalization.md) / [144](144-implement-indexcontext-compile-resolution.md); this grill decides **what may still be ASCA-shaped in strings** before compile.

## Deliverable

Decision table: **token or transform** → **SoT allowed?** → **if not, target** (Index surface / structured YAML / compile-only). Feeds [149](149-grill-parse-time-asca-env-rewrites-vs-structured-indexcontext.md) and implementation tickets 140–144.

## Answer

**Resolved 2026-10-17** (owner grill). Policy only — implementation via [153](153-task-atomic-syllable-symbol-compile-migration.md), feature-config split, [149](149-grill-parse-time-asca-env-rewrites-vs-structured-indexcontext.md), and CONTEXT/doc updates.

### SoT principles

1. **Applier-neutral YAML** uses Index/project surface in strings plus structured **`IndexContext`** (`position`, `dialect`). ASCA colon matrices, `//` exception grammar, ASCA tone numbers, and bundle geometry are **compile-only**.
2. **`stages`** is an ordered array of spine segments ([ADR-0011](../../docs/adr/0011-index-rule-stages.md)); **no `→` or `>` inside cleaned index fields** (chain = length ≥ 3). Retire parse-time `→` → `>` in persisted values (ticket 17 behaviour) — arrows exist only in **`raw`** / HTML.
3. **Parse-time normalisation** is allowed for phonological surface and **canonical cleaned-index feature names** (postfix `[...]` only). **ASCA host `:` modifiers** are never persisted.
4. **Regen-breaking** migration toward this policy is acceptable; acceptance requires **impact review** (inventory delta, changelog, cluster notes).

### Stress and symbols (parse vs compile)

| Transform | Layer | Target in SoT |
| --- | --- | --- |
| Index stress mark `”` | **Parse** | Postfix distinctive feature, e.g. `V[+stress]` or bare `[+stress]` at focus — **not** `V:[+stress]` or orphan `:[+stress]` |
| Index `%` / stem `$` | **Compile** (ASCA) | Keep Index `%` and `$` in SoT; atomic move [153](153-task-atomic-syllable-symbol-compile-migration.md) |

### Feature mappings (two configs)

| Config | Role |
| --- | --- |
| `config/parser/feature_mappings.yml` | **Index → canonical cleaned-index** names (e.g. `voiced`→`voice`, `stressed`→`stress`, `palatalized`→`palatal`); postfix bracket syntax unchanged |
| `config/compile/asca/feature_mappings.yml` (new) | **Canonical index feature → ASCA** (renames like `voice`→ASCA `voice`, `sibilant`→`strident`, **all `tone` rows**, **bundle expansions** for place/manner/vowel geometry, polarity inverts that are ASCA-specific) |

Owner approves final row lists before implementation. Corpus may **revert** parse-time ASCA names (`[+strident]`, etc.) back toward canonical index names on regen.

### Tier policy (confirmed)

**Tier A — Index / cleaned-index surface (allowed in SoT strings)**

- Subscripts, class letters, sets `{…}`, Index `#`/`∅`/`*`, Index `%` and `$`, Index optionals `(ː)` / `(X)` in stages **until** a dedicated pass says otherwise (see optionals below).
- **Optionals in sets/stages:** do **not** cartesian-expand `(X)` to `{…}` at parse by default ([grill 71](71-grill-paren-and-parallel-set-notation.md) / [100](100-spike-io-optionals-asca-and-convention.md)); parse **P4** `flatten_nested_sets` only for nested `{}`. Optional-length `(ː)` and cartesian I/O remain **compile** ([104](104-correction-pass-parenthesized-optional-length-marker.md), [111](111-correction-pass-cartesian-io-optionals.md)).
- Example spine `a(ː)` / `e(ː)` in **stages** array elements — no embedded rule arrow; env in separate field.

**Tier B — Project phonology (allowed)**

- `∅`, `#`, `_`, `V_V`, neighbour templates with postfix matrices on hosts, bare `[+stress]` / `[-stress]` at focus, structured `position` / `dialect`.
- **`#_, _#`** remains valid in SoT when Index means **word boundaries** — **not** as the stand-in for **medial** (medial → structured `position.medial` only).

**Tier C — ASCA-only (not in SoT strings)**

- Colon host matrices (`V:[+long]`), ASCA env sets / syllable encodings (`U#`, `_ %[-stress]` in **context** strings), ASCA `[tone: N]`, expanded bundle feature lists inside brackets at parse.
- **Medial:** do not persist medial as `exception: '#_, _#'`; use structured `position` + compile projection ([149](149-grill-parse-time-asca-env-rewrites-vs-structured-indexcontext.md)).
- **Syllable position `U#`:** prefer structured `position` (e.g. `in: U#`) — **own implementation ticket** (not this grill).
- **Sporadic:** always **`sporadic: true`** on the index rule at parse; compile/`SoundChangeRule` keeps existing apply-vs-skip sampling ([ticket 68](68-sporadic-sampling.md)). Do **not** treat `sporadic ; …` ASCA-shaped tails in env as durable SoT — migrate manual_mapping injections toward `sporadic` + **`comment`** / future applicability ([123](123-grill-applicability-dialect-sporadic-conditions-yaml.md)).

### Docs / glossary

- **148** records policy on the ticket and map; **update `CONTEXT.md`** (Symbol, Feature matrix, stages, Environment) when implementing splits — authoritative terms stay there today.
- **No `GLOSSARY.md` yet**; extracting glossary-only terms from `CONTEXT.md` into root `GLOSSARY.md` per domain-modeling skill is a **optional follow-on task**, not required to close 148.

### Follow-on

- [153](153-task-atomic-syllable-symbol-compile-migration.md) — `%`/`$`
- [149](149-grill-parse-time-asca-env-rewrites-vs-structured-indexcontext.md) — env rewrite retirement
- Task (to file): split `feature_mappings.yml`, rewrite `normalize_stress_marks`, remove persisted `→`/`>` normalisation, stress/doc sync
