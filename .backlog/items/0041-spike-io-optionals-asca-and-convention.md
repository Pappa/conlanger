Type: spike
Status: resolved
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Index I/O optionals vs ASCA structures and convention.
Result: [0041-io-optionals-asca-and-convention.md](../spike/0041-io-optionals-asca-and-convention.md)
Blocked by:

## Question

For Index parentheticals on **input/output** (zero-or-one segments, optional prefixes next to `{…}`, modifier `(ʰ)`/`(ʷ)`, feature-matrix prefixes), what encodings are (1) **ASCA-legal at validate and apply**, (2) **faithful to usual comparative/historical notation**, and (3) **not syllable-scoped by accident**? Confirm or reject the 71 working assumptions.

## Answer

Findings: [research/io-optionals-asca-and-convention.md](../spike/io-optionals-asca-and-convention.md)

**Headline recommendations (resume grill 71):**

- **Q5″:** **(a) Cartesian flat sets** on I/O for zero-or-one / parallel-column shapes. Do not keep Index `(C)a` on I/O (`OptLocError`). Env optionals `(C)_` stay ASCA-native.
- **Q10:** **(a) Never emit `<>` on I/O** in the 48/51 pass — `<>` is syllable-structure matching and fails apply-faithful optional semantics; reserve for env syllable-position ([58](../issues/58-spike-index-syllable-position-u-hash.md)) or manual rows.
- **Q6:** **Family A** (`(h)ə{p,b}`, `e(C){…}`, `(j){u,ʌ}`, `(G)V`) → cartesian then **one flat set** (fix 48 nesting). **Family B** (`k(ʰ){r,j}`) → `{k,kʰ}{r,j}` **adjacent sets** after modifier expansion. Re-scope ticket 51: unfaithful wraps (`{V[-long]}N`, `a{i,j,a}`, `{C,#,V}ʔ`) → cartesian or manual/skip.
- **Q2/Q4/Q9 / inventory trap:** all **confirmed** as in paused grill 71.

## Source list

- `.scratch/rule-index/issues/100-spike-io-optionals-asca-and-convention.md`
