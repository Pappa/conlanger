# Prefer SoT fidelity with class-first transforms; hold out meaning-changing cases

When cleaning Index Diachronica rules toward ASCA-valid **corpus rules**, prefer **historical fidelity** and **class-first** safe transforms; hold out meaning-changing cases. Domain terms in `CONTEXT.md`; this ADR records the trade-off.

## Considered Options

- **Class-first fidelity ladder + skip instead of inaccurate rewrite (chosen)** — scales mechanical fixes; keeps provenance honest; defers hard cases with filterable reasons (e.g. `valid-but-inaccurate`).
- **Allow valid-but-inaccurate substitutes when ASCA cannot express the claim** — maximises “compiles” metrics early; silently drifts from Index Diachronica.
- **Case-by-case human edit of every failure** — highest care per rule; does not scale to thousands of inventory failures.
- **Persist full state (`status`/`reason`/`description`) on every YAML rule** — convenient without the CSV; couples the applier-neutral corpus to validator diagnostics and bloats the SoT.

## Consequences

- Corpus field is thin optional `status` (`needs-validation` \| `skipped`); the older `skipped` reason-string field is superseded.
- Validation reports are analysis artifacts (e.g. pandas), not long-term SoT.
- Correction workflow, abbreviation, and feature-normalisation work follow this ladder and authority split (see wayfinder ticket *Historical fidelity vs valid-but-inaccurate fallback*).
