Type: grilling
Status: resolved
Blocked by: None

# Grill: parse-time `IndexRule` model and working-line surface normalization

Spawned from wayfinder session 2026-09-20. Enables completion of [Grill: position relations in the rule index YAML](122-grill-proximity-conditions-yaml.md) and [Grill: applicability, dialect scope, sporadic vs conditioning](123-grill-applicability-dialect-sporadic-conditions-yaml.md) by giving the parser a typed parse-time carrier (analogous to compile-time `SoundChangeRule`) and a clearer early pipeline for Index surface cleanup.

## Question

How should parse represent a rule **while** it is being loaded, split, and transformed — and where does a **sequential surface-normalization** step sit relative to corrections, `section_mappings`, `manual_mappings`, and structural split — so proximity ([122](122-grill-proximity-conditions-yaml.md)) and dialect/applicability ([123](123-grill-applicability-dialect-sporadic-conditions-yaml.md)) can be extracted without growing regex complexity or `manual_mappings.yml` hacks?

## Proposal (session input — not yet locked)

### `IndexRule` (Pydantic)

Parse-time equivalent of compile-time `SoundChangeRule`: holds `stages`, optional rule-level metadata (`sporadic`, `comment`, `status`, provenance), and **context fields** as structured objects rather than ad hoc `dict[str, Any]` threading through `parse_rule_element`.

### `IndexContext` + enums

`env` and `exception` on `IndexRule` are `IndexContext | None`, each carrying:

| Field | Type | Role |
| --- | --- | --- |
| `text` | `str` | Index-shaped segment/env string (target or structural env) |
| `proximity` | `IndexProximity \| None` | Neighbour/placement relation for this scope ([122](122-grill-proximity-conditions-yaml.md) relation enum) |
| `dialect` | `IndexDialect \| None` | Geographic/dialect scope extracted from this field ([123](123-grill-applicability-dialect-sporadic-conditions-yaml.md)) |

Rule-level `applicability` / `position` YAML from grills 122–123 may still serialize as **top-level** optional keys on the corpus rule; open question whether `IndexContext` is **only** in-memory IR or also the authoritative decomposition before YAML emit.

### Surface normalization (rename TBD)

Before (or interleaved with) today's heavy `extract_rule_parts` / prose passes, run an ordered list of **lossless or policy-documented** string transforms on the **working line** to align Index syntax toward conventional `input → output / env ! exception` shapes — absorbing work now done partly in `manual_mappings.yml` and scattered regexes. Goal: simpler split logic; retire manual rows when parity proven ([122](122-grill-proximity-conditions-yaml.md) Phase 2, [123](123-grill-applicability-dialect-sporadic-conditions-yaml.md) Q6).

## Facts (do not re-litigate without new evidence)

- Today `parse_rule_element` threads a `dict` from `extract_rule_parts` through ~15 transforms ([`parser.py`](../../../src/conlanger/tools/ingest/parser.py)); compile uses pydantic `SoundChangeRule` + per-field compile ([ADR-0014](../../../docs/adr/0014-per-field-asca-compile.md)).
- [122](122-grill-proximity-conditions-yaml.md) (paused): YAML `position: {env?, exception?}` relation map; targets stay in `env`/`exception` **strings**; parser extracts from `raw` with open **Q9/Q10** (manual mappings vs extract order).
- [123](123-grill-applicability-dialect-sporadic-conditions-yaml.md) (open): `applicability` object; retire `sporadic ;` manual injections; Phase 0 additive fields.
- Docs order A½: corrections → section_mappings → manual_mappings → B½ semicolon peel → B symbols → C split ([`index-diachronica-parser.md`](../../../docs/system/index-diachronica-parser.md)).
- `manual_mappings` runs **before** section_mappings in current code (comment in `parser.py` says manual before section; doc table says section before manual — **code wins**: manual first).

## Decisions (2026-09-20 grill — partial)

### Q1 — IR vs YAML

**Settled:** `IndexRule` is the parse pipeline model; **YAML uses the same schema** as `IndexContext` for `env` / `exception` (not a separate top-level `position` map as in paused [122](122-grill-proximity-conditions-yaml.md)). Supersedes 122’s `position: {env?, exception?}` + opaque string targets **when 139 closes** (122 must be amended or closed as superseded).

### Q2 — Normalisation step name

**Settled:** **index rule normalisation** (ordered transforms on the working line after manual mappings).

### Q3 — Pipeline order

**Settled** (differs from current code and from [index-diachronica-parser.md](../../../docs/system/index-diachronica-parser.md) A½ table — **ADR / doc update required**):

1. Store **`raw`** (audit HTML line)
2. **Corrections** overlay on working line (not necessarily the same as today’s “corrections replace `raw`” — see open Q below)
3. **Manual mappings**
4. **Index rule normalisation**
5. **Section mappings**
6. First **`;`** comment peel
7. … (symbol norm, structural split, field transforms — to confirm)

**Not settled:** whether corrections run before manual mappings on **HTML `raw`** only vs corrected working line; whether stored `raw` stays HTML-only while corrections apply only to working copy.

### Q4 — `IndexContext` shape and scope

**Settled direction:**

- `env` and `exception` on `IndexRule` are **`IndexContext`** (Pydantic), each holding **proximity/position** (terminology TBD) and **dialect** references.
- **Inclusive vs exclusive** semantics come from **which property** holds the context (`env` vs `exception`), not from extra flags on `IndexContext`.
- **YAML example** (illustrative):

```yaml
env:
  proximity:
    adjacent_to: C
```

- **Neighbour template expansion** (e.g. `C_, _C`) happens at **parse time** (not deferred to compile as [122](122-grill-proximity-conditions-yaml.md) Phase 1). Tension with [ADR-0002](../../../docs/adr/0002-applier-neutral-yaml-rule-index.md) — see open grill round 2.

### Q6 — Migration slice

**Direction:** Prefer **non-destructive YAML output** where possible; owner **unsure** whether that is achievable without **compile-time** changes (today compile assumes `env` / `exception` are **strings** throughout the pipeline).

## Open questions (grill frontier — round 2)

1. **`raw` vs corrections** — Should index `raw` always be the HTML extract while corrections apply only to the working line?
2. **Structured `env` schema** — Is `proximity.adjacent_to: C` the canonical shape for all relation kinds (`medial`, `penult`, `near`, …), or a `text` + `proximity` object hybrid for structural env (`V_C`)?
3. **Applier-neutral vs parse-time `C_, _C`** — Store neighbour templates in YAML after parse, or store relation + target and project to strings only at compile/render?
4. **122 / 123 ticket disposition** — Amend grills vs supersede by 139 outcomes.
5. **Compile boundary** — Coerce structured `env` → string at `SoundChangeRule` construction vs teach compile transforms to read `IndexContext`.

## Answer

**IndexRule** is the parse-time pydantic model (analogous to **SoundChangeRule**). **`env`** and **`exception`** are **`IndexContext | None`** in code and in YAML.

### `IndexContext` schema

| Field | Type |
| --- | --- |
| `context` | optional `str` — structural / target Index material |
| `position` | optional `object` — open map; property values are **`bool` \| `str` \| `list[str]`** |
| `dialect` | optional **`bool` \| `str` \| `list[str]`** |

Inclusive vs exclusive dialect/position semantics: determined by whether the object is on **`env`** or **`exception`**; `IndexContext` has no extra scope flag.

### Pipeline order (working line)

1. Store **`raw`** (HTML only)  
2. Corrections overlay  
3. Manual mappings  
4. **Index rule normalisation**  
5. Section mappings  
6. First `;` peel → symbols → split → field transforms  

Requires ADR + parser doc update ([140](140-adr-parse-pipeline-order-and-raw-semantics.md)).

### Compile / YAML policy

- **Option A:** YAML keeps structured `IndexContext`; **compile** resolves `position` / `dialect` + `context` to env/exception strings ([144](144-implement-indexcontext-compile-resolution.md)).
- Terminology: YAML key **`position`** (not top-level `position` map from paused 122).
- **Dialect** only on `IndexContext`; no separate rule-level `applicability` in v1 ([123](123-grill-applicability-dialect-sporadic-conditions-yaml.md) superseded for schema shape).

### Migration

**IndexRule** refactor with **minimal compile coercer** for new YAML schema ([142](142-implement-indexrule-pydantic-and-yaml-schema.md), [144](144-implement-indexcontext-compile-resolution.md)); full non-destructive YAML across the corpus is not expected without regen.

### Follow-on tickets

- [140 ADR parse order + raw](140-adr-parse-pipeline-order-and-raw-semantics.md)  
- [141 ADR structured env/exception](141-adr-structured-env-exception-indexcontext.md)  
- [142 Implement IndexRule](142-implement-indexrule-pydantic-and-yaml-schema.md)  
- [143 Index rule normalisation passes](143-implement-index-rule-normalisation-passes.md)  
- [144 Compile IndexContext resolution](144-implement-indexcontext-compile-resolution.md)  

[122](122-grill-proximity-conditions-yaml.md) and [123](123-grill-applicability-dialect-sporadic-conditions-yaml.md) are **superseded** for YAML shape; keep corpus inventory / manual_mapping retirement lists as input to 143/144.

## Outcomes (fill on resolve)

- [x] Normalisation name and pipeline order → ADR [140](140-adr-parse-pipeline-order-and-raw-semantics.md)
- [x] `IndexRule` / `IndexContext` / `position` schema locked → ADR [141](141-adr-structured-env-exception-indexcontext.md)
- [x] Neighbour templates at compile (structured YAML) → [144](144-implement-indexcontext-compile-resolution.md)
- [x] Follow-on implementation tickets filed
- [x] [122](122-grill-proximity-conditions-yaml.md) / [123](123-grill-applicability-dialect-sporadic-conditions-yaml.md) superseded for schema

## Related

- [Grill: position relations](122-grill-proximity-conditions-yaml.md)
- [Grill: applicability, dialect, sporadic](123-grill-applicability-dialect-sporadic-conditions-yaml.md)
- [Structured rule conditioning exploration](../research/structured-rule-conditioning-exploration.md)
- [Grill: pydantic compile models](92-grill-pydantic-compile-refactor.md)

## Comments

- 2026-09-20: Ticket filed and claimed from wayfinder; grill in chat.
- 2026-09-20: Round 1 answers recorded (Q1 yes; Q2 index rule normalisation; Q3 order with manual mappings before normalisation; Q4 structured env YAML + parse-time neighbour expansion; Q6 parity goal, compile impact TBD).
- 2026-09-20: Round 2 settled — HTML-only `raw`; `IndexContext` with `context` + open `position` map + `dialect` tri-type; compile option A; dialect on context only; tickets 140–144 filed. Grill closed.
