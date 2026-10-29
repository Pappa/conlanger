Type: epic-duck:decision
Status: resolved
Plan: [0001-plan-migrate-project-to-duck-skills.md](0001-plan-migrate-project-to-duck-skills.md)
Overview: When wayfinder spikes (research) become `.backlog/` spike items and where findings files live.
Blocked by:

## Question

When migrating wayfinder **spike** tickets from `.scratch/` into duck-skills, which spikes get a `.backlog/` **`Type: spike`** (or linked findings), and where do findings files live?

Define **“still valuable”** (feeds open backlog work, documents constraints not captured in ADR/docs/GLOSSARY, etc.), whether to copy findings to `.backlog/spike/` or link `.scratch/.../research/` only, and how this applies to plan **0003** (~18 legacy spike files under `.scratch/rule-index/`).

Deferred from [wayfinder ticket migration policy](0006-decision-wayfinder-ticket-migration-policy.md) item 4.

## Answer

### Scope (rule-index / plan **0003**)

Migrate **exactly 13** findings markdown files from `.scratch/rule-index/research/` — the owner-curated set below. **Do not** migrate other wayfinder spikes (prioritisation spikes, nested-set inventory scans, `asca-compile-transform-order.md`, agent-docs spike, etc.) unless a later decision adds them.

| Findings (source) | Backlog spike item |
|-------------------|-------------------|
| `asca-rule-validity.md` | Convert wayfinder [01-valid-asca-rule-string](../../.scratch/rule-index/issues/01-valid-asca-rule-string.md) |
| `positional-slots-and-identity-subscripts.md` | **Retroactive** item (no wayfinder spike file); source list: issues [38](../../.scratch/rule-index/issues/38-spike-asca-compile-transform-order.md), [40](../../.scratch/rule-index/issues/40-correction-pass-positional-identity-subscripts.md) |
| `subscript-notation-index-asca-brassica.md` | **Retroactive** item; source list: issue [38](../../.scratch/rule-index/issues/38-spike-asca-compile-transform-order.md) |
| `asca-khoisan-click-representation.md` | Convert [138-spike-asca-khoisan-click-representation](../../.scratch/rule-index/issues/138-spike-asca-khoisan-click-representation.md) |
| `asca-class-letter-mappings.md` | Convert [09-spike-asca-class-letter-feature-matrices](../../.scratch/rule-index/issues/09-spike-asca-class-letter-feature-matrices.md) |
| `asca-ejective-notation.md` | **Retroactive** item; source list: issues [20](../../.scratch/rule-index/issues/20-correction-pass-ejective-marks.md), [84](../../.scratch/rule-index/issues/84-correction-pass-breve-vowel-notation.md) |
| `index-feature-matrices-to-asca-targets.md` | Convert [29-spike-index-feature-matrices-to-asca-targets](../../.scratch/rule-index/issues/29-spike-index-feature-matrices-to-asca-targets.md) |
| `index-syllable-position-u-hash.md` | Convert [58-spike-index-syllable-position-u-hash](../../.scratch/rule-index/issues/58-spike-index-syllable-position-u-hash.md) |
| `inter-segment-whitespace-phoneme-boundaries.md` | Convert [44-spike-inter-segment-whitespace](../../.scratch/rule-index/issues/44-spike-inter-segment-whitespace.md) |
| `io-optionals-asca-and-convention.md` | Convert [100-spike-io-optionals-asca-and-convention](../../.scratch/rule-index/issues/100-spike-io-optionals-asca-and-convention.md) |
| `breve-vowel-notation.md` | Convert [80-spike-breve-vowel-notation](../../.scratch/rule-index/issues/80-spike-breve-vowel-notation.md) |
| `field-isolation-compile-validation.md` | Convert [35-spike-field-isolation-compile-validation](../../.scratch/rule-index/issues/35-spike-field-isolation-compile-validation.md) |
| `asca-native-per-field-validation.md` | Convert [86-spike-asca-native-per-field-validation](../../.scratch/rule-index/issues/86-spike-asca-native-per-field-validation.md) |

**Do not merge** findings or spike items for similarity; each row stays one findings file and one backlog **`Type: spike`** row on **0003**.

### “Still valuable” (future efforts **0004**, **0005**, and additions)

Use the **curated-set** rule above for rule-index. For other `.scratch` trees later: migrate a spike only when the owner (or migration pass) names it explicitly — typically because **`docs/`**, **`src/`**, or **`GLOSSARY.md`** still link to the findings, or the markdown remains the canonical spec for planned work not fully captured in ADRs / decision **Answer** sections. One-off prioritisation spikes that only filed correction passes stay in `.scratch` archaeology only.

### Findings location and artefacts

- **Copy** each migrated findings **`.md`** into [`.backlog/spike/`](../spike/) as `<NNNN>-<slug>.md`, matching the new backlog spike item number ([backlog.md](../../docs/agents/backlog.md)).
- **Do not** copy CSVs, scripts, probe directories, or other artefacts; **edit** the copied markdown to remove or rewrite passages that depend on those artefacts (probes, regenerate commands, appendix CSVs).
- **Do not** update links inside files under `.scratch/` (`.scratch/` is retired when plan **0001** completes).
- **Do** update **living** links in `docs/` and `src/` to point at `.backlog/spike/…`.

### Spike backlog items

- **`Type: spike`** (rubber-duck), **`Plan:`** [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md), **`Status: resolved`** after migration (historical research).
- **`Result:`** → migrated file under `.backlog/spike/` ([backlog.md](../../docs/agents/backlog.md)).
- **10 conversions:** reshape wayfinder spike tickets into duck-skills spike item shape (Question / Answer or equivalent summary, **source list** of wayfinder issue paths).
- **3 retroactive items** (positional, subscript, ejective): **best-effort** bodies summarising question, outcome, and source list — no requirement to recover a lost wayfinder spike file verbatim.

### Cap (**0006** amendment)

Plan **0003** keeps **≤25** indexed outcomes for **Decisions** table rows + **Decisions so far** gists + **`Type: task`** items combined ([0006](0006-decision-wayfinder-ticket-migration-policy.md)). **`Type: spike`** rows on **0003** are **counted separately** and are **not** subject to that ≤25 cap.

### Link hygiene

No CI or standing grep gate for `.scratch` research links. When plan **0001** is fully resolved, `.scratch/` is deleted; until then, living docs must not depend on scratch paths for migrated spikes (update as part of spike migration execution).

### Other product plans

Apply the same exclusions as **0006** (terminal / superseded) and the findings-copy rules when spikes appear under **0004** or **0005**; spike rows count separately from any numeric cap on those plans’ decisions and tasks.

## Comments

- 2026-10-29: Owner deferred spike rules during **0006** resolution; rule-index map migration proceeds with **zero** spike rows until this decision is resolved.
- 2026-10-29: Resolved — curated 13 findings; copy markdown only; 10 ticket conversions + 3 retroactive spikes; living link updates only; spikes excluded from ≤25 cap; no link-enforcement automation (scratch tree removed at **0001** completion).
