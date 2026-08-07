wayfinder:map

# ADR-0005: no ingest split

## Destination

[ADR-0005](../../docs/adr/0005-one-corpus-rule-per-html-line.md) amended: **one Index rule line → one corpus rule**, always — including multi-step sound-change **chains** on a single line. The ingest-split **exception** is removed. Sequences stay in YAML as a single row (`output` retains ` > ` chains); **compile-time** expansion produces the sequential applier rules ASCA needs. Parent effort: [Cleaned rule corpus SoT](../cleaned-rule-corpus/map.md).

## Notes

- Glossary: `CONTEXT.md` — **Corpus rule**, **Sound-change sequence**.
- ADRs: amend **0005**; **0010** skip ladder unchanged for truly unrepresentable lines (no ingest split as escape).
- Skills: `/grilling`, `/domain-modeling`, `/prototype` if compile expansion shape needs a spike.
- Code: revert parse-time `expand_chained_rule_parts` ([Correction pass: chained rules — parse-time split](../cleaned-rule-corpus/issues/18-correction-pass-chain-split.md)); add compile-time chain expansion in `src/conlanger/tools/` (likely `RuleChange` / `SoundChangeRuleSet` or `asca_compile/` pipeline).
- Tracker: `docs/agents/issue-tracker.md`.

## Decisions so far

- [Amend ADR-0005 — remove ingest-split exception](issues/01-amend-adr-0005-remove-ingest-split-exception.md) — Never inflate corpus rows at ingest; compile-time expansion only; unrepresentable → `status: skipped` (ADR-0010); supersedes ticket 18; opaque YAML strings; revert and compile expansion are separate tickets.
- [Corpus shape for chained rules (env / exception)](issues/04-compile-time-chain-expansion-with-env.md) — One corpus rule per HTML line: single `input`, single `output` (chain in `output`), at most one `env` and one `exception`; compile splits output chain only; same env/exception on each emitted ASCA rule.
- [Revert parse-time chain split](issues/02-revert-parse-time-chain-split.md) — Removed `expand_chained_rule_parts`; corpus **9201** rules (−116); **6395 / 9201 ok (69.5%)** until compile expansion.
- [Compile-time chain expansion](issues/03-compile-time-chain-expansion.md) — `expand_chained_corpus_rule` in `asca_compile/chains.py`; `SoundChangeRuleSet` emits one `RuleChange` per step; **6527 / 9201 ok (70.9%)** (+132 ok).

## Not yet specified

- **Validation granularity** — per expanded ASCA step vs whole corpus rule; interaction with field-isolation sidecar ([ticket 36](../cleaned-rule-corpus/issues/36-field-isolation-inventory-sidecar.md)).
- **YAML shape for non-chain multi-change lines** — alternations/sets already fit ADR-0005 “internal structure”; confirm no other parse-time row inflation besides chain split.
- **Timing vs [Refactor SoundChangeRuleSet](../cleaned-rule-corpus/issues/39-refactor-sound-change-ruleset.md)** — chain compile step slots into spike 38 order; refactor may follow or absorb.

## Out of scope

- Generative sound-change sequences model — [Generative sound-change sequences](../sound-change-sequences/issues/01-generative-sound-change-sequences.md)
- Brassica compile path for chains (defer until Brassica compiler exists; ADR-0001)
- Re-opening correspondence-series parse-time expansion (ADR-0004 / ticket 27) — that expands tokens inside fields, not corpus row count
