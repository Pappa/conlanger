Type: task
Status: resolved
Blocked by: None

# Correction pass: editorial slash and prose residue in compile fields

Target cluster: `expected_ipa` — editorial `/gloss/` slashes and unclosed-prose residue in compile fields — **30** failing rules (**8** mono-class sections would complete if cleared). Spawned from [114 IPA prioritisation spike](../issues/114-spike-ipa-correction-prioritization.md) (2026-09-05). Findings: [ipa-correction-prioritization.md](../research/ipa-correction-prioritization.md).

## Problem

Rules carry Index editorial slashes or prose tails inside I/O or env fields where ASCA expects IPA:

```
Original z (/ts/?) > dj
ɡ > j / V_ (if /j/ resulted, it dropped after /i/
{a/e} {e/a} > e a
V > ∅ / V:[+stress]$_(C)(C)V(C)# (
```

Error: `Expected an IPA character, Primative or Matrix, but received '/'` (or `''` from unclosed `(`).

Distinct from [108 double-slash env](../issues/108-correction-pass-double-slash-env.md) (`expected_underscore` bare `//`) and [21 trailing glosses](../issues/21-correction-pass-trailing-glosses.md) (parse-time strip at ingest).

## What to build

1. Classify shapes in `editorial_slash_gloss` bucket ([ipa-correction-classes.csv](../research/ipa-correction-classes.csv)).
2. Compile normalisation:
   - Strip editorial `/phoneme/` glosses to `comment` (preserve `raw`).
   - Peel unclosed `(` prose tails from env/I/O into `comment`.
   - Expand structural `{a/e}` vowel alternation → `{a,e}` (Tupi §18.3.x).
3. Defer `ipa_mappings` hold-outs (`*`, `@`) and malformed chains (§17.7.3.1.1).
4. Full inventory re-run; before/after in **Answer**.

## Acceptance criteria

- [x] Target cluster sized at claim time from current inventory
- [x] Class-first compile transforms; no silent meaning change
- [x] Full inventory re-run; metrics in **Answer**
- [x] Unit tests per supported shape family

## Answer

Implemented 2026-09-05.

### Segment shapes

| Shape | Example | Compile rewrite |
|-------|---------|-----------------|
| Set vowel alternation | `{a/e}`, `{o,u/y}` | `{a,e}`, `{o,u,y}` |
| Editorial phoneme slash | `/j/`, `/ts/?`, `(/ts/?)` | strip slashes / remove paren gloss |
| Unclosed paren prose tail | `V_ (if /j/ resulted…`, `_n{C,#} (Souletin` | peel trailing `(…` gloss |

Compile strips prose from fields only; index `raw` unchanged (ADR-0010). Prose often already captured in parse-time `comment` (ticket 30/31); compile peel complements parse-time `include_unclosed_paren=False` on env/exception (ticket 82).

### Code

- `normalize_editorial_slash_gloss_residue()` in `editorial_slash_gloss.py`; wired first in `compile_asca_field_pre_subscript`.

### Inventory

Before: **8321 / 9827 ok (84.7%)**; **734** fail; **417 / 714** sections all-OK; `editorial_slash_gloss` **30** rules (**8** mono-class sections).

After: **8340 / 9827 ok (84.9%)**; **715** fail; **424 / 714** sections all-OK (**+7** section-complete); `expected_ipa` **77 → 54**.

**Recovered (19 rules):** Tupi `{a/e}` §18.3.x (4), Old Provençal `/j/` + `_{o,u/y}` (5), Catalan/Basque/Motilón/Eritai/Salish unclosed-paren env (7), Franconian `(short only` (1), Spanish `ʎ` collateral (1), chain alt (1).

**Residual `editorial_slash_gloss` (12 rules, scan classifier):** deferred/misclassified — malformed chains §17.7.3.1.1 (`>`), Guānhuà `∅` env sets, ellipsis `…` prose, French truncated env, Middle Dutch prose env (`expected_underscore`), parenthetical modifiers `ʰ`/`ʲ` (ticket 116). No mono-class sections remain in bucket.

## References

- [Correction pass template](13-correction-pass-template.md)
- Scan bucket: `expected_ipa` / `editorial_slash_gloss`
