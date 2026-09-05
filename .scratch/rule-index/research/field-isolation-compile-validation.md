# Field-isolation compile validation

Spike for [ticket 35](../issues/35-spike-field-isolation-compile-validation.md).  
**ASCA version:** 0.10.2 (local `asca --version`).  
**Context7:** asca / asca-rust not indexed — ASCA claims below cite crate docs + registry source + CLI probes.

## 1. Executive summary

**Recommendation: go-with-limits.**

Validating one index field at a time by pairing it with **canned known-valid stubs**, still driving `validate_asca` + the baseline wordlist, **does** raise diagnostic confidence for the dominant failure modes (Tier 1–2 syntax: unknown character/feature/grouping, missing `_`, optionals in I/O, word-bound location, negation in output). It does **not** replace whole-rule validation: cross-field structural errors (uneven/lonely sets, condensed I/O balance, insertion+env coupling, deletion-only-segment against the baseline lexicon) can disagree between isolation and the full rule.

Stay inside the [ticket 10](../issues/10-rule-derived-probe-synthesis.md) boundary: **no** per-rule probe-word synthesis. Shape-aware **stub selection** (pick among a fixed stub table based on coarse field shape: insert/delete/set/metathesis) is allowed; inventing words from rule tokens is not.

## 2. Current compile / validate path

Primary sources: `src/conlanger/tools/{rules,phonological_ruleset,asca_validator,index_inventory}.py`.

```text
index rule dict {input, output, env?, exception?, …}
        │
        ▼  SoundChangeRule (requires input+output; optional env/exception)
   compile: join fields → group_mappings → length/ejective/alias norms
        │
        ▼  DiachronicSeries
   .rsca body (@ title + indented rule lines)
        │
        ▼  validate_asca → asca run <probe.wsca> --rules <tmp.rsca>
   baseline: tests/fixtures/asca_probe_words.wsca  (or ASCA_PROBE_WORDS / default five words)
```

Inventory (`validate_index_rule`) already isolates **per index rule** (one rule per mini-section) but not **per field**. A whole-rule failure yields one `failure_class` + `description` with no field attribution ([ticket 12](../issues/12-full-index-validation-inventory.md)).

`SoundChangeRule` ASCA separators (`rules.py`): ` > ` / ` / ` / ` // `. Skipped rules render as `#\t…` and are excluded by `_active_rule_changes`.

## 3. ASCA field constraints (0.10.2)

Primary: [asca-rust `doc/doc.md` @ 0.10.2](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md) § The Basics; crate `src/rule/parser.rs` (`rule` ← input → output → context? → except?); `src/error/{syntax,runtime}.rs`; prior inventory research [asca-rule-validity.md](asca-rule-validity.md).

| Field | Hard constraints (syntax / early runtime) |
|-------|-------------------------------------------|
| **input** | Non-empty; insert = `*`/`∅` alone; no word boundary `#` in I/O (`WordBoundLoc`); optionals `(…)` **not** allowed (`OptLocError`); negation OK (0.10.1+) |
| **output** | Non-empty; delete = `*`/`∅` alone; metathesis = only `&` or `@`; no negation (`BadNegationOutput`); optionals not in output (often surfaces as `Unknown character '('`); sets need matching input set at apply (`LonelySet` / UnevenSet) |
| **env** | Exactly one `_` focus (or joined `___`); empty `/` invalid (`EmptyEnv` / Expected `_`); `#` periphery only; optionals allowed; env sets `:{ … }:` |
| **exception** | Same env grammar; `|` or `//`; omit ≠ `| _` (“except everywhere”) |

CLI note: `parse_rsca` treats a trimmed line starting with `#` (but not `##`) as a **description**, not a rule (`src/cli/parse.rs`). A index `input: "#"` compiles to `\t# > …`, which after trim becomes `# > …` → **no rule line**. Local `validate_asca` then raises “no active SoundChangeRule lines” because `_active_rule_changes` also treats `#…` as skipped. This is a render/parse hazard for isolation of bare `#` I/O, not a field-stub issue alone.

## 4. Stub strategy table

Goal: one **real** field variable; all other fields are from a small canned set that ASCA 0.10.2 accepts with `tests/fixtures/asca_probe_words.wsca` (`a`, `ba`, `kata`, `sami`, `ntu`). Probes below were run with local `asca 0.10.2`.

### Default stubs (always-valid with baseline)

| Role | Stub value | Notes |
|------|------------|-------|
| input | `a` | Matches baseline; simple IPA |
| output | `e` | Simple IPA; **not** `*` (see limits) |
| env | *(omit)* | Equivalent to `/ _` for non-insertion ([docs](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#the-basics)) |
| exception | *(omit)* | Do **not** stub `| _` — that disables the rule |

### Per-field isolation recipe

| Isolated field | Constructed rule | Stub policy | Verified OK example | Verified FAIL catches real-field error |
|----------------|------------------|-------------|---------------------|----------------------------------------|
| **input** | `{real} > e` | Omit env/exception. If `real` is `*`/`∅`, use `{real} > e / #_` (bare `/ _` → `InsertionNoEnv`). | `p > e` | `Š > e` → Unknown character; `C:[+dental] > e` → Unknown feature; `(C) > e` → OptLocError |
| **output** | `a > {real}` | Omit env/exception. If `real` is `*`/`∅`, use `x > {real}` (non-matching stub input avoids `DeletionOnlySeg` on word `a`). If `real` is `&`/`@`, use `ab > {real}`. If `real` is a `{…}` set, use cardinality-matched set stub input (see limits) — **not** bare `a`. | `a > i`; `x > *`; `ab > &` | `a > C:[+dental]` → Unknown feature; `a > -C` → Negation in output; `a > (C)` → Unknown `(` |
| **env** | `a > e / {real}` | Omit exception. If the **original** rule’s input is insert (`*`/`∅`), prefer `* > e / {real}` so insertion+env coupling is exercised. | `a > e / #_`; `a > e / (C)_#` | `a > e / word-initially` → Expected `_`; `a > e / _ _` → TooManyUnderlines; `a > e / V#_#` → StuffBeforeWordBound |
| **exception** | `a > e // {real}` | Omit context (or `/ _`). Same grammar as env. | `a > e // #_` | `a > e // elsewhere` → Expected `_` |

### Shape-aware stub selection (fixed table — not probe synthesis)

| Coarse shape of real field | Adjustment |
|----------------------------|------------|
| Insert I (`*`/`∅`) | When isolating **input**: add stub env `#_`. When isolating **env/exception** of an insert rule: keep insert I/O stub `* > e` + real env/exc. |
| Delete O (`*`/`∅`) | When isolating **output**: stub input `x` (absent from baseline). Avoid stub output `*` when isolating other fields. |
| Metathesis O (`&`/`@`) | Stub input ≥2 segments: `ab`. |
| Set `{…}` in I or O | Prefer paired set stubs with equal cardinality when the *other* side is stubbed; otherwise isolation will false-fail (panic / UnevenSet). Cheap heuristic: count top-level commas in `{…}` (document as best-effort). |
| Condensed commas `a, u` | Isolation with singleton stub on the other side is ASCA-legal (singleton expansion); **UnbalancedRuleIO** only appears when both sides are multi and lengths disagree — keep whole-rule check. |
| Leading `#` as sole I/O token | Do not send through normal `.rsca` render without escaping/comment hazard; flag as `format_error` / dedicated check before ASCA. |

## 5. False positives / false negatives

Definitions relative to **whole-rule** `validate_asca` on the real compiled rule:

| Kind | Example | Why |
|------|---------|-----|
| **False pass** (field isolation OK, full rule FAIL) | Input `{p,t}` with stub `> e` OK; output `{b}` with careful stubs may look fine; full `{p,t} > {b}` → `UnevenSet` | Cardinality is cross-field (runtime in `substitution.rs`) |
| **False pass** | Condensed `a, u > e` OK in isolation; full `a, u > e, y, o` → `UnbalancedRuleIO` | Balance needs both multi-sides |
| **False pass** | Isolating env of an insert rule with stub `a > e / _` OK; full `* > a / _` → `InsertionNoEnv` | Bare `_` is empty context for insertion (`insertion.rs`) |
| **False fail** (isolation FAIL, full OK) | Isolating output `{b,d,g}` as `a > {b,d,g}` → ASCA **panic** / lonely-set path; full `{p,t,k} > {b,d,g}` OK | Stub input lacked matching set |
| **False fail** | Isolating delete as `a > *` → `DeletionOnlySeg` on baseline word `a`; full rule with rarer match or `x > *` OK | Baseline lexicon + stub input choice |
| **False fail** | Isolating `#` input via `SoundChangeRule` → treated as comment / no active lines | `.rsca` `#` description rule (`parse_rsca`) |
| **Aligned (useful)** | Unknown feature/character/grouping, missing `_`, OptLocError, BadNegationOutput, StuffBefore/AfterWordBound | Error token position is in the real field; stubs stay inert |

Inventory baseline (summary at research time): ~30% fail; top classes `syntax_other`, `unknown_character`, `expected_underscore`, `unknown_feature` — overwhelmingly Tier 1–2 where isolation **aligns**. Tier 4 / set / insert coupling is the residual disagreement band (same band ticket 10 declined to chase with probe synthesis).

## 6. Recording results (recommendation only)

**Prefer a sidecar CSV** (e.g. `inventory/field-isolation.csv`), joined by `(section_index, section_name, rule_idx)`, rather than widening the main inventory CSV for every rule.

Suggested columns:

- join keys (same as inventory)
- `whole_ok` (copy/join from main inventory)
- `input_ok`, `output_ok`, `env_ok`, `exception_ok` (bool or empty if field absent)
- `input_class`, `output_class`, … (reuse `classify_error`)
- `blame` — derived: pipe-joined failing field names (`input`, `input|env`, …), `multi` (isolation all OK but whole fail), `none`
- `description_*` truncated ASCA messages

**Run policy:** only for rows where `whole_ok` is false (and optionally where env/exception present). Cost: up to 4 extra `asca run` invocations per failing rule (~2.8k fails → ~10k runs), acceptable for regen; skip fields that are absent (`env`/`exception` empty → N/A, not OK).

Do **not** redefine inventory `ok` from isolation alone — whole-rule remains the SoT for correction-pass success rates ([ADR-0010](../../../docs/adr/) / ticket 12).

## 7. Boundary vs ticket 10 (wontfix)

| Allowed (this spike / follow-on) | Forbidden (ticket 10) |
|----------------------------------|------------------------|
| Canned stubs from a fixed table | Generating probe words from IPA/groups/matrices/sets in the rule |
| Shape-aware **choice among stubs** (insert → `#_`, delete → input `x`, set → `{a}`…) | Building 3–8 `.wsca` lines per rule from field tokens |
| Same `validate_asca` + `asca_probe_words.wsca` | Changing default probe path to synthesized lexicon |
| Attribute failures for clustering / human triage | Claiming Tier 4 completeness via matching probes |

Field isolation is a **diagnostic lens** on syntax/shape, not a Tier 4 coverage upgrade.

## 8. Recommendation

**go-with-limits** — graduate a follow-on **task** ticket that:

1. Implements field-isolation only as an **optional inventory enrichment** (sidecar), defaulting to failing whole-rule rows.
2. Uses the stub table in §4, including shape-aware rows for insert/delete/metathesis/sets.
3. Keeps whole-rule `ok` as the primary metric; uses `blame` for correction triage (especially large `syntax_other` / mixed-field clusters).
4. Documents known disagreement cases (§5) in the ticket Notes so agents do not “fix” false fails by inventing probes.

**Kill** a follow-on only if the owner decides attribution is not worth ~4× ASCA calls on fails; the design itself is sound within limits.

## 9. Open questions (for follow-on task / grilling)

1. Should `blame=multi` (isolation all green, whole red) file into a dedicated failure class for set/condensed/insert clusters?
2. How far may set-cardinality stub heuristics go before they feel like a mini-parser (still OK vs ticket 10)?
3. Should absent optional fields be omitted from sidecar columns or recorded as `n/a`?
4. Handle bare `#` I/O as a pre-ASCA `format_error` in isolation, or teach a non-comment render path?
5. Run isolation on OK rules too (regression lens) or fails-only?
6. Interaction with ticket 34 (success/error CSV splits / ok-changelog): join sidecar in the same regen pass or a separate flag?

## 10. Sources

| Claim area | Source |
|------------|--------|
| Rule form / env / exception / insert-delete | asca-rust 0.10.2 `doc/doc.md` § The Basics |
| `.rsca` `#` description lines | asca-rust 0.10.2 `src/cli/parse.rs` (`parse_rsca`) |
| Parse pipeline / tiers | crate `parser.rs`, `mod.rs` (`split_into_subrules`), `error/syntax.rs`, `error/runtime.rs`; [asca-rule-validity.md](asca-rule-validity.md) |
| UnevenSet / LonelySet / InsertionNoEnv | `subrule/substitution.rs`, `subrule/insertion.rs` |
| Local compile + validate | `src/conlanger/tools/rules.py`, `phonological_ruleset.py`, `asca_validator.py`, `index_inventory.py` |
| Whole-rule inventory policy | [ticket 12](../issues/12-full-index-validation-inventory.md), [ticket 10](../issues/10-rule-derived-probe-synthesis.md) |
| CLI probes | local `asca 0.10.2` + `tests/fixtures/asca_probe_words.wsca` (temp under `.scratch/rule-index/tmp-*`, deleted after) |
