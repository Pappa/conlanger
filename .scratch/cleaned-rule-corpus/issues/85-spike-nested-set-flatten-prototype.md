Type: spike
Status: resolved
Blocked by: None

# Spike: prototype parse-time nested-set flatten

Spawned from [spike 67](67-spike-nested-sets.md) and design discussion on Index editorial nesting vs cited source material. **Informs** (and may supersede compile-time policy on) [69](69-correction-pass-flatten-nested-context-sets.md) / [70](70-correction-pass-flatten-nested-io-sets.md).

## Question

If we flatten Index editorial nested `{…}` at ingest (**stages**, **env**, **exception**), how much does compile validation improve, what regresses, and where in the parse pipeline should the transform run?

## Hypothesis

Nested braces in Index Diachronica are often **authorial condensation**, not faithful transcription of cited source notation. Flat alternation in index fields is the right applier-neutral IR; **`raw`** preserves Index wording for audit (ADR-0010).

## Context

- **#67** bucketed **46** `nested_brackets` inventory rows; **40** index rules with brace depth ≥ 2 or unbalanced `{` in working fields. Findings: [nested-sets-inventory.md](../research/nested-sets-inventory.md). Scan: [scan_nested_sets.py](../research/scan_nested_sets.py).
- **#69** / **#70** currently assume **compile-time** flatten for env/exception and stages I/O respectively; **#70** blocked by grill [71](71-grill-paren-and-parallel-set-notation.md) for parallel-column shapes.
- Parse-time env normalizations already exist (medial, else, stress, feature/IPA, `series_expansions`) — nested-set flatten is the same *class* of move: de-condense Index shorthand into explicit alternation.
- No current applier accepts nested `{}` of the same type (ASCA `NestedBrackets`; Brassica flat `[a b]` categories only).

## What to build (throwaway / branch)

### 1. Naive flatten function

Implement `flatten_nested_sets(text: str) -> str` (location TBD; prefer a neutral module usable from parse and compile).

**Document algorithm scope explicitly:**

| In scope | Out of scope |
|----------|--------------|
| Same-type `{}` nesting: `{a,{b,c}}` → `{a,b,c}` | `segment{variants}` (ticket 48) |
| Union of comma-bounded set members at depth > 1 | `(h)ə{p,b}` parallel columns (#71) |
| Optional second mode: `({m,j,w})V` → `{mV,jV,wV}` (labelled separately in metrics) | Unbalanced / malformed chains (`2173`, `4654`, …) |
| Apply to each **stage string** independently + **env** + **exception** | **`raw`** (never) |

Run **two labelled modes** if cheap: **union-only** vs **union + parenthetical-in-set expansion**.

### 2. Phase A — in-memory YAML prototype

1. Load `data/diachronica/index_diachronica_parsed.yml`.
2. Apply flatten to `stages` / `env` / `exception` in memory (do not commit index YAML).
3. Run full compile validation inventory (same path as `create_index` validation).
4. Record before/after metrics (see deliverables).

### 3. Phase B — parse insertion probe

1. Wire flatten into `IndexDiachronicaParser` behind a spike flag or branch-only hook.
2. Test candidate insertion points with unit fixtures:

| Slot | Location | Risk / note |
|------|----------|-------------|
| P1 | After `extract_rule_parts`, before `series_expansions` | Early; series may introduce braces |
| P2 | After `series_expansions`, before medial/else | Post-collective expansion |
| P3 | After `apply_medial_env_conditions` / feature / IPA, before `finalize_stages_shape` | Post env prose normalizers |
| P4 | After `resolve_catch_all_else_rules` (section assembly) | **else** copies prev `env` → `exception` |

3. Regen to **temp YAML** (`uv run create_index --yaml-out /tmp/...`) — not `data/diachronica/index_diachronica_parsed.yml`.
4. Re-validate inventory; compare to Phase A.

### 4. Source-vs-Index sample (qualitative)

For **5–10** rules across #67 buckets (A–E from [nested-sets-inventory.md](../research/nested-sets-inventory.md)), note Index nested form vs cited source phrasing (one line each). Grounds ADR-0010 recommendation.

## Deliverables

| Artifact | Purpose |
|----------|---------|
| [research/nested-set-flatten-prototype.md](../research/nested-set-flatten-prototype.md) | Method, metrics, parse-slot recommendation, rejected orderings, go/no-go per bucket |
| [research/nested-set-flatten-prototype.csv](../research/nested-set-flatten-prototype.csv) | Per-rule: `source`, fields changed, `ok` before/after, `failure_class` before/after, bucket |
| Extend or sibling to [scan_nested_sets.py](../research/scan_nested_sets.py) | Before/after brace depth counts |
| Spike-only code on a throwaway branch | Do not merge parser wiring without follow-on task |

### Metrics table (required in findings)

| Metric | Before | After (union-only) | After (union + paren-in-set) |
|--------|-------:|-------------------:|-----------------------------:|
| Inventory `ok=True` rows | | | |
| `nested_brackets` rows | 46 | | |
| `ok` flips (changelog) | — | | |
| Regressions (`ok` True→False) | — | | |
| Rules with ≥1 field flattened | — | | |
| Corpus rules brace depth ≥ 2 | 40 | | |

**Changelog:** run validation with **existing** `asca-rule-inventory.csv` as baseline so `asca-rule-inventory-changelog.csv` appends `ok` flips — but **do not** treat changelog as the sole metric.

## Acceptance criteria

- [x] Naive algorithm documented with explicit scope exclusions
- [x] Phase A before/after inventory metrics (not changelog-only)
- [x] Regression count and `failure_class` transition summary
- [x] Parse insertion recommendation with evidence (**else-rule** fixture required)
- [x] Per #67 bucket (A–E): **go** / **no-go** / **go-with-limits** for parse-time flatten
- [x] Recommendation: parse-time vs compile-time; whether to rewrite [69](69-correction-pass-flatten-nested-context-sets.md) / [70](70-correction-pass-flatten-nested-io-sets.md)
- [x] Ticket marked `resolved` with **Answer** summarizing policy + follow-ons

## Answer

**Parse-time flatten at P4** (after `resolve_catch_all_else_rules`), not compile-time. Preserve `raw`. Findings: [nested-set-flatten-prototype.md](../research/nested-set-flatten-prototype.md).

| Metric | Before | Union-only | Union + paren-in-set |
|--------|-------:|-----------:|---------------------:|
| `ok=True` inventory rows | 8270 | 8277 | 8281 |
| `nested_brackets` | 45 | 32 | 27 |
| `ok` flips / regressions | — | 7 / 0 | 11 / 0 |
| Rules flattened | — | 13 | 20 |
| Working-field brace depth ≥ 2 | 31 | 18 | 13 |

Else `:5509`/`:5510`: P3 vs P4 commute (copy ∘ flatten). Recommend **P4**. Bucket **B go** (with paren mode); **A/C go-with-limits**; **D/E no-go**. Naive flatten does **not** fix #71 parallel columns. **#69 and #70 briefs rewritten** to parse-time P4.

Follow-ons: implement #69 (env/exception `union_paren`); #70 (stages union, `:1398` paren); #71 keeps D.

## Out of scope

- Committing changes to `data/diachronica/index_diachronica_parsed.yml`
- Production parser integration on `main` (follow-on task only)
- Rule-split shapes (#71, paired nested output sets, Menominee `{CC_C{…},CCG_C{…}}`) — classify only
- Changing optional-output / `alt_idx` behaviour (#66)
- Brassica emit syntax
- Re-bucketing all nested shapes (#67 already done)

## References

- [Spike: nested sets](67-spike-nested-sets.md)
- [nested-sets-inventory.md](../research/nested-sets-inventory.md)
- [Correction pass: flatten nested context sets](69-correction-pass-flatten-nested-context-sets.md) — parse-time P4 (rewritten after this spike)
- [Correction pass: flatten nested I/O sets](70-correction-pass-flatten-nested-io-sets.md) — parse-time union (rewritten; D stays #71)
- [Grill: paren and parallel set notation](71-grill-paren-and-parallel-set-notation.md)
- [ADR-0010 Historical fidelity](../../docs/adr/0010-historical-fidelity-class-first-status.md)
- [ADR-0002 Applier-neutral YAML](../../docs/adr/0002-applier-neutral-yaml-rule-index.md)
- `src/conlanger/tools/ingest/parser.py` — `parse_rule_element` transform order
- `src/conlanger/tools/ingest/section_policy.py` — `resolve_catch_all_else_rules`

## Agent Brief

**Category:** enhancement  
**Skills:** `/prototype` (throwaway code), metrics via `uv run create_index` validation path  
**Summary:** Prototype naive nested-set flatten on index fields; measure compile validation impact and recommend parse pipeline insertion point — informs parse-time vs compile-time policy for #69/#70.

**Current behavior:** ~46 `nested_brackets` inventory rows; index fields may carry nested `{…}` that no applier accepts. #69/#70 assume compile-time flatten; no flatten implementation shipped.

**Desired behavior:**
1. Shared `flatten_nested_sets()` with documented naive scope (see ticket body).
2. **Phase A:** in-memory YAML transform → full inventory validate → metrics CSV + markdown table.
3. **Phase B:** parser hook at best candidate slot(s) → temp regen → re-validate; document interactions with `series_expansions`, medial, else (`resolve_catch_all_else_rules`).
4. Qualitative source-vs-Index notes for 5–10 rules.
5. Close with **parse-time vs compile-time** recommendation and whether to rewrite #69/#70 agent briefs.

**Key interfaces:**
- Corpus fields: `stages` (list of strings), optional `env` / `exception`; never mutate `raw`
- Validation: `index_inventory` / `validate_asca` via `create_index` (use `--yaml-out` temp path for Phase B)
- Prior scan: `.scratch/cleaned-rule-index/research/scan_nested_sets.py`

**Verified baseline (2026-08-12, #67):**

| Bucket | Inv rows | Example `source` |
|--------|--------:|------------------|
| A — true nested I/O | 9 | `index_diachronica_original.html:998` |
| B — nested env/exception | ~16 | `index_diachronica_original.html:1903` |
| C — parenthetical-in-set | 6 | `index_diachronica_original.html:1903` |
| D — parallel columns (#71) | ~10 | `index_diachronica_original.html:2398` |
| E — prose/malformed | ~12 | `index_diachronica_original.html:2173` |

**Acceptance criteria:** (same as ticket body)

**Out of scope:** (same as ticket body)

**Hypotheses to test (not decisions):**
- Union-only flatten recovers most of buckets A–C with few regressions
- Parse slot P4 (post–else resolution) or P3 avoids propagating nested env into derived exceptions
- Parallel-column bucket D will not be fixed by naive flatten — confirms #71 boundary
- Parse-time flatten aligns better with ADR-0010 than compile-only (#69 as written)

## Comments

Claimed 2026-08-19. Research complete — findings: [nested-set-flatten-prototype.md](../research/nested-set-flatten-prototype.md). Verdict: parse-time P4; #69/#70 briefs rewritten.
