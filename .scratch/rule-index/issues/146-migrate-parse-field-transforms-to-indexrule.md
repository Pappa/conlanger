Type: task
Status: ready-for-agent
Blocked by: 145

# Migrate parse field transforms from `dict` to `IndexRule`

## Question

Rewire [`parse_rule_string`](../../../src/conlanger/tools/ingest/parser.py) so the rule is a single **`IndexRule`** from line ~157 through return, using [145](145-implement-indexrule-parse-lifecycle-and-parse-raw-rule.md) — with **no** `parts: dict[str, Any]`.

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

## Transform migration rules

Same module table as before; signatures **`def apply_*(rule: IndexRule, ...) -> IndexRule`**.

Test fixtures: `IndexRule(raw="…", source="t", rule_id=None).update_rule("…").update_model()` then run transform, or set fields directly when testing post-split only.

**Dialect pass:** [`apply_dialects_to_context`](../../../src/conlanger/utils/gloss.py) on string env/exception (or `IndexContext.context` when present).

## Parser cleanup

- Remove local `working` variable and duplicate `IndexRule` constructions on the main path (one object from entry).
- Delete `extract_rule_parts`, `from_parse_fields`, `split_semicolon_comment` usage.

## Docs

Update [`docs/system/index-diachronica-parser.md`](../../../docs/system/index-diachronica-parser.md): Phase A½ uses `update_rule` on `IndexRule`; Phase B½ semicolon + structural split via **`update_model()`** (not `extract_rule_parts`).

## Acceptance

- [ ] Full pipeline on one `IndexRule`; no dict carrier on main path.
- [ ] `IndexRule.from_parse_fields` removed.
- [ ] Quality gates + byte-identical `create_index` output (zero intentional semantic change).

## Related

- [145 `update_rule` / `update_model`](145-implement-indexrule-parse-lifecycle-and-parse-raw-rule.md)
- [142](142-implement-indexrule-pydantic-and-yaml-schema.md)
