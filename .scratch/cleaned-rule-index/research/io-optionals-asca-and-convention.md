# Index I/O optionals vs ASCA structures and linguistic convention

Research for spike [100](../issues/100-spike-io-optionals-asca-and-convention.md): ASCA legality and apply fidelity for Index parentheticals on **input/output**, linguistic convention for optional-segment notation, and concrete answers for grill [71](../issues/71-grill-paren-and-parallel-set-notation.md) Q5″/Q10/Q6.

Primary sources:

- Spike ticket: [100-spike-io-optionals-asca-and-convention.md](../issues/100-spike-io-optionals-asca-and-convention.md)
- Paused grill: [71-grill-paren-and-parallel-set-notation.md](../issues/71-grill-paren-and-parallel-set-notation.md)
- Tickets [48](../issues/48-correction-pass-parenthetical-segment-notation.md), [51](../issues/51-correction-pass-input-optionals-to-env.md)
- ASCA **0.10.2** (project `bin/bin/asca`): [doc/doc.md](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md) — [Optionals](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#optionals), [Sets](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#sets), [Syllable Structure Matching](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#syllable-structure-matching), [Underline Structures](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#underline-structures), [Special Characters](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#special-characters)
- Prior validity map: [asca-rule-validity.md](./asca-rule-validity.md)
- Nested-set bucket context: [nested-sets-inventory.md](./nested-sets-inventory.md) §4.5
- HTML SoT: [`data/diachronica/index_diachronica_original.html`](../../../data/diachronica/index_diachronica_original.html)
- Compile: `src/conlanger/tools/compile/asca/parenthetical.py` (ticket 48), `input_optionals.py` (ticket 51)

Local probes: `asca 0.10.2` at `bin/bin/asca`; scratch probes under [`.scratch/cleaned-rule-index/research/_spike100/`](./_spike100/).

---

## 1. Executive summary

**Recommendation for grill 71 (resume with these):**

| Question | Answer |
|----------|--------|
| **Q5″** — I/O compile target after `<>` wrap failed apply | **(a) Cartesian flat sets** for I/O zero-or-one and parallel-column shapes. Do **not** keep native Index `(C)a` on I/O (`OptLocError`). Do **not** use `<>` on I/O for optional segments. Env-only optionals `(C)_` stay as ASCA env/structure syntax. |
| **Q10** — When may compile emit `<>`? | **(a) Never on I/O** in the 48/51 cleanup pass. Reserve `<>` for env/exception syllable-position work ([ticket 58](issues/58-spike-index-syllable-position-u-hash.md)) or explicit manual rows where Index already uses syllable talk (`U`, `%`, `.`). |
| **Q6** — 48 policy Family A vs B | **Family A** (optional **prefix** + `{…}` column: `(h)ə{p,b}`, `e(C){V[…]}`, `(j){u,ʌ}`, `(G)V`): **cartesian product → one flat `{…}`** (no nesting). **Family B** (modifier + column: `k(ʰ){r,j}`): ticket 48 modifier expansion `{k,kʰ}` then **adjacent sets** `{k,kʰ}{r,j}` (Q9); do **not** nest `{k{r,j},kʰ{r,j}}`. **51 leftovers** (`(V[-long])N`, `({C,#}V)ʔ`, `a{i,j}(a)`): see §5 — several need cartesian or **manual/skip**, not singleton `{…}` wrap. |

**ASCA facts (0.10.2, validated locally):**

- I/O `(…)` → `Syntax Error: Options can only be used in Environments or Structures` (`OptLocError`).
- `<…>` is **syllable-structure matching**, not “optional segment string” ([Syllable Structure Matching](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#syllable-structure-matching)). `<ka> > x` applies to `ka` as one syllable but **not** `b.ka`; `bka`/`kab` unchanged — under- and over-generation vs segment optionality.
- Structure input → bare segment output → `Runtime Error: Syllables and boundaries cannot be substituted by a segment`.
- Adjacent input sets concatenate: `{k,kʰ}{r,j} > tɕ` applies (`kr` → `tɕ`); `<{k,kʰ}{r,j}> > tɕ` runtime-errors on apply.
- `#` in I/O → syntax error at validate; `{C,#,V}ʔ` (ticket 51 rewrite) → `Runtime Error: Word Boundaries cannot be in the input or output` at apply.

**Linguistic convention:** Index `(X)` on I/O aligns with handbook **zero-or-one segment** parens (Crowley/Trask/Campbell tradition), distinct from modifier parens `k(ʰ)` and from ASCA env optionals `(C)_`.

**Inventory `ok` trap:** Several 51 rewrites validate + `run` on identity or wrong probes (Indo-Aryan `a{i,j,a}`, `{V[-long]}N`, `{rk,rNk,sk,sNk}` with weak env probes). Treat inventory `ok` as syntax-only unless apply probes are shape-faithful.

---

## 2. ASCA semantics (cited + probed)

### 2.1 Optionals `(…)` — env and structures only

From [Optionals](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#optionals):

- `(C)_` = zero or one consonant before focus (equivalent to `(C,0:1)_`).
- `(C,0)_` / `(C,:)_` = zero or more consonants (lazy repetition).
- `([])_` = zero or one of any segment.

**Not allowed in I/O segment strings** ([asca-rule-validity.md](./asca-rule-validity.md) §2):

| Probe | Result |
|-------|--------|
| `(C)a` [input] | `OptLocError` |
| `({C,#}V)ʔ` [input] | `OptLocError` |
| `(C)_` [context] | **valid** |
| `(C)a > x` (full rule) | `OptLocError` on input |

Index I/O `(h)`, `(C)`, `(j)`, trailing `(a)`, `{s,z}(ʔ)` all hit the same wall at validate unless rewritten.

### 2.2 Sets — flat choices; adjacent sets concatenate

From [Sets](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#sets):

- `{p,t,k}` = choice among members; paired I/O sets zip by position.
- Sets can contain **sequences** (`{nd, N<C..>, 1$s}`) but **not nested `{}`** (`NestedBrackets`).
- When two set tokens are adjacent in the input, they denote **concatenation** of choices (one pass): `{k,kʰ}{r,j}` matches `kr`, `kʰr`, `kj`, `kʰj`.

Ticket 48’s prefix cartesian **nesting** `{hə{p,b},ə{p,b}}` is therefore ASCA-illegal (`NestedBrackets`) even though it mirrors Index structure.

### 2.3 `<>` — syllable structure matching, not I/O optionals

From [Syllable Structure Matching](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#syllable-structure-matching):

> Structures are defined between angle brackets … They can contain segments, matrices, references, sets, optionals, or ellipses.

Structures match **one existing syllable** in the word; they do not insert syllable boundaries. Unmarked words are one syllable ([The Basics](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#the-basics)).

| Word | Rule `<ka> > x` | Outcome |
|------|-----------------|---------|
| `ka` | apply | runtime error (structure → segment) |
| `b.ka` | syllable `ka` in second syllable | same runtime error |
| `bka` | no syllable equal to `ka` | **unchanged** |
| `kab` | no match | **unchanged** |
| `ka.b` | first syllable `ka` | runtime error |

`<(h)ə{p,b}> > t / _l` on `həpl`: **validates** but **does not apply** (no syllable match) — inventory false green if only syntax is checked.

[Underline Structures](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#underline-structures) place `_` **inside** structures for env focus — appropriate for `#U`/`U#` ([index-syllable-position-u-hash.md](./index-syllable-position-u-hash.md)), not for Muong-Khen-style segment optionals.

### 2.4 `#`, `$`, `%` in I/O

From [Special Characters](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#special-characters):

- `#` — word boundary; **env only**, at most once per periphery.
- `$` — syllable boundary (repair / metathesis).
- `%` — whole syllable.

| Probe | Result |
|-------|--------|
| `#` [input] | `Word boundaries are not allowed in the input or output` |
| `{C,#,V}ʔ > x / _C` | validate ok; apply `aʔ` → `Runtime Error: Word Boundaries cannot be in the input or output` |

### 2.5 Structure → segment substitution

Any rule with structure in input and a bare segment (or non-structure) output fails at apply:

- `<ka> > x` → `Syllables and boundaries cannot be substituted by a segment`
- `<{k,kʰ}{r,j}> > tɕ` → same on `kr`

Cartesian flat sets avoid this class of error.

---

## 3. Linguistic convention (handbooks + Index)

### 3.1 Three parenthesis roles in Index

| Role | Index examples | Handbook / Index intent | ASCA target |
|------|----------------|-------------------------|-------------|
| **Zero-or-one segment** (I/O) | `(h)ə{p,b}`, `e(C){V[…]}`, `(j){u,ʌ}`, `a{i,j}(a)`, `(G)V` | Optional presence of a segment in the **segment string** | Flat cartesian `{…}` (§5) |
| **Optional modifier** (on segment) | `k(ʰ)`, `ɡ(ʷ)`, `tɕ(ʰ)` (Amdo output) | Diacritic / secondary articulation may be present | Ticket 48: `{k,kʰ}`, `{ɡ,ɡʷ}` |
| **Env optional / grouping** | `(C)_`, `({C,#}V)ʔ` (intended optional C or template) | Crowley/Trask env collapse; Index template groups | Env: ASCA `(C)_`; I/O `#` templates → **manual** |

**Distinction from braces:** `{u,ʌ}` is parallel **either/or** (Crowley “curly brackets”); `(j)` before `{u,ʌ}` is **optional prefix** — combined semantics = `{ju,jʌ,u,ʌ}`, not nested braces.

### 3.2 Handbook sources (not Wikipedia)

| Source | Claim |
|--------|-------|
| **Crowley** (*Historical Linguistics*, Ch. 3 — Enggano example via course slides): `V > [+nas] / V (C) ___ [+nas]` — parens = intervening C may be absent. |
| **Trask** (1996), cited in Index §10.3 (Hiw): same rule-notation ecosystem as Index; Index `(C)` in `e(C){V[…]}` parallels handbook env optionals but on the **segment side**. |
| **Campbell** tradition / SPE-style handouts ([Zuraw rule notation](https://linguistics.ucla.edu/people/zuraw/200A_2004/0203RuleNotation.pdf); [Smith 531](https://brianwilliamsmith.github.io/teaching/531_2.html)): `(X)` = “one or zero X”; `{X,Y}` = either X or Y; `(X)*` = zero or more. |
| **Index HTML commentary** | Muong `(h)ə{p,b}` (line 2398) in presyllable-heavy Viet-Muong section — `(h)` = optional presyllable / prefix; Hiw line 3124 uses `(C)` as optional consonant in template `e(C){V[- low]}`; Lemerig prose (line 3143): “intervening consonants **sometimes optional**”. |

**Confirm:** Index I/O `(X)` is intended as **zero-or-one segment** (grill Q2), not ASCA syllable structures and not grouping-only notation.

**Reject:** Treating ticket 51’s `{V[-long]}N` wrap as faithful optional-prefix semantics — it makes the matrix **required** (`{V[-long]}` is a mandatory set member).

**Inconclusive:** Whether Indo-Aryan `a{i,j}(a)` allows bare `a` without glide (set empty branch) — cartesian should include `a` only if Index author intended it; `{ai,aj,aia,aja}` is the zero-or-one-suffix reading.

### 3.3 Modifier parens vs segment optionals

`k(ʰ){r,j}` (Amdo, line 12290) is **Family B**: optional aspiration on `k`, then parallel `{r,j}`. Handbook-wise this is modifier optionality (like `ɡ(ʷ)`), not `(C)` env notation. Ticket 48 already expands `k(ʰ)` → `{k,kʰ}`; remaining work is **adjacent set** `{k,kʰ}{r,j}`, not nested `{k{r,j},kʰ{r,j}}`.

---

## 4. Grill 71 assumptions (confirm / reject / inconclusive)

| Id | Assumption | Verdict | Evidence |
|----|------------|---------|----------|
| **Q2** | Index I/O `(X)` = zero-or-one segment | **Confirm** | §3; ASCA needs flat cartesian because `(X)` is env-only in ASCA |
| **Q4** | `#` in I/O → manual only | **Confirm** | §2.4; Arapaho inventory `runtime_other` on 51 rewrite |
| **Q5″** | Cartesian flat sets for I/O optionals in segment strings | **Confirm (a)** | §2.1–2.3; Muong `{həp,həb,əp,əb}` applies where `<(h)ə{p,b}>` does not |
| **Q9** | `{k,kʰ}{r,j}` adjacent sets | **Confirm** | §2.2; `kr` → `tɕ` on apply |
| **Q10** | No `<>` on I/O for 48/51 cleanup | **Confirm (a)** | §2.3; validates but wrong syllable scope + structure→segment errors |
| **Q6** | 48 Family A cartesian vs Family B | **Confirm split** | Family A → flat cartesian; Family B → modifier cartesian + adjacent sets (§6) |
| **Inventory `ok` trap** | `ok` ≠ apply-faithful | **Confirm** | Indo-Aryan `a{i,j,a}` inventory ok; `{V[-long]}N` validates, `aN` unchanged; `<>` wraps validate, no apply |

---

## 5. Corpus examples (71 / 51 shapes)

Compile functions (current code):

```python
from conlanger.tools.compile.asca.parenthetical import expand_index_parenthetical_notation  # 48
from conlanger.tools.compile.asca.input_optionals import expand_input_optionals_to_structures  # 51
```

ASCA: `bin/bin/asca` 0.10.2 — `validate -s` / `trace`.

| Example | Index `raw` | 48 output | 51 output | ASCA validate (native / 48 / 51) | ASCA apply (best encoding) | Recommended encoding | Manual? |
|---------|-------------|-----------|-----------|----------------------------------|----------------------------|----------------------|---------|
| **Muong-Khen** | `(h)ə{p,b}` | `{hə{p,b},ə{p,b}}` | same | OptLoc / NestedBrackets / NestedBrackets | `{həp,həb,əp,əb} > t / _l`: `həpl` → `tl` | `{həp,həb,əp,əb}` | no |
| **Hiw** | `e(C){V[- low]}` | `{e{V[- low]},eC{V[- low]}}` | same | OptLoc / NestedBrackets / NestedBrackets | `{eV[- low],eCV[- low]}` validates; apply needs class expansion | `{eV[- low],eCV[- low]}` (after `V` mapping) | no |
| **Scots** | `(j){u,ʌ}` | `{j{u,ʌ},{u,ʌ}}` | same | OptLoc / NestedBrackets / NestedBrackets | `{ju,jʌ,u,ʌ}` validates (output IPA `øː` needs compile norm) | `{ju,jʌ,u,ʌ}` | no |
| **Amdo** | `k(ʰ){r,j}` | `{k{r,j},kʰ{r,j}}` | same | parse error native / NestedBrackets / NestedBrackets | `{k,kʰ}{r,j} > tɕ`: `kr` → `tɕ` | `{k,kʰ}{r,j}` (+ paired output set for `ɡ{r,j}`) | no |
| **Indo-Aryan** | `a{i,j}(a)` | `a{i,j}(a)` | `a{i,j,a}` | OptLoc / OptLoc / **ok** | `{ai,aj,aia,aja} > e`: `ai` → `e`; 51: `aja` → `ea` (wrong) | `{ai,aj,aia,aja}` | no |
| **Arapaho** | `({C,#}V)ʔ` | same | `{C,#,V}ʔ` | OptLoc / OptLoc / ok* | 51: runtime `#` in I/O | — | **yes** (`manual_mappings` / corrections) |
| **V-long-N** | `(V[-long])N` | same | `{V[-long]}N` | OptLoc / OptLoc / **ok** | 51: `aN` unchanged (false green) | split rules or env-only optional; not `{V[-long]}N` | partial |
| **Athabaskan** | `{s,z}(ʔ)` | same | `{s,sʔ,z,zʔ}` | OptLoc / OptLoc / **ok** | `{s,sʔ,z,zʔ} > s / _#` validates; trace needs wordlist `#` | `{s,sʔ,z,zʔ}` | no |
| **GV** | `(G)V` | `{GV,V}` | same | OptLoc / **ok** / **ok** | `wa` → `x` | `{GV,V}` (48 already correct) | no |
| **Naxi** | `{r,s}(N)k` | same | `{rk,rNk,sk,sNk}` | OptLoc / OptLoc / **ok** | validates; apply needs `N` class + `_V` probe | `{rk,rNk,sk,sNk}` (51 code; not ticket table `{r,s,N}k`) | no |

\*Arapaho full rule also fails output `ø`/`ː` tokens in inventory pipeline; runtime failure is definitive for `#`.

### 5.1 51 leftovers called out in ticket

| Shape | 51 behaviour | Faithful? | Action |
|-------|--------------|-----------|--------|
| `(V[-long])N` | `{V[-long]}N` | **No** — required matrix prefix | manual / rule-split |
| `{s,z}(ʔ)` | `{s,sʔ,z,zʔ}` | **Yes** | keep cartesian (51) |
| `(G)V` | handled by 48 `{GV,V}` | **Yes** | 48 only |
| `{r,s}(N)k` | `{rk,rNk,sk,sNk}` | **Yes** (code) | keep; fix ticket doc |
| `a{i,j}(a)` | `a{i,j,a}` | **No** | cartesian `{ai,aj,aia,aja}` |
| `({C,#}V)ʔ` | `{C,#,V}ʔ` | **No** | manual/skip |

---

## 6. Recommendations for grill 71 (Q5″, Q10, Q6)

### Q5″ — I/O compile target

**Ship (a): cartesian flat sets** for all I/O zero-or-one and parallel-column shapes in §5.

- Implement as a **new compile pass** (or extend 48 with a “flatten cartesian” step after prefix expansion) that:
  1. Detects Family A `(X)…{…}` / `(X){…}` / `literal{…}(Y)` patterns.
  2. Emits **one flat** `{member1,member2,…}` with no nested `{}`.
  3. For Family B after modifier expansion, emits **adjacent** sets when two independent columns multiply (`{k,kʰ}{r,j}`).
- **Do not** emit native Index `(C)a` on I/O.
- **Do not** rely on ticket 51 singleton/distributive `{…}` wraps for optional semantics.
- **Env-only:** keep `(C)_`, `(C,0)_`, underline structures for syllable position — separate from I/O pass.

### Q10 — `<>` emission

**Ship (a): never on I/O** for 48/51 cleanup.

- `<>` remains valid ASCA for **env/exception** syllable templates ([98](issues/98-correction-pass-syllable-position-u-hash.md)).
- Per-rule `manual_mappings` if a future ticket needs syllable-scoped I/O (none identified in §5 corpus).

### Q6 — 48 Family A vs B

| Family | Index pattern | 48 today | Target |
|--------|---------------|----------|--------|
| **A** | Optional **segment** prefix + `{…}`: `(h)ə{p,b}`, `e(C){…}`, `(j){u,ʌ}`, `(G)V` | Prefix cartesian then **nest** beside `{…}` → `NestedBrackets` | Prefix cartesian then **flatten** to one set (§5 table) |
| **B** | Modifier optional + `{…}`: `k(ʰ){r,j}` | `{k{r,j},kʰ{r,j}}` nested | `{k,kʰ}{r,j}` adjacent (Q9) |
| **B′** | Lone modifier: `ɡ(ʷ)` | `{ɡ,ɡʷ}` | unchanged (48) |

**Ownership:** extend **48** (or successor pass immediately after 48) for Family A flatten + Family B adjacent-set emission; **re-scope 51** to env/structure-only shapes or retire unfaithful I/O wraps.

---

## 7. Inventory `ok` identity trap

Rules that reach **ok** without faithful optional behaviour:

| Rule id | Compiled shape | Why misleading |
|---------|----------------|----------------|
| `Central-Middle-Indo-Aryan-ai,ja-au,wa` | `a{i,j,a} > e` | Validates; `aja` → `ea`; omits `aia`; parse drops second `(a)` (Q7) |
| `Arapaho-V-longN` / Gros Ventre | `{V[-long]}N > * / _#` | Optional prefix became **required** set member |
| `Navajo-s,zʔ-…` (51 cartesian) | `{s,sʔ,z,zʔ} > s / _#` | Validates; trace on bare `sʔ` unchanged without proper word-boundary wordlist |
| Any `<>` I/O wrap | e.g. `<(h)ə{p,b}>` | Validates; no apply on segment probes |

**Policy:** require shape-specific apply probes in grill sign-off; do not use inventory `ok` alone to accept 51 taxonomy.

---

## 8. Follow-on

- **Resume grill 71** with Q5″/Q10/Q6 answered above; owner confirms then file implementation ticket(s) for cartesian flatten (48 successor) and 51 re-scope.
- **No new ticket** for Arapaho / `#`-in-I/O — already `manual_mappings` / corrections path (Q4).
- **Parse fix** for Indo-Aryan second `(a)` (Q7) remains separate from compile cartesian.

---

## 9. References

| Topic | Location |
|-------|----------|
| ASCA optionals | [doc.md § Optionals](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#optionals) |
| ASCA sets | [doc.md § Sets](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#sets) |
| Syllable structures | [doc.md § Syllable Structure Matching](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#syllable-structure-matching) |
| Word boundaries | [doc.md § Special Characters](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#special-characters) |
| Validity checklist | [asca-rule-validity.md](./asca-rule-validity.md) |
| Muong-Khen HTML | `index_diachronica_original.html:2398` |
| Hiw HTML | `index_diachronica_original.html:3124` |
| Amdo HTML | `index_diachronica_original.html:12290` |
| Crowley paren notation | Enggano `V (C) ___ [+nas]` ([slideserve summary](https://www.slideserve.com/kirti/commentary-on-crowley)) |
| SPE / handbook parens | [Zuraw 200A rule notation](https://linguistics.ucla.edu/people/zuraw/200A_2004/0203RuleNotation.pdf); [Smith 531](https://brianwilliamsmith.github.io/teaching/531_2.html) |
