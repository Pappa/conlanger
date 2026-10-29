Type: spike
Status: resolved
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: ASCA representation of Khoisan click segments.
Result: [0035-asca-khoisan-click-representation.md](../spike/0035-asca-khoisan-click-representation.md)
Blocked by:

## Question

How does **ASCA** (fork **0.10.3**, `github.com/Pappa/asca-rust`) represent **click** segments — and which **conlanger pipeline stage** can map Index Diachronica Unicode click letters (`ǃ`, `ǀ`, `ǁ`, `ǂ`, and related env/I/O shapes) to valid compiled rules without breaking historical fidelity?

**Do not implement** a correction pass until this spike resolves and [136](136-correction-pass-khoisan-click-invalid-ipa.md) is updated with the chosen lever.

## Answer

Findings: [research/asca-khoisan-click-representation.md](../spike/asca-khoisan-click-representation.md). ASCA requires **inventory click clusters** (default `k` + release) or **`[+click]`**; bare Index glyphs fail `validate`. **136:** compile-time normaliser + manual residuals (§17 `Early-Modern-English-ʊ`, optional I/O, `!!`/`ǂɡ` edge cases).

## Source list

- `legacy wayfinder rule-index issue 138-spike-asca-khoisan-click-representation.md`
