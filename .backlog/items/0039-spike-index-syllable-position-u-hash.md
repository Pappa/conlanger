Type: spike
Status: resolved
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Index `#U` / `U#` syllable position → ASCA env structures.
Result: [0039-index-syllable-position-u-hash.md](../spike/0039-index-syllable-position-u-hash.md)
Blocked by:

## Question

How should Index Diachronica **syllable-position** tokens (`#U` = word-initial syllable, `U#` = word-final syllable) be represented in ASCA when they appear in **exception** or **environment** fields on **segment-level** rules — e.g. Old Norse `Vː → V[- long] / ! in #U`?

## Answer

Findings: [research/index-syllable-position-u-hash.md](../spike/index-syllable-position-u-hash.md). Probes: [research/probes-58/](./research/probes-58/).

- **Partial pass** — faithful ASCA encodings exist for **mechanical** `#U` / `U#` tails using underline structures + env-set exceptions; do **not** ship `// #_%` or naive `U`→`%` on boundary tokens.
- **Recommended rewrites:** `! in #U` → `// :{#_#, #<.._>}:`; `! in U#` → `// :{#_#, <.._>#}:`; `! #U, U#` → `// :{#_#, #<.._>, <.._>#}:`; positive `in #U` / `in U#` → `/ #<.._>` / `/ <.._>#`. Env-set **member order** matters (`{#_#}` before structure).
- **~29 rules** uplift (16 mechanical exceptions + ~13 simple positive env); **~60+** prose/comment/complex tails defer.
- **Parse-only:** strip `in` before `#U`/`U#`; **amend** `group_mappings.csv` comment — `U`→`%` is class letter only, not `#U`/`U#` position markers.
- **Follow-on:** correction-pass ticket for compile rewrite; separate defer tickets for ME / Portuguese prose clusters.

## Source list

- `legacy wayfinder rule-index issue 58-spike-index-syllable-position-u-hash.md`
