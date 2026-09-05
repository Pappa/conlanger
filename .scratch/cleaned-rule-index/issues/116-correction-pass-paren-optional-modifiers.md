Type: task
Status: resolved
Blocked by: None

# Correction pass: parenthetical optional segment modifiers

Target cluster: `expected_ipa` — parenthetical optional modifiers on segments — **21** failing rules (**8** mono-class sections would complete if cleared). Spawned from [114 IPA prioritisation spike](../issues/114-spike-ipa-correction-prioritization.md) (2026-09-05). Findings: [ipa-correction-prioritization.md](../research/ipa-correction-prioritization.md).

## Problem

Rules use Index parenthetical optional modifiers inside segments where ASCA expects bare IPA or matrices:

```
ɸ(ʼ,ʰ) > p
k > tʃ / _V:[+front]k(ʷ)
{tʷ:[+cg],tʷ,dʷ} > {tɕ(ʼ),tɕʷ(ʼ),tʃ(ʼ),tʃʷ(ʼ)}
ʔ > ∅ / _nk(ʷ)
```

Error: `Expected an IPA character, Primative or Matrix, but received '('` or `ʷ`.

Extends [48 parenthetical notation](../issues/48-correction-pass-parenthetical-segment-notation.md) and [111 cartesian I/O optionals](../issues/111-correction-pass-cartesian-io-optionals.md) Family B (modifier + segment).

## What to build

1. Classify `paren_optional_modifier` shapes ([ipa-correction-classes.csv](../research/ipa-correction-classes.csv)).
2. Compile pass: unwrap `(ʷ)`, `(ʲ)`, `(ʼ,ʰ)`, `(ˀ)` modifier optionals → cartesian segment variants or feature matrices.
3. Coordinate with 111 Family B (`k(ʰ){r,j}`) — reuse or extend existing compile step.
4. Full inventory re-run; before/after in **Answer**.

## Acceptance criteria

- [x] Target cluster sized at claim time from current inventory
- [x] Class-first compile transforms; `raw` unchanged
- [x] Full inventory re-run; metrics in **Answer**
- [x] Unit tests per modifier family (labialization, ejective/aspiration, glottal)

## Answer

**Shipped 2026-09-05.** Extended ticket 48 `expand_index_parenthetical_notation` in `src/conlanger/tools/compile/asca/parenthetical.py` (wired via `expand_meta_notation`).

### Implementation

- **Comma-separated modifiers:** `ɸ(ʼ,ʰ)` → `{ɸ,ɸʰ,ɸ:[+cg],ɸʰ:[+cg]}` (independent optional modifiers; aspiration before `[+cg]` for ASCA legality).
- **Embedded env suffix:** `_k(ʷ)`, `_nk(ʷ)`, `_V:[+front]k(ʷ)`, `n_k(ʷ)` → labialization alternates in place.
- **Glottal modifier:** `m(ˀ)` → `{m,mˀ}`; prefix `(ˀ)t` → `{ʔt,t}` (ASCA rejects leading `ˀ` in env sets).
- **Set members:** `{j(ˀ),…}`, `{p:[+cg],p,m(ˀ)}`, output `{tɕ(ʼ),…}` unchanged path via existing set expansion.
- **Regression guard:** do not short-circuit tokens containing `{` before prefix/infix expansion (preserves ticket 111 `(h)ə{p,b}` cartesian path).

### Inventory

Pre-pass summary: **8340 / 9827 ok (84.9%)**; `expected_ipa` **54**; `paren_optional_modifier` cluster **21** rules / **8** mono-class sections.

| Metric | Before | After | Δ |
|--------|-------:|------:|--:|
| OK / total | 8340 / 9827 (84.9%) | **8361 / 9827 (85.1%)** | **+21 ok** |
| Fail | 715 | **694** | **−21** |
| All-OK sections | 424 / 714 | **431 / 714** | **+7** |
| `expected_ipa` | 54 | **33** | **−21** |
| `paren_optional_modifier` | 21 | **0** | **−21** |

**ok flips (+21):** Quechumaran `ɸ(ʼ,ʰ)` ×5 (§34.1, §34.4, §34.5, §34.8, §34.9); Shuswap `m(ˀ)`/`j(ˀ)`/`n(ˀ)`/`l(ˀ)` ×3 (§35.3); Yaitepec `k(ʷ)` env (§32.1.3); Laze `{r,s}p(ʰ)` (§36.3.1.1); Iroquoian `_k(ʷ)`/`_nk(ʷ)`/`n_k(ʷ)` ×9 (§37.1.2.1–§37.1.2.6); Huron/Seneca mono-class (§37.1.2.2, §37.1.2.5).

**Residual:** `paren_optional_io` (2 mono-class sections — overlap tickets 48/111, deferred per prioritisation spike).

## References

- [Correction pass template](13-correction-pass-template.md)
- Scan bucket: `expected_ipa` / `paren_optional_modifier`
