Type: grilling
Status: ready-for-human
Blocked by:

# Grill: pydantic compile models and per-field transforms

Owner (2026-08-21 Q8): refactor rule compilation so **`SoundChangeRule` (and the other `rules.py` classes)** become **pydantic** models; string transforms run **per field** (`input`, `output`, `env`, `exception`) **at instantiation**, not on a joined ASCA string. Intended section container name: **`DiachronicRuleset`** (today’s class is `DiachronicSeries`). This grill must finish **before** [ticket 93](93-pydantic-compile-refactor.md). **No code in this grill.**

Run `/grill-with-docs`. Implementation details are the point; do not start 93 until the frontier is empty and the owner confirms shared understanding.

## Question

How should compile-time classes in `src/conlanger/tools/rules.py` be reshaped — pydantic model boundaries, validator vs pure-function split, per-field vs cross-field transforms, join/`__str__`, alternatives, chain expansion, skip comments, and the `DiachronicSeries` → `DiachronicRuleset` rename — so ticket 93 can implement without inventing policy?

## Facts (do not re-litigate without new evidence)

- **Today:** `SoundChangeRule._format` joins `input > output / env // exception`, then `compile_asca_rule_string` rewrites that one string (`compile/asca/pipeline.py`). Corpus YAML is **`stages`**; `DiachronicSeries` expands chains, then constructs `SoundChangeRule` with `input`/`output`.
- **Pydantic** is not a current dependency; owner approved **latest pydantic** on the refactor ticket (`uv add pydantic` only when 93 is claimed).
- **Per-field is the intent.** Most transforms (ellipsis, series maps, group mappings, length, tone, apostrophe, ejective, breve) can run on one field.
- **Cross-field today:** `expand_index_subscript_references` splits the joined string and shares a `declared` set across fields, expanding **output last**. Optional-output / parallel-∅ alternatives inspect input and output together. Independent `field_validator`s cannot do that alone — likely `model_validator` (after) plus per-field validators.
- **Skip:** config-only `status: skipped` ([ticket 89](89-unify-status-skipped.md)); skipped rules are ASCA comments. Missing-arrow `stages` length 1 ([ticket 90](90-missing-arrow-single-stage.md)).
- **Prior refactor:** [ticket 39](39-refactor-sound-change-ruleset.md) extracted `compile/asca/` but kept join-then-transform. [Spike 38](38-spike-asca-compile-transform-order.md) order still applies unless this grill changes it.
- **ADR-0001 / 0002:** corpus stays applier-neutral; pydantic models are the **ASCA compile** layer, not the YAML schema.

## Edge cases to grill (non-exhaustive)

1. **Rename** — `DiachronicSeries` → `DiachronicRuleset`; `RuleTitle` / `RuleCitation` / `RuleComment` / `RulePartBase` as pydantic models too?
2. **Validator shape** — `field_validator` per field vs `model_validator` after; keep pure functions in `compile/asca/` called *from* validators?
3. **Join** — only in `__str__` / ASCA render after fields are already compiled?
4. **Chain expansion** — stays on the section model (`stages` → N rules) vs inside `SoundChangeRule`?
5. **Length-1 `stages`** — empty output policy vs omit `output` optional field.
6. **Alternatives** — child models vs a list field; RNG still instance-local.
7. **Skipped rules** — commented `raw` vs compiled-then-commented; interaction with pydantic required `input`/`output`.
8. **Group mappings / `compiler_config`** — constructor injection vs model private attrs vs context.
9. **Brassica** — one model with a format discriminator vs ASCA-only models for 93.
10. **Observable output** — must compiled `.rsca` strings match pre-refactor tests unless a grilled ordering change says otherwise?

## Outcomes

- Recorded model list, rename, validator/pure-function split, join point, chain and skip behaviour.
- Explicit “handle now / defer / won’t-fix” for cross-field transforms.
- Ticket 93 acceptance criteria updated if this grill changes them.
- **No implementation** in this ticket.
