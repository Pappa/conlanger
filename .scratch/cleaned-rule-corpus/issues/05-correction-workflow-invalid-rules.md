Type: grilling
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
