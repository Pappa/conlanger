Type: spike
Status: resolved

# Spike: Index syllable position `#U` / `U#` → ASCA

## Question

How should Index Diachronica **syllable-position** tokens (`#U` = word-initial syllable, `U#` = word-final syllable) be represented in ASCA when they appear in **exception** or **environment** fields on **segment-level** rules — e.g. Old Norse `Vː → V[- long] / ! in #U`?

## Why now

Grill session (2026-08-09) on `split_env_exception()` and syllable exceptions. Agreed policy: **leave these rules failing** until a faithful ASCA encoding is identified — do **not** ship a best-effort `// #_%` rewrite.

### Index semantics (grill consensus)

- `#` = word boundary; `U` = syllable class letter (maps to ASCA `%` at compile).
- `in #U` = “in the word's **first syllable**” (any nucleus/onset inside that syllable).
- `! in #U` = **exception** — block the change when the target segment is in the first syllable.
- `in U#` = word-**final** syllable (mirror case; one index rule today).
- Prose `in` is Index editorial glue, not ASCA syntax.

### What does **not** work (empirical, ASCA 0.10.2)

Tested with `asca run` on long-vowel shortening (`V:[+long] > V:[-long]`):

| Candidate | Intended meaning | Result |
| --- | --- | --- |
| `// #_%` | except first syllable | **Wrong** — does not block shortening in first syllable (including monosyllables). |
| `// #_` | except first syllable | **Partial** — blocks only when the long vowel is the **first segment** of the word (`a:`), not when it is inside a consonant-initial first syllable (`ska:.ta:`). |
| `// #%_`, `// #_$` | except first syllable | Same failure modes as above. |
| `/ $ _` (env inversion) | only non-initial syllables | **Wrong** — monosyllables still shorten; polysyllabic behaviour depends on explicit `$` marking. |

Root cause: Index `#U` is **syllable-tier** (“segment is inside the word-initial syllable”); segment rules with `#_%` anchor the focus at the word-onset / syllable junction, not membership in the syllable constituent.

### Corpus slice (current `index_diachronica_parsed.yml`)

| Pattern | Approx. count | Notes |
| --- | ---: | --- |
| `exception: 'in #U'` / `exception: in U#` | **14** | Mechanical `in` + `#U`/`U#`; includes Old Norse `! in #U`. |
| `env:` containing `in #U` / `in U#` | **21** | Often prose env (`in #U before …`, `in U[+open]`); separate from simple exception rewrite. |
| `in #U` anywhere in rule fields | **87** | Superset; includes complex Middle English tails. |

Proto-Norse parallel: `Vː → V[- long] / ! #U, U#` (no prose `in`) — same syllable-position semantics.

### Related parse bug (out of scope for this spike)

`a → u / %u / ! in #U` parses with `env: '$u /'` — trailing `/` before `!` should be stripped in `split_env_exception()`. Mechanical fix; does not resolve ASCA syllable-position encoding.

## Scope of this spike

1. **Primary sources** — ASCA 0.10.2 docs: `%` (whole syllable), `$` (boundary), `#` (word edge), underline structures `⟨…⟩`, syllable-structure matching, exception syntax. Can a segment rule block on syllable membership?
2. **Worked examples** — Old Norse `! in #U`, Proto-Norse `! #U, U#`, Iroquoian `! in U#`; define expected apply/block behaviour on consonant-initial and vowel-initial test words.
3. **Candidate encodings** — e.g. structure + env inversion, multi-rule decompositions, syllable-tier rules, blocking/propagation, explicit `$` requirements; rate each for fidelity and index coverage.
4. **Policy recommendation** — implementable correction pass vs permanent medium-fidelity deferral vs `status:` / comment-only for irreducible prose tails (ME “following U containing /iː/ …”).
5. **Follow-on ticket shape** — correction pass scope, parse-only normalisations (`in` strip, `U`→`%`), and whether `group_mappings.csv` comment on `U`→`%` needs amending.

## Out of scope

- Implementing a correction pass or changing compile output for `#U`/`U#` rules
- Prose-env cluster (`else`, `medial`) — [#53](53-correction-pass-prose-env-else.md), [#55](55-correction-pass-prose-env-medial.md)
- `split_env_exception` trailing-slash fix (file separately if desired)

## Deliverables

- Findings markdown: `.scratch/cleaned-rule-index/research/index-syllable-position-u-hash.md`
- Optional: small table of test words + expected vs actual ASCA outcomes per candidate encoding
- Explicit recommendation: fidelity tier + follow-on implementation ticket(s)

## Acceptance criteria

- [x] ASCA syllable / word-boundary semantics cited from primary sources
- [x] Index `#U` / `U#` semantics documented with grill examples
- [x] At least three candidate ASCA encodings evaluated against test words (including consonant-initial first syllable)
- [x] Recommendation: pass / partial / defer, with expected inventory uplift if pass is viable
- [x] Findings linked from this ticket's **Answer**; no production code change required to resolve

## Answer

Findings: [research/index-syllable-position-u-hash.md](../research/index-syllable-position-u-hash.md). Probes: [research/probes-58/](./research/probes-58/).

- **Partial pass** — faithful ASCA encodings exist for **mechanical** `#U` / `U#` tails using underline structures + env-set exceptions; do **not** ship `// #_%` or naive `U`→`%` on boundary tokens.
- **Recommended rewrites:** `! in #U` → `// :{#_#, #<.._>}:`; `! in U#` → `// :{#_#, <.._>#}:`; `! #U, U#` → `// :{#_#, #<.._>, <.._>#}:`; positive `in #U` / `in U#` → `/ #<.._>` / `/ <.._>#`. Env-set **member order** matters (`{#_#}` before structure).
- **~29 rules** uplift (16 mechanical exceptions + ~13 simple positive env); **~60+** prose/comment/complex tails defer.
- **Parse-only:** strip `in` before `#U`/`U#`; **amend** `group_mappings.csv` comment — `U`→`%` is class letter only, not `#U`/`U#` position markers.
- **Follow-on:** correction-pass ticket for compile rewrite; separate defer tickets for ME / Portuguese prose clusters.

## Blocked by

- None

## Comments

Grill 2026-08-09: maintainer confirmed leave failing; no `// #_%` shortcut.
