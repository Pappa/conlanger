Type: spike
Status: resolved

# Spike: native ASCA per-field validation effort

## Question

How much work would it take to modify **asca-rust** so it can validate a rule — and each section (`input` / `output` / `env` / `exception`) independently — as a private fork and/or an upstream contribution? Does that replace the stub engine in [Per-field ASCA blame in inventory](36-per-field-asca-blame-in-inventory.md)?

## Context

[Per-field ASCA blame in inventory](36-per-field-asca-blame-in-inventory.md) is ready to implement with canned stubs + `validate_asca` / `asca run` (spike 35 go-with-limits). An alternative is to add parse-only / per-field checking **inside asca**. Prior analysis of *where* asca validates lives in [asca-rule-validity.md](../research/asca-rule-validity.md); the 2026-08-04 session established that `asca run` is word-dependent at runtime and that `ParsedRules::try_from` is an unexposed parse-only check. Ticket 10 (probe synthesis) remains wontfix.

## What to investigate (primary sources)

1. asca 0.10.2 crate: visibility of `Parser::{get_input,get_output,get_context_block,get_except_block}`, `ParsedRules::try_from`, `Rule::split_into_subrules`.
2. CLI surface (`run` / `trace`) as a precedent for a `validate` command.
3. Which checks are field-local vs cross-field vs match-dependent.
4. Effort vs ticket 36 stubs; fork vs upstream.

## Deliverable

Findings markdown under `.scratch/rule-index/research/` with a sized work breakdown and a recommendation for ticket 36.

## Acceptance criteria

- [x] Cited crate/CLI/GitHub sources
- [x] Effort table (private fork vs upstream PR) by slice
- [x] Explicit comparison to stub isolation (false pass/fail)
- [x] Recommendation: build asca façade / keep stubs / both

## Answer

**~2–5 focused days for a private fork; ~1–2 weeks for an upstream-ready PR** to add whole-rule `validate` plus per-field `validate_part`. Not a parser rewrite: the four field grammars already exist as private `Parser` methods. Native field checks avoid stub false-fails (lonely sets, `#` `.rsca` wrap, deletion vs lexicon) but still cannot attribute cross-field / match-dependent errors — whole-rule `ok` stays SoT.

Findings: [research/asca-native-per-field-validation.md](../research/asca-native-per-field-validation.md).

**Ticket 36:** if this path is taken, retarget [Per-field ASCA blame in inventory](36-per-field-asca-blame-in-inventory.md) at asca per-field calls and drop the stub engine; if declined, implement 36 as written.

## Comments

- 2026-08-19 grill: **Q1 B** — whole-rule `validate` **plus** per-field `validate_part`. **Q2 C** — private fork only for now; no upstream. Clone: `/home/pappa/Projects/Pappa/asca-rust` (`github.com/Pappa/asca-rust`, vanilla **0.10.2** / `36c3c62`).
- 2026-08-19 grill: **Q3 A** — inventory `ok` stays `asca run` + probes. **Q4** — block [Per-field ASCA blame in inventory](36-per-field-asca-blame-in-inventory.md) (may rewrite/delete/close). **Q5 A** — [Implement `validate` + `validate_part` on the private asca fork](87-implement-asca-fork-validate.md) then [Wire conlanger to forked asca `validate`](88-wire-conlanger-forked-asca-validate.md). Version: asca-rust is `x.y.z` only (not git-describe); fork uses `0.10.3-dev` then `0.10.3`.
