Type: grilling
Status: resolved

# Historical fidelity vs valid-but-inaccurate fallback

## Question

When a rule cannot be expressed in a form that is both historically faithful and ASCA-valid after compile, what is the decision policy — case-by-case vs class-of-rules — and who approves a valid-but-inaccurate substitute?

## Notes

- Skills: `/grill-with-docs` (or grilling + domain-modeling).
- Working preference from charting: prefer historical fidelity; fall back to valid-but-inaccurate only when there is no other choice; consider case-by-case or by class when the same issue repeats.
- This ticket locks that preference into an explicit policy for the correction workflow.
- Amends schema from [YAML schema for the cleaned rule corpus](03-yaml-schema-cleaned-rule-corpus.md): replaces `skipped` reason field with optional `status`.

## Answer

### Fidelity bar

Prefer faithfulness to Index Diachronica HTML (`index_diachronica_original.html`). Faithfulness means the **attested phonological claim**, not byte-identical surface spelling. `raw` / `source` preserve the HTML line for audit.

### Edit ladder (apply class-first at scale)

1. **Simple formatting** — OK (HTML inconsistency → consistent YAML/ASCA-acceptable form).
2. **Simple token replacement** — OK (token→token so ASCA accepts the rule).
3. **Trailing undelimited comments** — attempt to extract onto the `SoundChangeRule` comment; if unresolved → `status: skipped` (CSV reason e.g. `trailing-comment`).
4. **Normalisation** — safe synonym/feature/length token swaps OK; **structural** changes → `status: needs-validation`, then clear when the validator passes.
5. **Broken / unclear intent** → `status: skipped`.
6. **Clear phonology, ASCA-unrepresentable** (e.g. unequal sets) → `status: skipped`.
7. **Only path would change the phonological claim** (“valid-but-inaccurate” rewrite) → **do not rewrite** in this effort; `status: skipped` with CSV reason `valid-but-inaccurate`.
8. **Other** → `status: skipped`.
9. **Later (rare uniques)** — permanent skip or swap for a same-intent valid rule only with **project-owner approval**.

### Class-first

Define reusable rewrite classes; apply mechanically corpus-wide. Gather remaining failures via validator output, group by prevalence, prioritise widespread issues. Case-by-case is for leftovers and human-gated exits.

### Corpus `status` vs validation CSV

| Layer | What |
|-------|------|
| YAML corpus | Optional `status: needs-validation \| skipped` (omit = `ok`). Replaces the old `skipped` reason string. Empty `input`/`output` when skipped. |
| Temporary CSV | Full state for pandas: status, controlled `reason`, `description`, validator-derived detail. Not permanent SoT. |

Suggested CSV reason vocabulary: `trailing-comment`, `broken-syntax`, `asca-unrepresentable`, `valid-but-inaccurate`, `other`.

### Authority

- Defined classes (formatting / tokens / safe normalisation): apply without per-rule approval.
- `needs-validation`: agent may clear when re-validation passes after a structural fix.
- Permanent `skipped` and rare same-intent swaps: **project owner only**.

### Schema / glossary

Amends ticket 03: drop corpus `skipped`; add optional `status`. Glossary: **Rule status**, **Validation report**; **Skipped** retained as a status value — see `CONTEXT.md`.

### ADR

[ADR-0010: Prefer SoT fidelity with class-first transforms; hold out meaning-changing cases](../../../docs/adr/0010-historical-fidelity-class-first-status.md).
