Type: spike
Status: resolved
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Native ASCA per-field validation fork effort sizing.
Result: [0044-asca-native-per-field-validation.md](../spikes/0044-asca-native-per-field-validation.md)
Blocked by:

## Question

How much work would it take to modify **asca-rust** so it can validate a rule — and each section (`input` / `output` / `env` / `exception`) independently — as a private fork and/or an upstream contribution? Does that replace the stub engine in [Per-field ASCA blame in inventory](36-per-field-asca-blame-in-inventory.md)?

## Answer

**~2–5 focused days for a private fork; ~1–2 weeks for an upstream-ready PR** to add whole-rule `validate` plus per-field `validate_part`. Not a parser rewrite: the four field grammars already exist as private `Parser` methods. Native field checks avoid stub false-fails (lonely sets, `#` `.rsca` wrap, deletion vs lexicon) but still cannot attribute cross-field / match-dependent errors — whole-rule `ok` stays SoT.

Findings: [research/asca-native-per-field-validation.md](../spikes/asca-native-per-field-validation.md).

**Ticket 36:** if this path is taken, retarget [Per-field ASCA blame in inventory](36-per-field-asca-blame-in-inventory.md) at asca per-field calls and drop the stub engine; if declined, implement 36 as written.
