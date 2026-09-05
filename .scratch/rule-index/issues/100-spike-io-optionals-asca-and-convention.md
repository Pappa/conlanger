Type: spike
Status: resolved
Blocked by: None

# Spike: Index I/O optionals vs ASCA structures and linguistic convention

Spawned from paused [grill 71](71-grill-paren-and-parallel-set-notation.md) (2026-08-29). That grill also re-opens [ticket 51](51-correction-pass-input-optionals-to-env.md) taxonomy. **Do this spike before answering 71’s remaining questions (Q5″, Q10, Q6).**

## Question

For Index parentheticals on **input/output** (zero-or-one segments, optional prefixes next to `{…}`, modifier `(ʰ)`/`(ʷ)`, feature-matrix prefixes), what encodings are (1) **ASCA-legal at validate and apply**, (2) **faithful to usual comparative/historical notation**, and (3) **not syllable-scoped by accident**? Confirm or reject the 71 working assumptions.

## What to research

1. **ASCA primary docs** (fork/ pallette: 0.10.2 / conlanger `ASCA_BIN`): optionals, sets, syllable structure matching, underline structures, env vs I/O, `#` in I/O, adjacent sets `{k,kʰ}{r,j}`, structure→segment substitution. Reproduce and extend 71 probes; cite doc sections. Prefer `/research` + current ASCA `doc.md`, not ticket 51’s module docstring.
2. **Linguistic convention:** how handbooks and the Index itself use `(C)`, `(h)ə{p,b}`, `k(ʰ)`, `{s,z}(ʔ)` — optional segment vs grouping parens vs “optional feature”. Campbell / Trask / typical SCA practice vs Index-only idiosyncrasy. Do **not** treat Wikipedia as SoT; prefer cited grammars, SCA manuals, Index surrounding commentary.
3. **Corpus examples** from 71: Muong-Khen `(h)ə{p,b}`, Hiw `e(C){V[…]}`, Scots `(j){u,ʌ}`, Amdo `k(ʰ){r,j}`, Indo-Aryan `a{i,j}(a)`, Arapaho `({C,#}V)ʔ`, 51 leftovers `(V[-long])N`, `{s,z}(ʔ)`. For each: Index `raw`, what 48 then 51 emit, what ASCA does on apply, and a recommended encoding **or** “manual/skip”.
4. **Inventory `ok` trap:** which encodings validate+run with **identity** (false green).
5. **Recommend** for grill 71: cartesian I/O vs env-shift vs `<>` vs keep Index `(C)a` vs fork ASCA; what 48 vs 51 should own. File follow-on only if the recommendation is a new ticket; otherwise write “resume 71 with …”.

## Acceptance criteria

- [x] Findings markdown under `.scratch/rule-index/research/`
- [x] ASCA claims cited to `doc.md` (and apply/`trace` where syntax ≠ apply)
- [x] Linguistic-convention section with sources; explicit **confirm / reject / inconclusive** on 71 assumptions (table)
- [x] Per-example encoding table for the 71/51 shapes
- [x] Grill 71 Q5″/Q10/Q6 can be answered from the findings (or marked blocked on a named ASCA/Index ambiguity)

## Out of scope

- Implementing compile/parse rewrites (48, 51, comment-capture Q7)
- Authoring `manual_mappings` / corrections rows except as **illustrative** snippets in findings
- Brassica compiler (mention only if a convention is applier-specific)

## References

- [100](100-spike-io-optionals-asca-and-convention.md) — this spike
- [71](71-grill-paren-and-parallel-set-notation.md) — settled Q2/Q4/Q7/Q9; findings dump; open Q5″/Q10/Q6
- [51](51-correction-pass-input-optionals-to-env.md), [48](48-correction-pass-parenthetical-segment-notation.md)
- [ASCA doc 0.10.2](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md) — Optionals, Sets, Syllable Structure Matching, Underline Structures
- [asca-rule-validity.md](../research/asca-rule-validity.md)
- [nested-sets-inventory.md](../research/nested-sets-inventory.md) §4.5

## Agent Brief

**Category:** spike  
**Summary:** Research ASCA + linguistic convention for Index I/O optionals so grill 71 can be finished; no compile implementation.

**Current behavior:** Ticket 48 cartesian-expands many `(…)` into sets (nests beside `{…}`). Ticket 51 then wraps leftover I/O optionals as singleton/distributive `{…}` so `OptLocError` goes to 0. Inventory `ok` does not imply apply-faithful optional semantics. `<>` was proposed then shown to match **syllables**.

**Desired behavior:** A findings file that a human can use to answer 71 Q5″ (cartesian vs keep `(C)a` vs env-only wrap), Q10 (`<>` on I/O or not), and Q6 (48 Family A vs B).

**Key interfaces:** Index `raw` / `stages`; compile `parenthetical.py` / `input_optionals.py`; `asca validate` + `run`/`trace`.

**Acceptance criteria:** Same as ticket checkboxes. Resolve this spike with `/research`; append **Answer** with link to findings; set `Status: resolved`. Then unblocking 71 is automatic.

**Out of scope:** Shipping transforms; changing 51/48 code; full `create_index` unless needed for one cited row.

## Answer

Findings: [research/io-optionals-asca-and-convention.md](../research/io-optionals-asca-and-convention.md)

**Headline recommendations (resume grill 71):**

- **Q5″:** **(a) Cartesian flat sets** on I/O for zero-or-one / parallel-column shapes. Do not keep Index `(C)a` on I/O (`OptLocError`). Env optionals `(C)_` stay ASCA-native.
- **Q10:** **(a) Never emit `<>` on I/O** in the 48/51 pass — `<>` is syllable-structure matching and fails apply-faithful optional semantics; reserve for env syllable-position ([58](../issues/58-spike-index-syllable-position-u-hash.md)) or manual rows.
- **Q6:** **Family A** (`(h)ə{p,b}`, `e(C){…}`, `(j){u,ʌ}`, `(G)V`) → cartesian then **one flat set** (fix 48 nesting). **Family B** (`k(ʰ){r,j}`) → `{k,kʰ}{r,j}` **adjacent sets** after modifier expansion. Re-scope ticket 51: unfaithful wraps (`{V[-long]}N`, `a{i,j,a}`, `{C,#,V}ʔ`) → cartesian or manual/skip.
- **Q2/Q4/Q9 / inventory trap:** all **confirmed** as in paused grill 71.
