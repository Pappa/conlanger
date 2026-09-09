Type: grilling
Status: needs-grilling
Blocked by: None

# Grill: applicability, dialect scope, sporadic vs conditioning, and phased structured YAML

Spawned from agent session 2026-09-07. Background: [structured-rule-conditioning-exploration.md](../research/structured-rule-conditioning-exploration.md) (all parts; proximity deferred to [ticket 122](122-grill-proximity-conditions-yaml.md)).

Run `/grill-with-docs` or grilling + domain-modeling. **No code in this grill.**

## Question

How should Index **applicability** prose (dialect, region, morphological scope, uncertainty) be represented in the **applier-neutral** rule index — separately from phonological **proximity** `conditions` ([122](122-grill-proximity-conditions-yaml.md)) and from boolean **`sporadic`** — and how should **user-supplied config** (e.g. `dialect: northern` or `dialect: "*"`) gate compile, validation, and render?

Also decide **Phase 0** rollout (additive YAML fields, no compile change), **`lexical_targets`** parse config, parse-order for extraction, and retirement of `manual_mappings.yml` **`sporadic ;`** injection rows — **before** implementation.

## Facts (do not re-litigate without new evidence)

- `manual_mappings.yml` injects `sporadic ;` before dialect/region phrases so [apply_sporadic_qualifier](../../../src/conlanger/tools/ingest/transforms.py) sets `sporadic: true` — conflates dialect conditioning with uncertainty ([exploration doc](../research/structured-rule-conditioning-exploration.md) Part 2).
- `_UNCERTAINTY_WORDS` in [gloss.py](../../../src/conlanger/utils/gloss.py): `sporadic`, `sometimes`, `occasionally`, `(?)` — not dialect phrases.
- [Ticket 68](68-sporadic-sampling.md): `sporadic: true` → 50% apply/skip at **render** via instance `Random`; inventory **always applies**. Distinct from optional outputs ([61](61-grill-optional-outputs.md)).
- [prose_position_env.py](../../../src/conlanger/tools/ingest/prose_position_env.py): `not universal` → `sporadic: true`; trailing `, in monosyllables` → `comment` (ticket 107).
- [double_slash_env.py](../../../src/conlanger/tools/ingest/double_slash_env.py): dialect names in `//` env often → `comment` (ticket 108).
- **Sporadic** vs **optional outputs** vs **applicability** are three gates in glossary [CONTEXT.md](../../../CONTEXT.md).
- Proposed fields: `applicability` (dialect/region/morphology/uncertainty), optional `conditions` for non-proximity env atoms, `lexical_targets` in parser config ([exploration doc](../research/structured-rule-conditioning-exploration.md) Parts 4–6).

## Grill questions

### Applicability schema

1. **Q1 — `applicability` shape:** Is the proposed object (`kind`, `include`/`exclude` dialects/regions, `source_text`, `confidence`) sufficient, or should morphological scope (`in nouns`, `diminutives`, `Form VI`) live here vs in `conditions` vs `comment` only?
2. **Q2 — Kind taxonomy:** Lock enum values: `universal`, `dialect_subset`, `region`, `morphological`, `probabilistic`, `unknown`, …? What is missing?
3. **Q3 — Include vs exclude:** Model `! in Queensland` as `exclude.regions`, negated `applicability`, or `conditions` on exception scope?
4. **Q4 — Normalization:** Store normalized tokens (`northern`) alongside `source_text`, or prose-only until a dialect ontology exists?

### Sporadic vs dialect vs uncertainty

5. **Q5 — Split policy:** Which phrases stay `sporadic: true` (ticket 68 path) vs `applicability.kind: probabilistic` vs `applicability.kind: dialect_subset`? (`in some dialects`, `in certain situations`, `maybe`, `not universal`, `(?)`, …)
6. **Q6 — Retire `sporadic ;` hack:** When can manual-mapping injection rows be removed in favour of direct `applicability` extraction?
7. **Q7 — Render vs inventory:** For `applicability` mismatch (user `dialect: southern`, rule `northern` only): skip at render (`#\t`), omit from series, still validate in inventory, or separate inventory row per dialect variant?
8. **Q8 — Interaction with ticket 68:** If a rule is both `sporadic: true` **and** `applicability.dialect_subset`, what is draw order and semantics?

### Morphological and grammatical comments

9. **Q9 — Classifier:** How to separate `in northern dialects` (geographic) from `in nouns` / `in monosyllables` (morphological) from `in the feminine ending` (lexical template)? Rules of thumb vs inventory clustering?
10. **Q10 — Ticket 107 overlap:** Should `, in monosyllables` tails become `applicability.morphological` or stay `comment` + structural env only?
11. **Q11 — Exception dialect prose:** Phrases in `exception` / `//` clauses (ticket 108) — same `applicability` model or exception-specific?

### Lexical targets and non-proximity conditions

12. **Q12 — `lexical_targets` config:** Ship `consonants` → `C`, `emphatics` → `[+ emphatic]`, etc. in `config/parser/` at parse time? Who authors rows (inventory-driven vs seed set)?
13. **Q13 — Non-proximity `conditions`:** Should stress/position/morphology atoms share the same `conditions[]` list as proximity ([122](122-grill-proximity-conditions-yaml.md)), or separate top-level fields?
14. **Q14 — Ticket 119 link:** How do `applicability` and bare env feature matrices ([119](119-grill-distinctive-features-env-exception.md)) compose without double projection?

### Phased rollout (Phase 0)

15. **Q15 — Phase 0 fields:** Confirm additive-only: `conditions` (non-proximity atoms deferred to 122 for proximity subset), `applicability`, both optional; `env`/`sporadic`/`comment` unchanged; compile ignores new fields.
16. **Q16 — Extraction timing:** Phase **C¾** after split ([exploration doc](../research/structured-rule-conditioning-exploration.md) Part 7) — agree for applicability as well as proximity?
17. **Q17 — Diagnostic report:** What columns in `structured-conditions.csv` (or sibling) prove extraction quality before any behavior change?
18. **Q18 — Glossary / ADR:** New CONTEXT terms (`Applicability`, structured `conditions`)? New ADR or amend 0010/0011?

### Config and validation

19. **Q19 — Operator config location:** `config/compile/context_resolution.yml` for `dialect.active` and `on_mismatch` — parse config, compile config, or both?
20. **Q20 — `dialect: "*"`:** Validate all applicability variants in inventory (multiple rows), single row with worst case, or owner choice per run?

## Outcomes (fill on resolve)

- [ ] `applicability` schema and kind enum locked
- [ ] Sporadic vs dialect vs probabilistic split policy
- [ ] Morphological vs geographic classifier policy (incl. 107/108 overlap)
- [ ] Phase 0 field set and extraction order
- [ ] Config shape for dialect/region gating
- [ ] Inventory/render behavior on applicability mismatch
- [ ] Follow-on tickets filed (extractor, report, glossary, ADR, compile gate, …)

## Related

- [Grill: proximity relations in structured rule conditions](122-grill-proximity-conditions-yaml.md)
- [Grill: distinctive features in env and exception](119-grill-distinctive-features-env-exception.md)
- [Sporadic sampling](68-sporadic-sampling.md)
- [Grill: optional outputs](61-grill-optional-outputs.md)
- [Correction pass: prose env positions](107-correction-pass-prose-env-positions.md)
- [Correction pass: double-slash env](108-correction-pass-double-slash-env.md)
- `config/parser/manual_mappings.yml` — `sporadic ;` / dialect rows (~lines 75–140, 250+)

## Comments

- 2026-09-07: Ticket filed from structured-conditioning exploration session. See [research/structured-rule-conditioning-exploration.md](../research/structured-rule-conditioning-exploration.md).
