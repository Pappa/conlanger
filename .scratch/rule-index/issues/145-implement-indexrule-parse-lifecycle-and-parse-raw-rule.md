Type: task
Status: resolved
Blocked by: 140

# Implement `IndexRule` working line, `update_rule()`, and `update_model()`

## Question

How should **`IndexRule`** carry the parse working line from entry through overlays, then derive `stages` / `env` / `exception` — without a separate factory or public `working_line` field?

## Decision

### Construction at parser entry (~line 157)

In [`parse_rule_string`](../../../src/conlanger/tools/ingest/parser.py), create **`IndexRule` immediately** at the start of the function body (before skip/correction branches). Constructor requires only corpus identity fields:

```python
rule = IndexRule(raw=raw, source=source, rule_id=rule_id or None)
```

- **`raw`** — HTML extract only ([ADR-0016](../../../docs/adr/0016-parse-pipeline-order-and-raw-semantics.md)); never overwritten by corrections.
- On construction, initialise the internal working copy from **`raw`** (see below). No `working_line` constructor argument.

**Skipped rules:** same entry `IndexRule(...)`, then set `status` / `comment` / empty `stages` and return — no `update_model()`.

### Internal working line (pseudo-private)

| Member | Visibility | YAML / `to_index_dict()` |
| --- | --- | --- |
| `_working_line` (or Pydantic `PrivateAttr`) | Parse-time only; not part of public schema | **Never** emitted |

Do not add a public `working_line` field. YAML-loaded rules have no working line unless re-parsed.

**Read access for orchestration:** expose **`working_text() -> str`** (or equivalent) so `parse_rule_string` and str→str helpers (corrections overlay, normalisation, manual/section mappings) can read the current line without touching private attributes from outside the model module. Only **`update_rule`** mutates the working line from outside the class’s parse logic.

### `update_rule(self, text: str) -> Self`

Public mutator for the **pre-structural** phase (parser lines ~169–191 today):

- Replaces internal `_working_line` with `text`.
- Returns `self` for chaining.
- Does **not** change `raw`, `stages`, `env`, or `exception`.

Parser shape after [146](146-migrate-parse-field-transforms-to-indexrule.md):

```python
rule = IndexRule(raw=raw, source=source, rule_id=rule_id or None)
# skip branch …
if rule_id and rule_id in self._corrections:
    rule.update_rule(self._corrections[rule_id])
    ...
rule.update_rule(apply_index_rule_normalisation(rule.working_text()))
working, hits = apply_manual_mappings(rule.working_text(), ...)
rule.update_rule(working)
...
rule.update_rule(apply_section_mappings(rule.working_text(), self._current_section_mappings))
if is_quoted_prose_paragraph(rule.working_text()):
    ...
```

Quoted-prose branch: set `comment` (and empty `stages`) on the same `rule` object; return without `update_model()`.

### `update_model(self) -> Self`

Renamed from `parse_raw_rule`. Called **once** after quoted-prose check fails (today ~line 202), **before** field-level transforms.

Derives **public** index fields from the current **`_working_line`**:

1. **First-`;` comment peel** (today [`split_semicolon_comment`](../../../src/conlanger/tools/ingest/transforms.py)): partition on first `;`; head → `_working_line` (`.rstrip()`); tail → merge into `comment` via [`join_rule_comment`](../../../src/conlanger/tools/ingest/transforms.py). Behaviour must match [`test_split_semicolon_comment`](../../../tests/conlanger/tools/ingest/test_transforms.py).
2. **`normalize_symbols`** on `_working_line` ([`normalize_symbols`](../../../src/conlanger/utils/symbols.py)).
3. Structural split — move logic from [`extract_rule_parts`](../../../src/conlanger/utils/parsing.py) / [`extract_missing_arrow_rule_parts`](../../../src/conlanger/utils/parsing.py):
   - `strip_leading_index_list_marker`
   - `split_input_output` / `split_post_arrow` / `build_stages_from_spine` or missing-arrow path
   - [`normalize_rule_arrows`](../../../src/conlanger/utils/parsing.py) on stages and string env/exception
4. Assign **`stages`**, **`env`**, **`exception`** on the model.

**Does not** modify **`raw`**. May clear or retain post-peel `_working_line` after split — document choice; prefer leaving peel-only text for debugging unless tests require clear.

Subsequent field transforms ([146](146-migrate-parse-field-transforms-to-indexrule.md)) mutate **`stages` / `env` / `exception` / `comment` / `sporadic`** via the model interface — not by re-parsing `_working_line`.

### Retire public `extract_rule_parts`

- Remove from public API of [`conlanger.utils.parsing`](../../../src/conlanger/utils/parsing.py); helpers stay for use inside `update_model`.
- Port [`tests/conlanger/utils/test_parsing.py`](../../../tests/conlanger/utils/test_parsing.py) to `IndexRule(raw=...).update_rule(fixture).update_model()` + field assertions.

### Retire `split_semicolon_comment` as parser API

- Logic lives inside **`update_model`** only.
- Delete or privatise in `transforms.py`.

### Field-transform interface (contract for [146](146-migrate-parse-field-transforms-to-indexrule.md))

- `stages`, `env`, `exception`, `comment`, `sporadic`, `status` — as today on the model.
- `merge_comment`, `set_sporadic`, `map_stages` / `map_env` / `map_exception` (or equivalent) for transforms.
- Transforms: **`IndexRule -> IndexRule`** (`model_copy` per step preferred).

### Remove `IndexRule.from_parse_fields`

In [146](146-migrate-parse-field-transforms-to-indexrule.md), not 145.

## Acceptance

- [ ] `IndexRule(raw, source, rule_id?)` initialises `_working_line` from `raw`; `update_rule`, `working_text`, `update_model` implemented.
- [ ] Unit tests: semicolon + structural split parity; YAML round-trip unchanged (no working line in dump).
- [ ] `extract_rule_parts` removed from public API; semicolon not peeled outside `update_model`.
- [ ] Parser rewire is **[146](146-migrate-parse-field-transforms-to-indexrule.md)**; 145 lands with model tests only.

## Related

- [139 grill](139-grill-parse-indexrule-model-and-surface-normalization.md), [142](142-implement-indexrule-pydantic-and-yaml-schema.md)
- [146 Migrate parse field transforms to `IndexRule`](146-migrate-parse-field-transforms-to-indexrule.md)
- [77 first `;` cut](77-implement-first-semicolon-comment-cut.md)

## Answer

Implemented `IndexRule` parse lifecycle on the model: `_working_line` (`PrivateAttr`) initialised from `raw`, `working_text()`, `update_rule()`, and `update_model()` (first-`;` peel via `_split_semicolon_comment`, `normalize_symbols`, structural split via `_extract_rule_parts` / `extract_missing_arrow_rule_parts`). Retired public `extract_rule_parts` and `split_semicolon_comment` (now `_`-prefixed); parser still uses the private helpers until #146. Tests ported to `test_index_models.py`; YAML/`to_index_dict()` omit working line.
