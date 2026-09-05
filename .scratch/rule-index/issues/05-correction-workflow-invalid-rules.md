Type: grilling
Status: resolved
Blocked by: 01, 02, 04

# Correction workflow for invalid rules

## Question

What is the efficient workflow to find and modify invalid rules (regex or other approaches; case-by-case vs class-of-rules), such that corrections land in the cleaned rule index and remain auditable against Index Diachronica HTML?

## Notes

- Blocked on validity criteria ([02](02-inventory-valid-vs-invalid-rules.md)), fidelity policy ([04](04-historical-fidelity-vs-validity.md)).
- [08-asca-validator](08-asca-validator.md) supports but does not block.

## Answer

Domain terms: **Class-first**, **Historical fidelity**, **Sound-change section**, **Corpus rule**, **Validation report**, **Failure class**, **Compile validation** — see `CONTEXT.md`.

### Where corrections live

**Class-first** transforms in `IndexDiachronicaParser`. Regenerate cleaned YAML each run; git-diff for churn control and fixture growth. External one-off override file deferred.

### Compile unit

One **sound-change section** (HTML `<h2>`) per compile container → **DiachronicSeries** (ticket 06). **Compile validation** per **index rule**, not whole-section-only.

### Steady-state loop

1. Parse HTML.
2. Per section / **index rule**: parse → compile → `validate_asca`.
3. Regenerate YAML.
4. Update validation metadata (shape deferred).
5. Fixture samples whose **rule status** changed.
6. Cluster errors → top **failure classes**.
7. Propose **class-first** fixes in parser; one-offs via override file later.

Policy: [ADR-0010](../../../docs/adr/0010-historical-fidelity-class-first-status.md) + ticket 04 edit ladder.
