Type: task
Status: resolved
Blocked by: None

# Parse: extract `IndexContext.position` for neighbour and medial relations

**Supersedes (2026-10-11):** prior wording about pre-split **index rule normalisation** (`str → str` passes and `apply_index_rule_normalisation`). Grill consensus: prose canonicalisation stays in **`manual_mappings.yml`** (definition order); this ticket owns **post-split** extraction of structured **`IndexContext.position`** on `env` / `exception`. Compile projection → [144](144-implement-indexcontext-compile-resolution.md).

## Question

After `manual_mappings` and structural split, how should parse represent Index **adjacent**, **near**, and **medial** conditioning in applier-neutral YAML — without baking ASCA neighbour templates (`C_, _C`) or medial boundary strings into the index SoT?

## Answer

### In scope (v1 relations)

| Relation | Typical Index surface (after manual_mappings) | Parse output (illustrative) |
| --- | --- | --- |
| `adjacent_to` | `adjacent to C`, `adjacent to {s,z}`, `adjacent to V[+nasal]` | `IndexContext(position={"adjacent_to": <target>})` with **`context` omitted or empty** when the only env material is that target (do not duplicate `C` in both `position` and `context`) |
| `near` | `near C`, `near {ħ,ʕ}`, … | `IndexContext(position={"near": <target>})` — same **no duplicate target in `context`** rule |
| `medial` | bare `medial` / `medially` / `when medial`; suffix `… when medially` on env | `IndexContext(position={"medial": true})` with structural remainder in `context` when present; **do not** set parse-time `exception: "#_, _#"` (compile applies medial boundary per [144](144-implement-indexcontext-compile-resolution.md)) |

- **`near` and `adjacent_to` are distinct** in YAML; compile defaults `near` to the same template as `adjacent_to` when config is silent ([144](144-implement-indexcontext-compile-resolution.md)).
- **No** parse-time rewrite of `near X` / `adjacent to X` → `X_, _X`. Comment out the `#region near replacements` regex block in `config/parser/manual_mappings.yml` when extraction covers those surfaces (keep other manual rows unchanged).

### Pipeline

1. Unchanged through **corrections → manual_mappings → section_mappings →** `IndexRule.init()` (structural split).
2. New pass(es) on each `env` / `exception` **`IndexContext`**: read `context` string (and merge with existing `position` if any), write structured `position` + trimmed `context`.
3. **Remove** from the parse pipeline (replace, do not guard-and-keep):
   - `apply_medial_env_conditions` (medial → structured `position` only).
   - **Adjacent / near** branches inside `normalize_bare_prose_position_env` / `apply_prose_position_env_conditions` (other phrases in that module — final syllable, between two vowels, etc. — **stay** until a separate audit ticket).
4. Audit overlap with `apply_double_slash_env_conditions` for the same three relations in a **follow-on ticket** (not blocking 143 v1).

### Withdrawn

- Delete `apply_index_rule_normalisation` and its call site; remove from [ADR-0016](../../../docs/adr/0016-parse-pipeline-order-and-raw-semantics.md) and [index-diachronica-parser.md](../../../docs/system/index-diachronica-parser.md) Phase A½.
- Do **not** add replacement pre-split hook unless a later ticket needs it.

### Out of scope

- Retiring or reshaping `manual_mappings.yml` beyond commenting out the **near template** regex region when extraction lands.
- `penult`, `//` shorthand, prose conditional env, catch-all `else`, nested-set flatten.
- Full deletion of legacy env regex passes (separate audit ticket(s)).
- Dialect / sporadic manual rows.

## Acceptance

- [x] `apply_index_rule_normalisation` removed; docs + ADR-0016 updated (A½: corrections → manual → section only).
- [x] Post-split extraction for `adjacent_to`, `near`, `medial` on `env` and `exception` where applicable.
- [x] Legacy medial pass removed; YAML no longer carries medial boundary exception strings from parse (compile adds via [144](144-implement-indexcontext-compile-resolution.md)).
- [x] `#region near replacements` manual regex rows commented out with a one-line reason pointer to this ticket.
- [x] Tests: ADR-0017-style round-trips + rule-id fixtures from inventory for the three relations.
- [x] `uv run create_index` regen documented; **`uv run validate_rules` ok count must not regress** (compile resolver must be sufficient — coordinate with [144](144-implement-indexcontext-compile-resolution.md) if split across PRs).

### Resolution (2026-10-17)

- **Code:** `apply_index_context_position_extraction` in [`index_context_position.py`](../../../src/conlanger/ingest/utils/index_context_position.py); wired in [`parser.py`](../../../src/conlanger/ingest/parser.py) after feature/IPA on `context` (parser doc D6).
- **Regen:** structured `position` on corpus rules in `data/diachronica/index_diachronica.yml`.
- **Validation:** `uv run validate_rules` (2026-10-17) — **9045** ok / **254** fail / **542** skipped; **0** ok-flips in changelog (compile [144](144-implement-indexcontext-compile-resolution.md) sufficient).

## Related

- [139](139-grill-parse-indexrule-model-and-surface-normalization.md) (intent; normalisation **name** withdrawn for this ticket)
- [141 ADR / 0017](../../../docs/adr/0017-structured-env-exception-indexcontext.md)
- [144 compile resolver](144-implement-indexcontext-compile-resolution.md)
- [122](122-grill-proximity-conditions-yaml.md) (inventory input; schema superseded by 141)

## Comments

- 2026-10-11: Scope rewritten after grill-with-docs (`map.md`); owner: manual_mappings stay; parse emits structured `position`; compile templates in 144.
