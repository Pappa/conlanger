Type: grilling
Status: resolved
Blocked by:

# Grill: pydantic compile models and per-field transforms

Owner (2026-08-21 Q8): refactor rule compilation so **`SoundChangeRule` (and the other `rules.py` classes)** become **pydantic** models; string transforms run **per field** (`input`, `output`, `env`, `exception`) **at instantiation**, not on a joined ASCA string. Section container stays **`DiachronicSeries`** (`DiachronicRuleset` was a typo). This grill must finish **before** [ticket 93](93-pydantic-compile-refactor.md). **No code in this grill.**

## Question

How should compile-time classes in `src/conlanger/tools/rules.py` be reshaped — pydantic model boundaries, validator vs pure-function split, per-field vs cross-field transforms, join/`__str__`, alternatives, chain expansion, skip comments — so ticket 93 can implement without inventing policy?

## Answer

**Gist:** All six `rules.py` types become pydantic `BaseModel`s. Keep **`DiachronicSeries`**. Per-field ASCA transforms at `SoundChangeRule` instantiation; join only at render. Alternatives stay on `SoundChangeRule`. Chains stay on `DiachronicSeries`. ADR: [0014](../../../docs/adr/0014-per-field-asca-compile.md). Implement: [93](93-pydantic-compile-refactor.md).

### Settled (2026-08-21)

| Q | Decision |
| --- | --- |
| 1 | No rename. **`DiachronicSeries`**. |
| 2 | `RulePartBase`, `RuleTitle`, `RuleCitation`, `RuleComment`, `SoundChangeRule`, `DiachronicSeries` are all pydantic `BaseModel`s. Title/citation/comment have no compile validators. |
| 3 | Pure functions stay in `compile/asca/`; validators orchestrate. May change later. |
| 4 | `field_validator` on the four compile fields; `model_validator(mode='after')` for subscript refs (shared `declared`, output last). Alternatives: split **raw** I/O then compile each child. |
| 5 | Join only at `__str__` / render. Drop join-then-rewrite `compile_asca_rule_string`. |
| 6 | Chain expansion stays on `DiachronicSeries`. `SoundChangeRule` never reads `stages`. Length-1 → `output=""` ([ticket 90](90-missing-arrow-single-stage.md)). |
| 7 | `group_mappings`, `compiler_config`, `section_index`, instance `Random`: `PrivateAttr` (or non-dump injection). Not corpus YAML. |
| 8 | Ticket 93 is **ASCA-only**. |
| 9 | Prefer byte-identical `.rsca`. If `DiachronicSeries` / `SoundChangeRule` **unit-test input/output strings** must change, document each change in ticket 93’s resolution with description and justification. |
| 10 | **`_build_alternatives` is the first detection of optional paths** (parse does not). Keep detection and peers on **`SoundChangeRule`**. Gates as pure functions called from its `model_validator`. No YAML alternatives field. Do not hoist fan-out to `DiachronicSeries`. |

Skip comments: config `status: skipped` ([ticket 89](89-unify-status-skipped.md)) — skipped `SoundChangeRule` bypasses compile transforms; rendered value is **`raw`**, prefix `#\t`.

## Facts (do not re-litigate without new evidence)

- **Today:** `SoundChangeRule._format` joins `input > output / env // exception`, then `compile_asca_rule_string` rewrites that one string (`compile/asca/pipeline.py`). Corpus YAML is **`stages`**; `DiachronicSeries` expands chains, then constructs `SoundChangeRule` with `input`/`output`.
- **Pydantic** is not a current dependency; owner approved **latest pydantic** on the refactor ticket (`uv add pydantic` only when 93 is claimed).
- **Per-field is the intent.** Most transforms (ellipsis, series maps, group mappings, length, tone, apostrophe, ejective, breve) can run on one field.
- **Cross-field today:** `expand_index_subscript_references` splits the joined string and shares a `declared` set across fields, expanding **output last**. Optional-output / parallel-∅ alternatives inspect input and output together.
- **Skip:** config-only `status: skipped` ([ticket 89](89-unify-status-skipped.md)); skipped rules are ASCA comments. Missing-arrow `stages` length 1 ([ticket 90](90-missing-arrow-single-stage.md)).
- **Prior refactor:** [ticket 39](39-refactor-sound-change-ruleset.md) extracted `compile/asca/` but kept join-then-rewrite. [Spike 38](38-spike-asca-compile-transform-order.md) order still applies per field.
- **ADR-0001 / 0002:** corpus stays applier-neutral; pydantic models are the **ASCA compile** layer, not the YAML schema.
- **Alternatives:** first detected in `SoundChangeRule._build_alternatives`; inventory only reads `.alternatives` afterward.

## Outcomes

- Recorded above; [ticket 93](93-pydantic-compile-refactor.md) spec replaced with this answer.
- **No implementation** in this ticket.
