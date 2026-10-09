Type: task
Status: ready-for-agent
Blocked by:

# Refactor parser output to `Index` / `IndexSection` / `IndexRule` (no dict carriers)

## Context

[146](146-migrate-parse-field-transforms-to-indexrule.md) moved the **per-rule parse pipeline** onto **`IndexRule`**, but **`parse_rule_string` / `parse_rule_element` still return `list[dict]`** via `to_index_dict()`, and **`IndexDiachronicaParser.parse()`** still builds **`section_obj: dict`** and returns **`{"sections": [...]}`** only.

This ticket completes the parse **document** layer: typed Pydantic models end-to-end, with **one** serialization boundary at `parse()` return.

**Grill decisions (settled):**

| Topic | Decision |
| --- | --- |
| Section container model name | **`IndexSection`** (user text “SectionIndex” was a typo). |
| Local variable in `parse()` | Rename **`section_obj`** → **`section`**, typed **`IndexSection`**. |
| Root YAML shape | Add top-level **`name`** (`"Index Diachronica"`). Existing consumers use `doc["sections"]`; they keep working; full-file snapshots may need updating. |
| Rule provenance | **`parse(source_file=…)`** still sets **`IndexRule.source`** to `"{source_file}:{line}"` (unchanged). |
| `Index` vs glossary “rule index” | Model class **`Index`** = one parsed **document** instance; glossary **rule index** = the stored YAML artifact. No `CONTEXT.md` change required. |
| Serialization | **`model_dump(exclude_none=True, mode="python")`** at **`Index`** root only for `parse()` return; inner functions return **models**, not dicts. |
| `IndexRule.to_index_dict()` | **Keep** as a thin alias to `model_dump(exclude_none=True, mode="python")` for callers/tests that still want a dict for one rule; **remove** from the main parse return path. |

## Requirements

### 1. `parse_rule_string` and `parse_rule_element`

**File:** [`src/conlanger/tools/ingest/parser.py`](../../../src/conlanger/tools/ingest/parser.py)

- Change return type to **`list[IndexRule]`** (all exit paths).
- Replace every **`return [rule.to_index_dict()]`** with **`return [rule]`** (including skip-rules, quoted-prose, and fully transformed paths).
- **`parse_rule_element`** delegates to **`parse_rule_string`** unchanged apart from typing.

**Non-goals:** No change to transform order or field semantics ([ADR-0016](../../../docs/adr/0016-parse-pipeline-order-and-raw-semantics.md)).

### 2. Section-level passes on `IndexRule`

Refactor these modules to accept and return **`IndexRule`** (and **`list[IndexRule]`** where applicable), not **`dict[str, Any]`**:

| Function | File |
| --- | --- |
| `flatten_nested_sets_in_section_rules` | [`flatten_nested_sets.py`](../../../src/conlanger/tools/ingest/flatten_nested_sets.py) |
| `flatten_nested_sets_in_rule_fields` | same |
| `resolve_catch_all_else_rules` | [`section_policy.py`](../../../src/conlanger/tools/ingest/section_policy.py) |

**`flatten_nested_sets_in_rule_fields(rule: IndexRule) -> IndexRule`:**

- Return a **copy** (`model_copy(deep=True)` or equivalent) with flattened working strings; never mutate **`raw`**.
- **`stages`:** flatten each stage string (unchanged behaviour).
- **`env` / `exception`:** when the field is **`IndexContext`**, flatten **`context`** when it is a non-empty string; leave **`position`** / **`dialect`** unchanged. Do not coerce structured-only contexts through string flatten (no `context` → skip field mutation).
- Remove dict key iteration (`for key in ("env", "exception")` on plain dicts).

**`resolve_catch_all_else_rules(rules: list[IndexRule]) -> list[IndexRule]`:**

- Preserve current complementary-`else` logic ([`section_policy.py`](../../../src/conlanger/tools/ingest/section_policy.py)).
- Replace **`append_rule_comment_parts(dict, …)`** with **`IndexRule.merge_comment`** (or equivalent on the model). Refactor **`append_rule_comment_parts`** only if it becomes unused; prefer **`merge_comment`** on the model as the single API.
- Env text resolution must use **`IndexContext`** (e.g. read/write **`context`** on the model), not bare strings on **`env`/`exception`** attributes — consistent with [146](146-migrate-parse-field-transforms-to-indexrule.md).
- When copying the previous rule’s env onto an else rule’s **exception**, assign the **`IndexContext`** object (deep copy), not a dict snapshot.

**Call site in `parse()`:**

```python
if rules:
    section.rules = flatten_nested_sets_in_section_rules(
        resolve_catch_all_else_rules(rules)
    )
```

(where **`rules`** is **`list[IndexRule]`** built from **`parse_rule_element`**).

### 3. `IndexSection` model

**File:** [`src/conlanger/tools/ingest/index_models.py`](../../../src/conlanger/tools/ingest/index_models.py)

Add **`IndexSection`** with fields aligned to today’s section YAML mapping (glossary: **sound-change section**):

| Field | Type | Notes |
| --- | --- | --- |
| `section` | `str` | Display name (today’s YAML key `section`). |
| `index` | `str` | Section index id from the `<h2>` heading. |
| `citation` | `str \| None` | First non-`schg` paragraph. |
| `comments` | `list[str]` | Further paragraphs (strings, not dicts). |
| `rules` | `list[IndexRule]` | Default `Field(default_factory=list)`; omit from dump when empty if `exclude_none` / optional empty-list policy matches current YAML (today empty `rules` key is omitted — build section without setting `rules` or use serializer omit-empty). |
| `status` | `str \| None` | e.g. `"skipped"` from `skip_sections`. |

`model_config = ConfigDict(extra="forbid", validate_assignment=True)` to match **`IndexRule`**.

### 4. `Index` document model

**Same file:** `index_models.py`

```python
class Index(BaseModel):
    name: str
    sections: list[IndexSection] = Field(default_factory=list)

    def add_section(self, section: IndexSection) -> None:
        self.sections.append(section)
```

- **`IndexDiachronicaParser.parse()`** constructs **`Index(name="Index Diachronica")`** at the start (after resetting parser state).
- For each HTML section, build **`IndexSection`**, populate fields, run rule passes, then **`index.add_section(section)`**.
- **Return:** `return index.model_dump(exclude_none=True, mode="python")`.
- Update the **`parse()`** docstring: root mapping includes **`name`** and **`sections`**.

### 5. Public exports and docs

- Export **`Index`**, **`IndexSection`** from [`src/conlanger/tools/ingest/__init__.py`](../../../src/conlanger/tools/ingest/__init__.py) alongside **`IndexRule`**, **`IndexContext`**.
- Update [`docs/system/index-diachronica-parser.md`](../../../docs/system/index-diachronica-parser.md): parse output is built from **`Index`** / **`IndexSection`** / **`IndexRule`**; note new top-level **`name`** on written YAML.

## Tests

- **`tests/conlanger/tools/ingest/test_parser.py`:** assertions on **`parse_rule_string`** results use **`IndexRule`** attributes (or **`model_dump`**) instead of dict subscripts.
- **`tests/conlanger/tools/ingest/test_flatten_nested_sets.py`:** parametrized fixtures may stay as dict **inputs** only if helpers accept **`IndexRule`**; prefer constructing **`IndexRule(raw=…, source="t", …)`** and comparing **`model_dump(exclude_none=True)`** slices or field-wise asserts.
- **`tests/conlanger/tools/ingest/test_section_policy.py`:** same migration to **`IndexRule`** / **`IndexContext`**.
- Add at least one test that **`IndexDiachronicaParser.parse()`** return value includes **`name`** and nested rules serializing **`IndexContext`** to string or mapping per existing serializers.
- Run full Python quality gates per repo rules.

## Acceptance criteria

- [ ] No `list[dict[str, Any]]` for rules in `parser.py` parse loop or in the three section-level pass functions’ public signatures.
- [ ] `parse()` return equals `Index(...).model_dump(exclude_none=True, mode="python")` with stable section/rule shape for a golden snippet.
- [ ] `create_index` / `write_cleaned_index` path still works; regenerated YAML includes document **`name`** at root.
- [ ] Behaviour unchanged for nested-set flatten and catch-all else (existing parametrized tests updated, not deleted).

## References

- [Grill: parse-time `IndexRule` model](139-grill-parse-indexrule-model-and-surface-normalization.md)
- [ADR-0017 structured env/exception](../../../docs/adr/0017-structured-env-exception-indexcontext.md)
- [`CONTEXT.md`](../../../CONTEXT.md) — **sound-change section**, **corpus rule**

## Comments

_Grilling session 2026-10-09: requirements sourced from user; ambiguities resolved in table above._
