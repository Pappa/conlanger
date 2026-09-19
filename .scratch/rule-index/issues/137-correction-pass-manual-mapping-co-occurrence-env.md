Type: task
Status: resolved
Blocked by: [60](60-parse-time-manual-rule-mappings.md)

# Correction pass: manual mapping — co-occurrence env prose (`if … occur`)

Target cluster: `expected_underscore` — Index env tails that describe **non-local co-occurrence** (not neighbour **position** — see grill [122](122-grill-proximity-conditions-yaml.md)) — **3** failing inventory rows today (**1** section **6.2.2.1.14** Moroccan Arabic `dʒ` family). Spawned from `/grill-with-docs` on [map.md](../map.md) (2026-09-19).

**Interim policy (until ticket 122 / structured `position` or broader conditioning lands):** use `config/parser/manual_mappings.yml` with the existing **`sporadic ;`** injection pattern ([123](123-grill-applicability-dialect-sporadic-conditions-yaml.md) documents the hack; do not wait for grill resolution).

## Problem

```
dʒ → {d,ɡ} / if s or z occur somewhere else in the word
dʒ → ʒ // if s or z occur somewhere else in the word
```

Parsed `env` / `exception` retain bare prose → compile env has no `_` → `expected_underscore`.

ASCA has no faithful env for “elsewhere in the word”; ticket [134](134-correction-pass-prose-conditional-env.md) defers this family here (not parse-time strip).

## What to build

1. Add **`manual_mappings.yml`** row(s) (substring `from` → `to`, `reason`):

   | `from` | `to` | Notes |
   |--------|------|--------|
   | ` / if s or z occur` | ` / sporadic ; if s or z occur` | Covers `Moroccan-Arabic-dʒ` alts 0–1 on line 1481 |
   | ` // if s or z occur` | ` // sporadic ; if s or z occur` | Covers `Moroccan-Arabic-dʒ_2` (line 1482) if substring differs |

   `raw` unchanged; mapping runs before other parse transforms ([60](60-parse-time-manual-rule-mappings.md)).

2. Confirm parse outcome after [77 first-`;` comment cut](77-implement-first-semicolon-comment-cut.md):
   - `sporadic: true` via `apply_sporadic_qualifier`
   - Prose tail after first `;` on rule **comment** (or equivalent field split)
   - Compiled env structural enough to validate (e.g. `_` or empty env per double-slash / sporadic handling)

3. `uv run create_index && uv run validate_rules`; record ok delta (**expect +3** on current inventory) and `expected_underscore` cluster in **Answer**.

4. Scan `expected_underscore_errors.csv` for additional `if … occur` / similar co-occurrence phrases; add mapping rows only when the same interim policy applies (document in **Answer**).

## Acceptance criteria

- [x] Manual mapping row(s) committed with `reason` citing interim policy + link to [122](122-grill-proximity-conditions-yaml.md)
- [x] `raw` unchanged; Moroccan `dʒ` rules validate or documented hold-out with cause
- [x] Full inventory re-run; metrics in **Answer**

## Answer

**Manual mappings** (`config/parser/manual_mappings.yml`): three substring rows with `reason: interim non-local co-occurrence env until issue 122 structured conditioning`:

| `from` | `to` |
|--------|------|
| ` / if s or z occur` | ` / sporadic ; if s or z occur` |
| ` / if ʃ is somewhere` | ` / sporadic ; if ʃ is somewhere` |
| ` / if ʒ is somewhere` | ` / sporadic ; if ʒ is somewhere` |

**Parse outcome:** `sporadic: true`, co-occurrence prose in `comment`, no bare prose `env` (same pattern as other `sporadic ;` injections).

**Inventory (2026-09-19):** **9003 / 9839** ok (**+4** vs pre-run **8999**); **`expected_underscore` 49** (−4 from **53**); sections all OK **501 / 714** (unchanged).

**Hold-out:** `Moroccan-Arabic-dʒ_2` (`dʒ → ʒ / else`) — catch-all else still needs a structural `_` in the immediately previous `env` ([53](53-correction-pass-prose-env-else.md)); after this pass the conditioned branch has no `env`, so the complementary `else` row remains one `expected_underscore` failure until structured conditioning or an agreed else pairing strategy.

**`expected_underscore_errors.csv` scan:** no remaining `if … occur` or `somewhere in the stem` co-occurrence phrases beyond the `dʒ_2` else hold-out.

## References

- `config/parser/manual_mappings.yml` — existing ` / sporadic ; …` rows (~lines 78+)
- [structured-rule-conditioning-exploration.md](../research/structured-rule-conditioning-exploration.md)
- [Correction pass template](13-correction-pass-template.md)
