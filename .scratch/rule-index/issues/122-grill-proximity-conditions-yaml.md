Type: grilling
Status: needs-grilling
Blocked by: None

# Grill: proximity relations in structured rule conditions

Spawned from agent session 2026-09-07. Background: [structured-rule-conditioning-exploration.md](../research/structured-rule-conditioning-exploration.md) (Parts 2–4.1, 5–7, 9–10 proximity items).

Run `/grill-with-docs` or grilling + domain-modeling. **No code in this grill.**

## Question

How should Index **proximity** prose (`adjacent to`, `near`, `next to`, …) be represented in the **applier-neutral** rule index YAML, and how should **compile-time resolution** (user-supplied config) project those claims to ASCA env/exception — without collapsing distinct Index relations (especially **near** ≠ **adjacent**)?

Decide schema for optional `conditions` atoms, resolver config shape, interaction with existing prose-env passes ([107](107-correction-pass-prose-env-positions.md), [108](108-correction-pass-double-slash-env.md)), and migration off `manual_mappings.yml` proximity rows — **before** Phase 0 extraction or compile resolver implementation.

## Facts (do not re-litigate without new evidence)

- Today `manual_mappings.yml` rewrites e.g. ` / near consonants` → ` / C_, _C` (treating near as immediate neighbor) and ` / adjacent to short u` → ` / u[-long]_, _u[-long]` — ASCA shapes baked in at parse ([exploration doc](../research/structured-rule-conditioning-exploration.md) Part 2).
- [prose_position_env.py](../../../src/conlanger/tools/ingest/prose_position_env.py) already normalizes some **adjacent** / **next to** phrases (`_,{set}`, `_,u` for `typically near *u`) but not the full manual-mapping set.
- [double_slash_env.py](../../../src/conlanger/tools/ingest/double_slash_env.py) handles `adjacent to another consonant` → `C_,_C` on exception tails (ticket 108).
- Ticket [119](119-grill-distinctive-features-env-exception.md) locks segment-at-focus feature policy for env/exception matrices; proximity targets may reference `class`, `feature`, or `segment` hosts.
- ADR-0002 / ADR-0010: YAML stays Index-shaped claims; ASCA projection is compile; do not lose Index wording in SoT.
- Proposed Phase 0: add `conditions` to corpus rules **without** changing `env` or compile ([exploration doc](../research/structured-rule-conditioning-exploration.md) Part 6).

## Grill questions

### Schema and SoT

1. **Q1 — `conditions` atom shape:** Is the proposed `conditions[]` entry (`scope`, `relation: proximity`, `proximity: adjacent|near|…`, `target`, `source_text`) the right v1 atom, or should proximity be flatter/different?
2. **Q2 — Relation vocabulary:** Which Index surface forms map to which stored `proximity` values? (`adjacent to`, `next to`, `near`, `typically near`, `unless adjacent to`, …) Are `adjacent` and `next to` synonyms in SoT?
3. **Q3 — Target typing:** When the object is `consonants`, `emphatics`, `nasals`, `gutturals`, `short u`, `{S}`, … — use `target.kind: class|feature|segment|set`, a `lexical_targets` config indirection, or raw `prose` until mapped?
4. **Q4 — Exception scope:** For `! near emphatics` / `unless adjacent to another consonant` — `conditions` with `scope: exception`, negated atom, or separate `polarity: block` field?

### Compile resolution

5. **Q5 — Resolver catalog:** What named strategies must v1 support? (e.g. `immediate_neighbor`, `same_syllable`, `next_syllable`, `same_word`, `within_segments` + distance, …) Which are required vs deferred?
6. **Q6 — Default for `near`:** What is the config default when the user does not specify? (Acknowledge current `C_, _C` is a legacy stand-in, not linguistically faithful.)
7. **Q7 — ASCA emission:** Does each strategy always emit env/exception underscore patterns (`C_, _C`), or sometimes input-side colon / structure notation (cf. ticket 119)?
8. **Q8 — Multiple proximity atoms:** Can one rule have several `conditions` (e.g. near consonants **and** not near emphatics)? Compose how — conjunction in one env, multiple env slots, or compile fan-out?

### Parse and migration

9. **Q9 — Extraction source:** Extract from `raw`, post-mapping `env`, `comment`, or all three? How to recover prose destroyed by current manual mappings during Phase 0?
10. **Q10 — Parse order:** Confirm or reject Phase **C¾** (structured capture after split, before D transforms). Should extracted patterns suppress later string rewrites?
11. **Q11 — Overlap with 107/108:** Which proximity patterns stay in dedicated extractors vs remain in `apply_prose_position_env_conditions` / `apply_double_slash_env_conditions`?
12. **Q12 — Phase 0 acceptance:** What parity report threshold justifies removing a `manual_mappings.yml` proximity row?

### Validation and fidelity

13. **Q13 — Inventory:** Does proximity resolution affect `validate_asca` / per-field blame, or only render-time env strings?
14. **Q14 — Historical fidelity:** When no resolver can express Index intent faithfully, hold out (`status: skipped`), leave opaque `env`, or emit best-effort with `comment`?

## Outcomes (fill on resolve)

- [ ] `conditions` proximity atom schema locked
- [ ] `proximity` enum + Index phrase mapping table
- [ ] Compile resolver config shape + v1 strategy set
- [ ] Extraction source and parse-order decision
- [ ] Migration plan off manual-mapping proximity rows
- [ ] Follow-on tickets filed (Phase 0 extract, config stub, compile resolver, …)

## Related

- [Grill: distinctive features in env and exception](119-grill-distinctive-features-env-exception.md)
- [Correction pass: prose env positions](107-correction-pass-prose-env-positions.md)
- [Correction pass: double-slash env](108-correction-pass-double-slash-env.md)
- `config/parser/manual_mappings.yml` — proximity / near rows (~lines 48–74, 253+)

## Comments

- 2026-09-07: Ticket filed from structured-conditioning exploration session. See [research/structured-rule-conditioning-exploration.md](../research/structured-rule-conditioning-exploration.md).
