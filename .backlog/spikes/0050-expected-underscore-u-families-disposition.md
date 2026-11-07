# Unrelated `expected_underscore` families (U1–U7) — disposition

Task: [0050-task-expected-underscore-env-prose-cluster.md](../items/0050-task-expected-underscore-env-prose-cluster.md). Post–**0046**–**0048** inventory. Syllable triage: [0045 spike](0045-expected-underscore-syllable-compile-review.md). Policy: [0025](../items/0025-decision-env-and-prose-conditions.md), [0017](../items/0017-decision-historical-fidelity-vs-validity.md).

## TLDR

| Metric | At 0045 triage | After syllable compile (2026-11-07) |
|--------|---------------:|------------------------------------:|
| `expected_underscore` rows | 102 | **76** |
| Nominal F1–F4 (0045 labels) | 40 | **15** (all legacy F3; **0** bare `%[±F]` / `U[±F]` in compiled env) |
| Post-syllable classifier F1–F4 | — | **0** ([`classify_expected_underscore_families.py`](../../diagnostics/inventory/analysis/classify_expected_underscore_families.py)) |

**No compile changes in 0050** — document hold-outs so prose / `else` / `//` rows are not mistaken for syllable underline work.

---

## Disposition table (per family)

| Family | Rows (post-syllable) | Chosen disposition | Rationale |
|--------|---------------------:|--------------------|-----------|
| **U1** bare `else` | 12 | **deferred** | Index `else` is editorial; not ASCA `/ env`. Future: structured `IndexContext`, `status: skipped`, or correction-pass per 0017. |
| **U2** Index prose env | 23 | **deferred** | Commas, `when…`, river names, stem-final phrasing. Env correction cluster; 0025 structured context preferred over literal env. |
| **U3** Index `//` in env | 6 | **deferred** | Index disjunction in env slot; ASCA wants `_` at focus. Split env/exception or skip until `//` policy is implemented. |
| **U4** prose inside `:{…}:` | 23 | **deferred** | Includes **15** rows reclassified from legacy **F3** (prose/`}:` tail after syllable matrix projection). No bare syllable host left. |
| **U6** other empty-token | 11 | **deferred** | Valid-looking env missing `_` for non-syllable reasons (`C[-nas]`, `iV`, tone env, …). Track per-cluster compile or skip. |
| **U7** stray character in env | 1 | **deferred** | `Old-Mandarin-w_2` — manual review / phoneme notation. |
| **F1–F4** (syllable) | 0 | **fixed** (0046–0048) | Underline scopes; remaining historical F3 labels on prose rows → **U4** in post-syllable classifier. |

**Fixed in 0046–0048:** all inventory rows whose sole `expected_underscore` cause was bare `%[±F]` / unclassified `position.in` / whole-field syllable env / env-set syllable tail (see 0046–0048 ticket Comments).

**Skipped / YAML:** none in this task — deferrals recorded here only; skips require a follow-up correction pass with explicit `status: skipped` and reason.

---

## Re-run classifier

```bash
uv run python diagnostics/inventory/analysis/classify_expected_underscore_families.py
```

Output: [`0050-expected-underscore-post-syllable-summary.json`](../../diagnostics/inventory/analysis/0050-expected-underscore-post-syllable-summary.json).

---

## References

- Triplets (2025-11 baseline): [`0045-expected-underscore-triplets.csv`](../../diagnostics/inventory/analysis/0045-expected-underscore-triplets.csv)
- Operator doc (syllable scopes): [`docs/system/sound-change-applier.md`](../../docs/system/sound-change-applier.md) (0049)
