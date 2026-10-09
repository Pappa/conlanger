Type: task
Status: resolved
Blocked by:

# Migrate parse field transforms from `dict` to `IndexRule`

## Question

Rewire [`parse_rule_string`](../../../src/conlanger/ingest/parser.py) so the rule is a single **`IndexRule`** from line ~157 through return. **[145](145-implement-indexrule-parse-lifecycle-and-parse-raw-rule.md) is resolved** (`update_rule` / `update_model` on the model); this ticket completes parser + transform migration — **no** `parts: dict[str, Any]`.

## Target `parse_rule_string` shape

```python
rule = IndexRule(raw=raw, source=source, rule_id=rule_id or None)
# skipped → status/comment/stages, return

if rule_id and rule_id in self._corrections:
    rule.update_rule(self._corrections[rule_id])
    ...
rule.update_rule(apply_index_rule_normalisation(rule.working_text()))
working, hits = apply_manual_mappings(rule.working_text(), self._manual_mappings)
rule.update_rule(working)
...
rule.update_rule(apply_section_mappings(rule.working_text(), self._current_section_mappings))

if is_quoted_prose_paragraph(rule.working_text()):
    # set comment, stages=[], return [rule.to_index_dict()]

rule.update_model()
rule = apply_series_expansions(rule, ...)
...
return [rule.to_index_dict()]
```

Field-transform order unchanged from current `parser.py` (~210–226).

## `env` / `exception`: `IndexContext` only

On **`IndexRule`**, **`env`** and **`exception`** are typed **`IndexContext | None`** only. Remove **`EnvExceptionField`** and the `str | IndexContext` union from [`index_models.py`](../../../src/conlanger/ingest/models/index_models.py). Parse-time code must not store bare strings on those attributes.

### Construction and `update_model()`

After structural split, assign:

```python
self.env = IndexContext(context=env_str) if env_str else None
self.exception = IndexContext(context=exc_str) if exc_str else None
```

(`env_str` / `exc_str` from former dict keys; arrow-normalised strings.)

### YAML load (`model_validate` / ingest)

**Before** validators on `IndexRule.env` / `IndexRule.exception`:

- YAML **string** → `IndexContext(context=that_string)`
- YAML **mapping** → `IndexContext.model_validate(mapping)`
- absent → `None`

No public `str` on the model after validation.

### YAML dump (`to_index_dict` / `IndexRule` serialization)

Serialization is **`IndexContext`’s responsibility** (custom serializer, `@model_serializer`, or `IndexRule.to_index_dict` delegating per field — pick one place, document it).

| `position` | `dialect` | Emitted shape for that `env` / `exception` |
| --- | --- | --- |
| `None` | `None` | **Scalar string** — the `context` value (must be non-`None` when the field is present; omit field entirely when `env`/`exception` is `None`) |
| any non-`None` | any | **Object** — `model_dump(exclude_none=True)` of `IndexContext` (same keys as [ADR-0017](../../../docs/adr/0017-structured-env-exception-indexcontext.md)) |

Examples:

- `IndexContext(context="_#")` → `env: "_#"` in YAML
- `IndexContext(context="#_", position={"adjacent_to": "C"})` → `env: {context: "#_", position: {adjacent_to: C}}`

Round-trip tests in [`test_index_models.py`](../../../tests/conlanger/tools/ingest/test_index_models.py) already expect string `env` in **`to_index_dict()`** for the simple case; keep that **wire format** while asserting **in-memory** type is `IndexContext`.

### Field transforms

All transforms that today read/write `parts["env"]` / `parts["exception"]` strings must go through **`IndexRule`** helpers, e.g.:

- `map_env_context(fn: Callable[[str], str])` — no-op when `env is None`; updates `env.context` in place (or via `model_copy`)
- same for `exception`
- when a pass **introduces** `position` or `dialect`, the field stays (or becomes) a full object dump on emit

**Dialect pass:** [`apply_dialects_to_context`](../../../src/conlanger/utils/gloss.py) operates on **`env.context` / `exception.context`** strings (create `IndexContext(context=…)` if needed).

## Transform migration rules

Same module table as before; signatures **`def apply_*(rule: IndexRule, ...) -> IndexRule`**.

Test fixtures: `IndexRule(raw="…", source="t", rule_id=None).update_rule("…").update_model()` then run transform, or set fields directly when testing post-split only (`IndexContext(context="…")` for env/exception).

## Parser cleanup

- Remove local `working` variable and duplicate `IndexRule` constructions on the main path (one object from entry).
- Delete `extract_rule_parts`, `from_parse_fields`, `split_semicolon_comment` usage.

## Docs

Update [`docs/system/index-diachronica-parser.md`](../../../docs/system/index-diachronica-parser.md): Phase A½ uses `update_rule` on `IndexRule`; Phase B½ semicolon + structural split via **`update_model()`** (not `extract_rule_parts`).

## Acceptance

- [x] Full pipeline on one `IndexRule`; no dict carrier on main path.
- [x] `env` / `exception` are `IndexContext | None` in memory; `EnvExceptionField` removed.
- [x] Dump: context-only → string; any `position` or `dialect` → object; load accepts both legacy string and object YAML.
- [x] `IndexRule.from_parse_fields` removed.
- [x] Quality gates + byte-identical `create_index` output (zero intentional semantic change).

## Related

- [145 `update_rule` / `update_model`](145-implement-indexrule-parse-lifecycle-and-parse-raw-rule.md)
- [142](142-implement-indexrule-pydantic-and-yaml-schema.md)
