Type: task
Status: ready-for-agent
Blocked by: None

# Store compiled ASCA fields on SoundChangeRule; join at render

Spawned from closing [ticket 93](93-pydantic-compile-refactor.md) (2026-08-29). Grill [92](92-grill-pydantic-compile-refactor.md) Q4–Q5 and [ADR-0014](../../../docs/adr/0014-per-field-asca-compile.md) required compiled **field strings** at instantiation and join only at `__str__`. 93 shipped per-field transforms and byte-identical `.rsca`, but still joins into `value` at construction while `input` / `output` / `env` / `exception` stay Index-raw.

[Ticket 94](94-grill-structured-soundchangerule-ir.md) is blocked on this seam.

## Problem

After 93:

- Alternatives detection still correctly uses **raw** I/O (keep that).
- Transforms already run per field, then `compile_asca_rule_fields` **joins** and stores the blob on `value`.
- `__str__` only prefixes `value`; it does not join.
- Field isolation (`validate_asca_part`) reads `SoundChangeRule.input` etc. — still Index-shaped, not the compiled strings whole-rule `ok` used.

## What to build

1. At `SoundChangeRule` instantiation (after alternative detection on **raw** I/O): write **compiled** strings onto `input`, `output`, `env`, `exception`.
2. Join those compiled fields only in `__str__` / render (`join_asca_rule_fields`). Do not keep a pre-joined compile blob as the source of truth.
3. Skipped rules unchanged: no field compile; render `#\t` + `raw`.
4. Inventory: field isolation and alternative reconstruction must use **compiled** field strings for `validate_asca_part`, and must **not** double-compile by stuffing compiled text back through `stages` as if it were Index YAML.
5. Prefer byte-identical `.rsca`. If any `DiachronicSeries` / `SoundChangeRule` unit-test **render** strings change, list each in **Answer** with justification.

## Acceptance criteria

- [ ] After construction, `input` / `output` / `env` / `exception` are compiled ASCA field strings (Index-raw only for skipped rules)
- [ ] `__str__` joins those fields; no join-then-store as the compile SoT
- [ ] Alternative peers still detected from **raw** I/O before field compile
- [ ] Field isolation `validate_asca_part` fragments match the compiled fields whole-rule validation used
- [ ] Reconstructing an alternative for inventory does not run the compile pipeline twice on the same text
- [ ] Full gate: `uv run pytest`; `uv run ruff check --fix`; `uv run ruff format && uv run ruff format --check src`

## Out of scope

- Structured column/set IR ([94](94-grill-structured-soundchangerule-ir.md))
- Changing index YAML
- Brassica
- Reordering spike-38 transforms

## Agent Brief

**Category:** enhancement
**Summary:** Make `SoundChangeRule` hold compiled field strings and join them only when rendering `.rsca`

**Current behavior:**
Per-field ASCA transforms run at construction, then the four fields are joined into `value`. The public `input` / `output` / `env` / `exception` attributes remain Index-raw. `__str__` prefixes `value`. Field isolation validates those raw attributes. Alternative detection already uses raw I/O (correct).

**Desired behavior:**
After alternative detection on raw I/O (or when there are no alternatives), the four compile fields become the compiled ASCA strings. Render joins those strings with the existing field separators. Skipped rules still emit `#\t` plus `raw` with no field compile. Inventory field-blame and alternative rows validate the compiled field strings and do not feed compiled text back through index `stages` for a second compile.

**Key interfaces:**
- `SoundChangeRule`: `input`, `output`, `env`, `exception` are compiled after init (except `status: skipped`)
- Render: join compiled fields at `__str__` (same separators as today’s `.rsca` lines)
- Compile helpers: per-field compile may return the four strings without joining; join stays a render-only helper
- Inventory: `validate_asca_part` fragments are the compiled fields; alternative fan-out still starts from raw I/O members

**Acceptance criteria:**
- [ ] Constructed non-skipped rule exposes compiled field strings on the four attributes
- [ ] `str(rule)` equals join of those attributes (plus the usual tab / skip prefix)
- [ ] `_build_alternatives` (or equivalent) still inspects raw I/O, not compiled fields
- [ ] Field isolation uses compiled fragments; no second compile of already-compiled alternative text via `stages`
- [ ] Existing `.rsca` unit-test renders stay byte-identical, or each change is listed in **Answer**
- [ ] Full gate green

**Out of scope:**
- Ticket 94 structured IR
- Index YAML schema
- Brassica compiler
