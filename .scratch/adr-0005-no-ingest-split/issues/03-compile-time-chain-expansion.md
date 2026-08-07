Type: task
Status: resolved
Blocked by: 01

# Compile-time chain expansion

## Question

Implement compile-time expansion when a corpus rule's `output` contains ` > ` (multi-step chain): one YAML row compiles to sequential ASCA rules (e.g. `input: a`, `output: b > c > d` → `a > b`, `b > c`, `c > d`).

**Corpus invariants** (grill 2026-08-07): a chained HTML line is still **one corpus rule** with one `input`, one `output` (chain in `output`), and at most **one** optional `env` and **one** optional `exception` — never per-step env/exception in YAML. Expansion splits the **output chain** only; rule-level `env`/`exception` attach to each emitted ASCA rule when present.

Wire into `SoundChangeRuleSet` / `RuleChange` so `validate_asca` exercises each expanded step. Slot into compile order per [ASCA compile transform ordering](../cleaned-rule-corpus/research/asca-compile-transform-order.md).

**Target:** recover ~136 ok rules lost when [Revert parse-time chain split](02-revert-parse-time-chain-split.md) lands. **Separate ticket** from revert — may be implemented and merged independently.

**Open during implementation:** whether other compile transforms run per-step or once on the joined string before split.

## Answer

**Done 2026-08-07.**

- `expand_chained_corpus_rule()` in `src/conlanger/tools/asca_compile/chains.py`.
- `SoundChangeRuleSet` expands each corpus rule to one `RuleChange` per chain step before compile; per-step rules run the full `compile_asca_rule_string` pipeline.
- Rule-level `env` / `exception` propagate to every emitted step.

**Design:** expand **before** per-step field join + compile transforms (not once on the multi-`>` joined string).

**Inventory (ASCA 0.10.2):**

| Metric | Before | After |
| --- | ---: | ---: |
| OK / total | 6395 / 9201 (69.5%) | **6527 / 9201 (70.9%)** |
| `syntax_other` fails | 1234 | **1078** (−156) |

+132 ok rules recovered vs pre-expansion baseline.
