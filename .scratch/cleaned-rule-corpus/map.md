wayfinder:map

# Cleaned rule corpus SoT

## Destination

A cleaned, applier-neutral YAML **rule corpus** adopted as the working source of truth — derived from Index Diachronica HTML — where each rule’s fields are well-formed enough to **compile to valid ASCA**, preferring historical fidelity and falling back to valid-but-inaccurate only when there is no other choice; plus a **reliable method** to find and fix invalid rules at scale.

## Notes

- Domain: sound-change ingestion / Index Diachronica → rule corpus → ASCA (Brassica later). Read `CONTEXT.md` and ADRs 0001–0009 before any ticket work.
- Skills: `/research` (ASCA validity), `/grill-with-docs` or grilling + domain-modeling (schema, policy, workflow), `/prototype` if a correction UX needs a cheap artifact.
- Standing preferences: ASCA-first but multi-applier capable (ADR-0001); neutral YAML corpus (ADR-0002); validate after compile (ADR-0003); keep series indices (ADR-0004); one corpus rule per HTML line with rare edge splits (ADR-0005); HTML is current SoT (`notebooks/data/index_diachronica_original.html`), cleaned YAML is planned successor (ADR-0006).
- Tracker: local markdown — see `docs/agents/issue-tracker.md` Wayfinding operations.

## Decisions so far

- [What counts as a valid ASCA rule string?](issues/01-valid-asca-rule-string.md) — ASCA form is `input ARROW output [/env] [|exception]`; non-empty I/O (`*`/`∅` insert/delete, `&` metathesis); one `_` focus in env; `#` env-peripheral only; check via `asca run words.wsca -r rule.rsca`. Findings: [research/asca-rule-validity.md](research/asca-rule-validity.md).
- [YAML schema for the cleaned rule corpus](issues/03-yaml-schema-cleaned-rule-corpus.md) — Top-level `abbreviations` + `sections`; rules carry `input`/`output`/`raw`/`source` (optional `env`/`exception`/`skipped`); ID-shaped strings; hierarchical string→string abbreviation tables; multi-line `raw` via `\|`; HTML SoT `index_diachronica_original.html` via lxml.
- [Inventory which current rules compile and which fail](issues/02-inventory-valid-vs-invalid-rules.md) — Provisional AI YAML: 9721 rules → 5554 ok / 4167 fail under `asca 0.9.3`; CSV + summary in [inventory/](inventory/).

## Not yet specified

- Exact prose-environment mapping approach (investigative spike; may graduate after schema + validity work)
- Adoption criteria for when cleaned YAML *replaces* HTML as SoT
- How abbreviation tables are authored and maintained at scale (policy for unsupported keys lives on [Resolve abbreviations unsupported by ASCA and Brassica](issues/06-resolve-applier-unsupported-abbreviations.md); this fog is authorship/maintenance at scale)
- Brassica compiler details (out of near-term path, but in-principle per ADR-0001)
- Edge-split policy when one HTML line must become multiple corpus rules (deferred; interim: optional `skipped` reason with empty input/output)

## Out of scope

- Generative sound-change *sequences* model — see Future Work in `docs/README.md` and [Generative sound-change sequences (GAN or next-in-sequence)](../sound-change-sequences/issues/01-generative-sound-change-sequences.md)
- Bundle ~100 preset inventories — [Bundle ~100 pre-generated phoneme inventories](../phoneme-inventories/issues/01-bundle-100-pregenerated-inventories.md)
- Automate PHOIBLE/WALS prep — [Automate PHOIBLE and WALS data preparation pipeline](../data-processing-pipeline/issues/01-automate-phoible-wals-prep.md)
- Full Brassica adoption / shipping a Brassica compiler
