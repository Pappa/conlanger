Type: grilling
Status: needs-triage
Blocked by: None

# Grill: parenthetical + parallel-set notation (`(h)ə{p,b}`, `e(C){V[…]}`)

Spawned from [spike 67](67-spike-nested-sets.md). Findings: [nested-sets-inventory.md](../research/nested-sets-inventory.md) §4.5; [spike 100](../issues/100-spike-io-optionals-asca-and-convention.md) → [research/io-optionals-asca-and-convention.md](../research/io-optionals-asca-and-convention.md).

**Paused 2026-08-29** — also re-opened [ticket 51](51-correction-pass-input-optionals-to-env.md). ~~Blocked on [spike 100](100-spike-io-optionals-asca-and-convention.md)~~ **resolved 2026-08-29.** Q5″/Q10/Q6 answered in spike findings; **owner confirm** to close grill and file implementation tickets. Do not ship 48/51 changes until confirmed.

## Question

Index uses **optional segment prefix + brace parallel column** and **segment-template + set** shapes that ASCA reports as `nested_brackets` but are not always true nested `{}`:

- `(h)ə{p,b} → t / _l` (`index_diachronica_original.html:2398`, `Muong-Khen-həp,b`)
- `e(C){V[- low]} → …` (`index_diachronica_original.html:3124`)
- `(j){u,ʌ}` with env (`index_diachronica_original.html:5900`)

How should these compile? (Original options: rule fan-out / flatten / `manual_mappings`.) The 2026-08-29 session reframed this as **I/O zero-or-one** vs **ASCA `<>` syllable structures** vs **ticket 48 cartesian of modifiers**.

## Settled (2026-08-29, session paused — not a closed grill)

Scope was **both** 51 taxonomy and 71 shapes; 51 first.

| Id | Decision |
|----|----------|
| Q2 | Index I/O `(X)` means **zero-or-one** of X, uniformly. |
| Q4 | `({C,#}V)ʔ` is still an optional group, but **`#` in I/O** is invalid ASCA at **run** (`Word Boundaries cannot be in the input or output`; Arapaho `{C,#,V}ʔ` after 51). **Do not** parse/compile-resolve; **corrections.yml or `manual_mappings`**. |
| Q7 | `Central-Middle-Indo-Aryan-ai,ja-au,wa`: peeling the last `(a)` into `comment` is a **parse bug**. `raw` is `a{i,j}(a) a{u,w}(a) → e o`; YAML stages drop the second optional. In scope of this work, not a glossary “comment”. |
| Q9 | Family B Amdo `k(ʰ){r,j}` → **`{k,kʰ}{r,j}`** (two adjacent sets, **no** `<>`). Lone modifiers stay cartesian: `{ɡ,ɡʷ}`, `{k,k:[+cg]}` (member order in the set does not matter). |
| Q5″ | **(a) Cartesian flat sets** on I/O for zero-or-one / parallel-column shapes — per [spike 100](../research/io-optionals-asca-and-convention.md) §1. Not native `(C)a` on I/O; env `(C)_` stays ASCA-native. |
| Q10 | **(a) Never emit `<>` on I/O** in 48/51 cleanup — reserve for env syllable-position ([58](58-spike-index-syllable-position-u-hash.md)) or manual rows. |
| Q6 | **Family A** → cartesian then **one flat set** (fix 48 nesting). **Family B** → modifier cartesian then **adjacent sets** (Q9). Re-scope 51 unfaithful wraps. |

**Withdrawn**

- **Q5 wrap-in-`<>`:** rejected by apply probes (spike 100 §2.2).
- **Keep `(C)a` on I/O:** rejected (`OptLocError`; spike 100 §2.1).

## Findings (facts)

**Muong-Khen is ticket 48, not 51.** `(h)ə{p,b}` → 48 `{hə{p,b},ə{p,b}}`; 51 is a no-op. Inventory: `nested_brackets`, `Cannot have nested brackets of the same type`. Same family: Hiw `e(C){V[…]}`, Vera’a `a(C){o,e}`, Scots `(j){u,ʌ}`, Amdo `k(ʰ){r,j}`.

**51 taxonomy is unfaithful even where it compiles.** Singleton wrap `(V[-long])N` → `{V[-long]}N` makes the V **required**. Ticket table `{r,s}(N)k` → `{r,s,N}k` disagrees with code `{rk,rNk,sk,sNk}`. `a{i,j}(a)` → `a{i,j,a}` is not zero-or-one of trailing `a` (that would be `ai, aj, aia, aja`). `({C,#}V)ʔ` → `{C,#,V}ʔ` is not optional-group.

**ASCA 0.10.2 (`asca validate` / `run`):**

- I/O `(G)V`, `a{i,j}(a)`, `(h)ə{p,b}`, `{s,z}(ʔ)`: `Options can only be used in Environments or Structures`. Env `(G)_` is valid. Inventory `ok` on Indo-Aryan is from **51 rewrite** (and parse dropping the second `(a)`), not native Index syntax.
- `<>` is **syllable structure matching** ([ASCA doc](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#syllable-structure-matching)): matches **one existing syllable**, does not insert `.`. Unmarked words are one syllable.
- `<ka> > <x>`: `ka` → `x`; `b.ka` → `b.x`; `ka.b` → `x.b`; **`bka` / `kab` unchanged**. Wrap **under-generates** inside a larger syllable and **over-generates** across existing `.`.
- `<(h)ə{p,b}>` and `<(h)ə>{p,b}` **validate**; with `/ _l` on `həpl` they **do not apply**. Cartesian `{həp,həb,əp,əb} > t / _l` **does** (`həpl` → `tl`). Structure → bare segment: runtime `Syllables and boundaries cannot be substituted by a segment`.
- `{k,kʰ}{r,j} > tɕ` applies (`kr`/`kʰr`/`kj`/`kʰj` → `tɕ`). `<{k,kʰ}{r,j}> > tɕ` runtime-errors unless the output is also a structure.

**48 vs 51 today** (`expand_index_parenthetical_notation` then `expand_input_optionals_to_structures`): Family A prefixes `(h)`, `(C)`, `(j)`, `(G)` cartesian-expand and **nest** when a `{…}` follows. Family B `ɡ(ʷ)` cartesian is ASCA-legal; wrap `ɡ<(ʷ)>` is not. 51 leftovers are feature-matrix prefixes, set-suffix optionals, `{p,t,k}({p,t,k})n`, `({C,#}V)ʔ`.

**Inventory `ok` is a weak fidelity signal:** validate+run can succeed on **identity** (wrap that never matches).

## Open (owner confirm to close)

- [ ] Owner confirms spike 100 recommendations (Q5″/Q10/Q6) — then mark grill **resolved** and file implementation ticket(s) for 48/51 re-scope (+ parse Q7).
- [ ] Implementation ticket(s) filed or defer written (acceptance criteria below).

## Original acceptance criteria

- [ ] Owner decision on semantics per shape family
- [ ] Unblocks mixed I/O rows that 70 deferred to this grill (70 itself is resolved)
- [ ] Answer recorded; implementation ticket filed or defer written

## Facts (original)

- Ticket [66](66-implement-optional-outputs-alt-idx.md) optional outputs apply only to **unpaired whole-field output sets** — not these input-side shapes.
- Ticket [48](48-correction-pass-parenthetical-segment-notation.md) handled many I/O parens; residual parallel-column shapes remain.
- Ticket [51](51-correction-pass-input-optionals-to-env.md) — cluster 18→0 via unfaithful `{…}` wraps; **re-open implied**, not implemented.
- ASCA 0.10.2: no nested `{}`; optionals `(…)` not allowed in I/O segments; `<>` = syllable match.

## References

- [51](51-correction-pass-input-optionals-to-env.md), [48](48-correction-pass-parenthetical-segment-notation.md), [100](100-spike-io-optionals-asca-and-convention.md)
- [research/io-optionals-asca-and-convention.md](../research/io-optionals-asca-and-convention.md)
- [ASCA Optionals](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#optionals), [Syllable Structure Matching](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#syllable-structure-matching)
- Compile: `src/conlanger/tools/compile/asca/parenthetical.py`, `input_optionals.py`

## Comments

> 2026-08-29: Grill-with-docs session paused. Spike 100 resolved — see [findings](../research/io-optionals-asca-and-convention.md). Owner confirm Q5″/Q10/Q6 to close grill.
