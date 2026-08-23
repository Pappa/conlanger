Type: grilling
Status: resolved

# Historical fidelity vs valid-but-inaccurate fallback

## Question

When a rule cannot be expressed in a form that is both historically faithful and ASCA-valid after compile, what is the decision policy — case-by-case vs class-of-rules — and who approves a valid-but-inaccurate substitute?

## Notes

- Amends schema from [YAML schema for the cleaned rule index](03-yaml-schema-cleaned-rule-index.md): replaces `skipped` reason field with optional `status`.

## Answer

Domain terms: **Historical fidelity**, **Class-first**, **Rule status**, **Validation report**, **Skipped**, **Raw**, **Source** — see `CONTEXT.md`.

### Edit ladder (apply **class-first** at scale)

1. **Simple formatting** — OK.
2. **Simple token replacement** — OK.
3. **Trailing undelimited comments** — extract to compile comment; else `status: skipped` (CSV reason `trailing-comment`).
4. **Normalisation** — safe swaps OK; structural changes → `status: needs-validation`, clear on re-validate.
5. **Broken / unclear intent** → `status: skipped`.
6. **Clear phonology, ASCA-unrepresentable** → `status: skipped`.
7. **Valid-but-inaccurate rewrite** (would change the claim) → do not rewrite; `status: skipped`, CSV reason `valid-but-inaccurate`.
8. **Other** → `status: skipped`.
9. **Later (rare)** — permanent skip or same-intent swap: **project owner only**.

### Corpus `status` vs validation CSV

| Layer | What |
|-------|------|
| YAML index | Optional `status: needs-validation \| skipped` (omit = ok). Empty `input`/`output` when **skipped**. |
| **Validation report** | Full state: status, `reason`, `description`, validator detail. Not SoT. |

CSV `reason` vocabulary: `trailing-comment`, `broken-syntax`, `asca-unrepresentable`, `valid-but-inaccurate`, `other`.

### Authority

- Defined transform classes: apply without per-rule approval.
- `needs-validation`: agent may clear on clean re-validate.
- Permanent **skipped** / rare swaps: project owner only.

### ADR

[ADR-0010](../../../docs/adr/0010-historical-fidelity-class-first-status.md).
