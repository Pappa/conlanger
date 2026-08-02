Type: grilling
Status: resolved
Blocked by: 01, 02, 04

# Correction workflow for invalid rules

## Question

What is the efficient workflow to find and modify invalid rules (regex or other approaches; case-by-case vs class-of-rules), such that corrections land in the cleaned rule corpus and remain auditable against Index Diachronica HTML?

## Notes

- Skills: `/grill-with-docs` (or grilling + domain-modeling); `/prototype` if a cheap workflow artifact helps.
- Blocked on validity criteria, the valid/invalid inventory, and fidelity policy.
- Must honor fidelity policy from [Historical fidelity vs valid-but-inaccurate fallback](04-historical-fidelity-vs-validity.md) (class-first; optional corpus `status`; reasons in temporary validation CSV).
- [Create an ASCA validator for SoundChangeRule](08-asca-validator.md) supports this discussion but does not block it.
- Goal is reliability and scale beyond vibe-coded regex piles.

## Answer

### Where corrections live

Class-first transforms live in **`IndexDiachronicaParser`**. Cleaned YAML is **fully regenerated** on each run. Git-diff the regenerated YAML to catch inadvertent churn on unrelated rules; use that diff to grow unit tests. Skips need not be a durable overlay — a later parse+validate pass re-marks failures. An **external one-off override file** (status / rule translations for edge cases) will exist; **exact schema deferred**.

### `SoundChangeRule` dual role

1. **Temporary (now):** Parser builds section dicts → `SoundChangeRule` (one instance per HTML section leaf; class may need updates) so each sound change can be formatted/validated with `validate_asca` while iterating on the parser.
2. **Permanent (later):** Once YAML is the adopted SoT (few/no skips), load YAML → `SoundChangeRule` instances for the rest of the application.

Regenerated YAML remains the ticket-03 **applier-neutral corpus** (successor SoT); ASCA rendering/`SoundChangeRule` are the validate/runtime view.

### Validation grain

Validate **each sound change individually** (not whole-section-only). Section-wide shared failures (e.g. local abbreviations) are fine and support methodical section burn-down.

### Steady-state loop

1. Load HTML into memory.
2. For each section / rule: parse → `SoundChangeRule` → `validate_asca` per sound change.
3. Regenerate YAML output.
4. Update external rule-status metadata (shape deferred).
5. Update unit-test fixtures with samples whose **status changed**.
6. Cluster errors (validation report / pandas).
7. Reason about the top 3–5 classes and propose class-first resolutions (implement in parser; one-offs via override file later).

Honors ADR-0010 (class-first ladder, `status`, temporary validation CSV, owner-gated permanent skip/swap).
