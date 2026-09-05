Type: grilling
Status: resolved
Blocked by: None

# Grill: parenthetical + parallel-set notation (`(h)ə{p,b}`, `e(C){V[…]}`)

Spawned from [spike 67](67-spike-nested-sets.md). Findings: [nested-sets-inventory.md](../research/nested-sets-inventory.md) §4.5; [spike 100](../issues/100-spike-io-optionals-asca-and-convention.md) → [research/io-optionals-asca-and-convention.md](../research/io-optionals-asca-and-convention.md).

## Question

Index uses **optional segment prefix + brace parallel column** and **segment-template + set** shapes that ASCA reports as `nested_brackets` but are not always true nested `{}`:

- `(h)ə{p,b} → t / _l` (`index_diachronica_original.html:2398`, `Muong-Khen-həp,b`)
- `e(C){V[- low]} → …` (`index_diachronica_original.html:3124`)
- `(j){u,ʌ}` with env (`index_diachronica_original.html:5900`)

How should these compile? (Original options: rule fan-out / flatten / `manual_mappings`.) Reframed as **I/O zero-or-one** vs **ASCA `<>` syllable structures** vs **ticket 48 cartesian of modifiers**.

## Settled (grill closed 2026-09-02; owner confirmed)

### Core semantics (spike 100 + owner confirm)

| Id | Decision |
|----|----------|
| Q2 | Index I/O `(X)` means **zero-or-one** of X, uniformly. |
| Q4 | `({C,#}V)ʔ` — **`#` in I/O** invalid at ASCA apply. **Do not** auto compile-resolve; human review ([113](113-human-review-io-optional-residuals.md)). |
| Q5″ | **Cartesian flat sets** on I/O for zero-or-one / parallel-column shapes. Not native `(C)a` on bare I/O; not `<>` on I/O for this pass. |
| Q6 | **Optional segment prefix + `{…}`** → cartesian → **one flat set**. **Modifier + `{…}`** → modifier cartesian → **adjacent sets** (`{k,kʰ}{r,j}`). |
| Q9 | `{r,s}(N)k` → `{rk,rNk,sk,sNk}` (zero-or-one `N` per set member; not `{rN,sN}k` or `{r,s,N}k`). |
| Q10 | **Never emit `<>` on I/O** in 48/51 cleanup — reserve for env syllable-position ([98](98-correction-pass-syllable-position-u-hash.md)) or manual rows. |
| Q7 | Indo-Aryan second `(a)` dropped from `stages` is a **parse bug** — [112](112-parse-fix-indo-aryan-optional-stages.md). |

### ASCA optionals (clarified 2026-09-02)

ASCA [Optionals](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#optionals) docs show env examples (`(C)_`); they do not prose-ban I/O. **Validator placement:** bare I/O `(…)` → `OptLocError` on input or `Unknown character '('` on output; optionals inside **input** structures `<…>` validate; optionals inside **output** structures fail at apply. Grill target is **faithful cartesian sets**, not native ASCA optionals on segment strings.

### 51 re-scope (owner 2026-09-02)

| Pattern | Action |
|---------|--------|
| `{s,z}(ʔ)` → `{s,sʔ,z,zʔ}` | **Keep** |
| `{r,s}(N)k` → `{rk,rNk,sk,sNk}` | **Keep** |
| `(G)V` → `{GV,V}` (48) | **Keep** |
| `a{i,j}(a)` | **Replace** → `a{i,j,ia,ja}` (prefer partial structure over flat `{ai,aj,aia,aja}`) |
| `(V[-long])N`, `({C,#}V)ʔ` | **Remove** auto-expand → [113](113-human-review-io-optional-residuals.md) |

### Implementation

| Ticket | Scope |
|--------|-------|
| [111](111-correction-pass-cartesian-io-optionals.md) | Compile cartesian flatten + 51 re-scope; shape-faithful apply probes |
| [112](112-parse-fix-indo-aryan-optional-stages.md) | Parse Indo-Aryan chain optional |
| [113](113-human-review-io-optional-residuals.md) | Human: `(V[-long])N`, `#`-in-I/O templates |

**Withdrawn:** wrap-in-`<>` (apply probes); keep `(C)a` on bare I/O (`OptLocError`).

## Findings (facts)

**Muong-Khen is ticket 48, not 51.** `(h)ə{p,b}` → 48 `{hə{p,b},ə{p,b}}` → `NestedBrackets`. Same family: Hiw `e(C){V[…]}`, Vera’a `a(C){o,e}`, Scots `(j){u,ʌ}` (output-side), Amdo `k(ʰ){r,j}`.

**Tickets 70–110:** parse-time flatten ([70](70-correction-pass-flatten-nested-io-sets.md)) excludes bucket D; field-token IR ([105](105-implement-compile-field-intermediate-representation.md)) defers these shapes to string layer; spike 100 answered research but did not ship compile changes.

**Inventory `ok` trap:** `{V[-long]}N`, `a{i,j,a}`, `<>` wraps can validate without faithful apply.

## Acceptance criteria

- [x] Owner decision on semantics per shape family
- [x] Unblocks mixed I/O rows that 70 deferred to this grill
- [x] Answer recorded; implementation tickets filed

## References

- [51](51-correction-pass-input-optionals-to-env.md), [48](48-correction-pass-parenthetical-segment-notation.md), [100](100-spike-io-optionals-asca-and-convention.md)
- [research/io-optionals-asca-and-convention.md](../research/io-optionals-asca-and-convention.md)
- Compile: `src/conlanger/tools/compile/asca/parenthetical.py`, `input_optionals.py`

## Answer

Grill closed **2026-09-02** after grill-with-docs session (owner confirmed Rounds 1–3).

**Compile target:** string-layer cartesian pass after 48 — Family A flat sets, Family B adjacent sets, no `<>` on I/O. **51:** keep faithful cartesian patterns; replace `a{i,j}(a)` with `a{i,j,ia,ja}`; strip auto-expand for `#`-in-I/O and `(V[-long])N` (human ticket 113).

**Filed:** [111](111-correction-pass-cartesian-io-optionals.md), [112](112-parse-fix-indo-aryan-optional-stages.md), [113](113-human-review-io-optional-residuals.md).

## Comments

> 2026-08-29: Grill-with-docs session paused. Spike 100 resolved — see [findings](../research/io-optionals-asca-and-convention.md). Owner confirm Q5″/Q10/Q6 to close grill.

> 2026-09-02: Grill-with-docs resumed; owner confirmed all frontier questions. ASCA Optionals doc clarified (placement enforced by validator, not prose ban). Grill resolved; tickets 111–113 filed.
