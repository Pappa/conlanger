Type: spike
Status: resolved
Blocked by:

# Spike: ASCA representation of Khoisan clicks (`invalid_ipa`)

Spawned from `/grill-with-docs` on [map.md](../map.md) (2026-09-19). Blocks [136 correction pass — Khoisan click `invalid_ipa`](136-correction-pass-khoisan-click-invalid-ipa.md). Prior deferrals: [64 syntax_other near-miss](64-spike-syntax-other-near-miss-sections.md), [114 IPA prioritisation](114-spike-ipa-correction-prioritization.md).

## Question

How does **ASCA** (fork **0.10.3**, `github.com/Pappa/asca-rust`) represent **click** segments — and which **conlanger pipeline stage** can map Index Diachronica Unicode click letters (`ǃ`, `ǀ`, `ǁ`, `ǂ`, and related env/I/O shapes) to valid compiled rules without breaking historical fidelity?

**Do not implement** a correction pass until this spike resolves and [136](136-correction-pass-khoisan-click-invalid-ipa.md) is updated with the chosen lever.

## Baseline (inventory at ticket spawn)

| Metric | Value |
|--------|------:|
| `invalid_ipa` failures (active) | **47** |
| Click IPA tokens in messages | `ǃ` **25**, `ǀ` **11**, `ǁ` **6**, `ǂ` **5** |
| Primary section family | **§20.x** Khoisan |

Cluster CSV: [invalid_ipa_errors.csv](../inventory/error_clusters/invalid_ipa_errors.csv).

Example compiled fail:

```
ʊ > ɤ ! C:[+labial]_ and _l
```

(Index may mix click glyphs with prose env — classify rows in findings.)

## Research tasks

1. **ASCA primary sources** — read upstream/fork docs and implementation:
   - [Groupings / IPA / matrices](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md) (and 0.10.3 fork delta if any)
   - Crate IPA inventory, `validate` / lexer errors for click-like input
   - Whether clicks are **literal segments**, **feature matrices** (e.g. `[+click]`), **group references**, or **unsupported**

2. **Probe matrix** — for each Index glyph in the cluster (`ǃ`, `ǀ`, `ǁ`, `ǂ`, and ASCII `!` if used as click stand-in), record minimal rules that `asca validate` accepts or rejects on the fork pinned in [DEV.md](../../../docs/DEV.md).

3. **Pipeline fit** — recommend one primary path (with fallbacks):
   - **Parse-time** (`ipa_mappings.yml`, `manual_mappings.yml`) when ASCA uses stable literal segments and mapping is 1:1
   - **Compile-time** normalisation when Index letters must become ASCA feature bundles or grouped click classes programmatically
   - **Manual / overlay** (`index_diachronica_corrections.yml`, per-rule `manual_mappings`) when shapes are rule-specific or lossy
   - **Skip** (`skip_sections` / `skip_rules`) when no faithful ASCA projection exists

4. **Fidelity notes** — Index vs ASCA click inventory alignment (which contrasts are preserved vs collapsed); flag rules that need human review regardless of automation.

5. **Deliverable** — findings file: [research/asca-khoisan-click-representation.md](../research/asca-khoisan-click-representation.md) with a **Recommendation** section that names the correction-pass shape for ticket 136 (or `wontfix` / skip-only if no straightforward resolution).

## Answer

Findings: [research/asca-khoisan-click-representation.md](../research/asca-khoisan-click-representation.md). ASCA requires **inventory click clusters** (default `k` + release) or **`[+click]`**; bare Index glyphs fail `validate`. **136:** compile-time normaliser + manual residuals (§17 `Early-Modern-English-ʊ`, optional I/O, `!!`/`ǂɡ` edge cases).

## Acceptance criteria

- [x] Findings markdown committed under `.scratch/rule-index/research/`
- [x] Each Index click token in the inventory cluster classified (mappable / manual-only / skip)
- [x] Explicit recommendation: parse vs compile vs manual vs skip (or ordered combination)
- [x] Ticket [136](136-correction-pass-khoisan-click-invalid-ipa.md) unblocked with a short pointer in spike **Answer** (implementation stays on 136)

## References

- [ipa-correction-prioritization.md](../research/ipa-correction-prioritization.md)
- `config/parser/ipa_mappings.yml`, `config/compile/asca/group_mappings.yml` (`[+click]` rows if present)
- [Correction pass template](13-correction-pass-template.md) — instance 136 awaits this spike
