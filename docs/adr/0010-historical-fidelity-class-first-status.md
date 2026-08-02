# Prefer SoT fidelity with class-first transforms; hold out meaning-changing cases

When cleaning Index Diachronica rules toward ASCA-valid corpus entries, **prefer faithfulness to the HTML source of truth** (the attested phonological claim; `raw`/`source` keep the surface line). Apply **class-first** safe transforms at scale — formatting, token replacement, and non-structural normalisation — then cluster remaining failures for investigation. Do **not** rewrite a rule into a valid-but-inaccurate form in the normal path; set optional corpus `status: skipped` (omit = ok; also `needs-validation` for structural normalisation pending a clean re-validate) and record full reason/description in a **temporary validation report CSV**. Permanent skip or rare same-intent swap requires project-owner approval; an agent may clear `needs-validation` when re-validation passes.

## Considered Options

- **Class-first fidelity ladder + skip instead of inaccurate rewrite (chosen)** — scales mechanical fixes; keeps provenance honest; defers hard cases with filterable reasons (e.g. `valid-but-inaccurate`).
- **Allow valid-but-inaccurate substitutes when ASCA cannot express the claim** — maximises “compiles” metrics early; silently drifts from Index Diachronica.
- **Case-by-case human edit of every failure** — highest care per rule; does not scale to thousands of inventory failures.
- **Persist full state (`status`/`reason`/`description`) on every YAML rule** — convenient without the CSV; couples the applier-neutral corpus to validator diagnostics and bloats the SoT.

## Consequences

- Corpus field is thin optional `status` (`needs-validation` \| `skipped`); the older `skipped` reason-string field is superseded.
- Validation reports are analysis artifacts (e.g. pandas), not long-term SoT.
- Correction workflow, abbreviation, and feature-normalisation work follow this ladder and authority split (see wayfinder ticket *Historical fidelity vs valid-but-inaccurate fallback*).
