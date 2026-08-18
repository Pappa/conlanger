Type: grilling
Status: resolved
Blocked by:

# Grill: correspondence-series mapping source of truth (manual SoT vs rule I/O inference)

## Question

Given that **rule I/O inference** in `series_mappings.csv` conflates *sound changes* with *abbreviation definitions* — and can **destroy** the changes it inferred from when maps are applied at parse time — what should replace the current auto-extraction policy?

Decide:

1. **What counts as an authoritative mapping row** (prose, inventory tables, manual curation, conventional reconstructions like PIE laryngeals — vs inferring from parallel/singleton rules).
2. **Where the SoT lives** (manual table only? hybrid with HTML prose extraction into `section_abbreviations.yml` as advisory?).
3. **What to do with unresolvable / unknown correspondence-series tokens** at compile time (user-supplied config vs `status: skipped` vs leave literal and fail validation).
4. **Whether to revert or quarantine** existing I/O-inferred rows (e.g. `d₁ → d` from Paiwan, `x₁ → k` from Omotic singletons, `s₁ → ʃ` from Aari chains) and how that interacts with [ticket 65](65-series-mappings-coverage-pass.md)’s 100% in-scope coverage metric.

## Background (recent discussion)

### `section_abbreviations.yml`

We added prose/table extraction into `data/diachronica/section_abbreviations.yml` (tokens + `raw` source text). It lists tokens **mentioned** in non-`schg` HTML; it does **not** drive parse expansion. Current entries include Afro-Asiatic `s₁`–`h₂`, PIE inventory `h₁`–`h₃`, Albanian prose-only `h₃`/`h₄`, Niger-Congo table `d₂`.

### “Are all these unresolvable? Should rules be skipped?”

**Partially correct linguistically, not how the project currently works.**

- Linguistically: Afro-Asiatic series members are “indeterminate reconstruction”; Albanian `h₄` is explicitly hypothetical (“if it existed”).
- In code: `series_mappings.csv` (107 rows) **does** map many tokens — often to **opaque ASCA placeholders** (`s₁ → f1`) or **inferred IPA from rules** (`x₁ → k`), not to independently verified phonetics.
- Policy ([ticket 26](26-parse-time-correspondence-series-indices.md), ADR-0004): unmapped tokens stay literal; **no pre-emptive `status: skipped`** during correction; compile validation fails to drive map authoring.
- Prose-only tokens (e.g. `h₄`) do not appear in `schg` rules today.

### `d₁ → d` and parallel I/O inference

Row sourced from Paiwan rule:

```text
t₁ d₁ d₃ Z → t d ɖ ɟ
```

Extractor (`infer_parallel_rule_mappings`) zips input/output slots and treats aligned pairs as **definitions** (`d₁ → d`). That rule actually encodes **four simultaneous changes**, not “`d₁` means /d/”.

When `expand_series_tokens_in_field` applies the map to **all stages**, the rule becomes:

| Stage | Before | After expansion |
| --- | --- | --- |
| Input | `t₁ d₁ d₃ Z` | `t d ɖ Z` |
| Output | `t d ɖ ɟ` | `t d ɖ ɟ` |

Changes on `t₁`, `d₁`, `d₃` collapse to identity; only `Z → ɟ` remains. Same class of bug as singleton `x₁ → k` → `k → k`.

**Category error:** confusing *diachronic development* (X becomes Y in this rule) with *notation expansion* (X stands for segment Y in this section).

### Owner direction (high level, for this grill)

- **Replace** incorrect auto-inferred mappings with a **manual mapping table**.
- Include **commonly accepted mappings** where they exist (e.g. PIE laryngeals via `apply_asca_aliases`: `h₁→h`, `h₂→x`, `h₃→ɣʷ`).
- **List unresolvable symbols** explicitly.
- At compile time: either resolve via **user input config** or **skip** rules that still contain tokens with no resolvable mapping.

## Facts (do not re-litigate without new evidence)

- Parse expansion: `apply_series_mappings` / `expand_series_tokens_in_field` in `src/conlanger/utils/series.py` — global substring replace on all `stages` + env/exception.
- Extraction: `infer_parallel_rule_mappings`, `infer_singleton_rule_mappings` in `src/conlanger/tools/series_extract.py`; [ticket 28](28-extract-correspondence-series-mappings-from-html.md) explicitly allowed I/O inference; [ticket 65](65-series-mappings-coverage-pass.md) expanded it to 100% in-scope coverage.
- `section_abbreviations.yml` ≠ `series_mappings.csv`; YAML is documentary, CSV drives parse.
- `apply_asca_aliases` runs at **compile**, not parse; maps Unicode laryngeals to conventional IPA.

## Constraints / links

- ADR-0004, ADR-0010 (skip policy), `CONTEXT.md` (**Correspondence-series index** vs sound-change **stages**).
- Existing data: `data/asca/series_mappings.csv`, `data/diachronica/section_abbreviations.yml`, `manual_mappings.csv` pattern ([ticket 60](60-parse-time-manual-rule-mappings.md)).
- Skills: `/grilling`, `/domain-modeling`.

## Outcomes this grill should produce

A recorded decision on:

- Authoritative sources for mapping rows (and whether I/O inference is retired or demoted).
- Manual table shape, ownership, and relationship to `section_abbreviations.yml`.
- Runtime policy for unknown series tokens (config vs skip vs fail).
- Migration plan for the current CSV (revert inferred rows? split “definition” vs “attested in rules” columns?).

Follow-on implementation tickets should be filed **after** this grill closes — not in this session.

Series ontology (what may be a defined expansion; unknown-token policy) moved to [ticket 73](73-grill-series-mapping-config-sot.md).

## Comments

- 2026-08-16 grill session: ingest pipeline overtook the original question. Settled so far: pre-lxml `<sub>`→Unicode (skip nested tags); in-memory HTML only; **Index Diachronica correction** replaces **raw** by **rule id** (flat YAML, Unicode lines); Manual mapping never mutates raw (first match, optional regex); **rule id** replaces positional `rule_idx` everywhere; unmatched correction keys warn. Q10 reversed: this work **removes** parse-time `series_mappings.csv` / expansion; PIE aliases stay in Python (ticket 73); inventory `ok` drop accepted. Collective subscripts also stay Index-shaped at parse. `section_abbreviations.yml` left as a stale advisory snapshot (not regenerated); corpus section `abbreviations` omitted when empty.
- 2026-08-18: Owner confirmed shared understanding (Q1 option 1). Ticket closed; implementation filed as [74](74-implement-ingest-corrections-drop-series-csv.md). Series ontology remains [73](73-grill-series-mapping-config-sot.md).

## Answer

### Ingest pipeline (this work)

1. Load HTML in memory only (never write the file).
2. Whole-file `<sub>…</sub>` → Unicode (`to_subscript`); nested inner tags: skip that tag; tree walk extracts text only.
3. lxml parse.
4. For each `p.schg`, extract text. If `index_diachronica_corrections.yml` has that **rule id**, that Unicode line **is `raw`**. Missing file = no replacements. Unknown keys: warn; use HTML extract.
5. **Manual mapping** on working copy only (first match; `use_regex` → `from` is a pattern). `raw` unchanged.
6. Rest of parse **without** `apply_series_mappings`.

**Rule id** (HTML `id`) replaces `rule_idx` on corpus rules, inventory, changelogs, and debug CSVs. Corrections file: flat YAML `rule_id: line`, Unicode, no `<sub>`.

**Retire parse-time series expansion:** delete `series_mappings.csv` apply path from parse; do not regenerate `section_abbreviations.yml`; omit empty section `abbreviations`. Correspondence-series and collective tokens stay Index-shaped. Inventory `ok` drop accepted.

`PIE_LARYNGEAL_ALIASES` stays in Python at compile until [ticket 73](73-grill-series-mapping-config-sot.md).

### Deferred to ticket 73

What counts as an authoritative expansion row; config shape and layer; indeterminate/unknown token policy (config vs skip vs fail); collective handling under any future config; migration of any manually curated rows. I/O inference and opaque placeholders (`s₁→f1`) are **not** a SoT.

### ADRs

- [ADR-0004](../../../docs/adr/0004-series-indices-per-section-maps.md) amended (parse-time CSV retired).
- [ADR-0012](../../../docs/adr/0012-index-diachronica-corrections-overlay.md) (corrections overlay).

### Implementation

[Implement ingest corrections overlay and drop parse-time series CSV](74-implement-ingest-corrections-drop-series-csv.md).
