# Parse-time inter-segment whitespace — prototype results

Companion to [Spike: inter-segment whitespace and phoneme boundaries](../issues/44-spike-inter-segment-whitespace.md) and the throwaway demo [prototypes/parse-time-inter-segment-whitespace.html](../prototypes/parse-time-inter-segment-whitespace.html).

Ticket: [Prototype: parse-time inter-segment whitespace feasibility](../issues/46-prototype-parse-time-inter-segment-whitespace.md).

**Purpose of this note:** explain how to read the prototype, dump its fixture outcomes under the main toggle combinations, and record what that implies for later grill / placement decisions. This is **not** a locked ADR.

Prior research (ASCA space-optional; Brassica spaces required; Index spaces mostly parallel parts): [inter-segment-whitespace-phoneme-boundaries.md](./inter-segment-whitespace-phoneme-boundaries.md).

---

## 1. How to interpret the prototype UI

The demo is a **segmentiser sandbox**, not a production parser. Each click re-runs a crude algorithm on the current **Source** string and shows the result in **Current state**.

### 1.1 State panel fields

| Field | Meaning |
|-------|---------|
| **Fixture** | Which canned Index-shaped example is loaded (id + note). |
| **Source** | The raw string being segmented (Index `input` / `output` / `env`-like fragment). |
| **Units** | Atomic pieces the algorithm thinks are separate phonemes/graphemes/syntax atoms (chips). |
| **Spaced candidate** | What a parse-time “insert spaces between units” pass would write into YAML **if** that policy were adopted. |
| **Toggles** | Which of the three algorithm switches are on. |
| **Warnings** | Algorithm self-reports of ambiguity or broken assumptions (red). Take these seriously. |
| **Notes** | Milder commentary (e.g. insert-off). |
| **ASCA reminder** | Static: ASCA 0.10.2 does **not** require inter-segment spaces. |

### 1.2 The three toggles

| Toggle | ON (default) | OFF |
|--------|--------------|-----|
| **Digraph longest-match** | `tʃ`, `dz`, … stay **one** unit (Index affricate table). | Split into base letters (`t`+`ʃ`). |
| **Treat spaces as parallel parts** | Existing ASCII spaces split **parallel condensed parts** (`dz ʃ tʃ` = three side-pieces), not phonemes. | Strip those spaces and segment the glued remainder (naive). |
| **Insert inter-segment spaces** | Join units with spaces in **Spaced candidate**. | Leave Index-shaped / parallel-joined string. |

When parallel mode is ON and there are multiple parts, the demo joins **phoneme** spaces inside each part and uses `·` between parts so you can see both kinds of space. That `·` is a **UI marker only** — not proposed SoT syntax.

### 1.3 What “good” vs “bad” looks like

- **Looks workable:** units match linguistic intent; spaced string is readable; no red warnings (or only expected parallel warnings).
- **Feels wrong:** units split a digraph, matrix, or subscript compound incorrectly; warnings about parallel collision; Kind B bracket spaces destroy `[...]`.
- **Do not confuse:** a spaced candidate that “looks Brassica-like” is **not** evidence ASCA needs spaces. ASCA is space-optional; the question is SoT mutation cost.

---

## 2. Algorithm assumptions (prototype only)

Crude left-to-right scan (see HTML `<script>` module):

1. Optionally split on ASCII space as **parallel parts**.
2. Inside `[...]` keep as one unit (when the bracket is intact).
3. Inside `{...}` recurse on comma members.
4. Longest-match Index digraph table (affricates) when enabled.
5. Else one base character + following diacritics / subscripts.
6. Emit spaced join of units when insert is ON.

**Known prototype bugs / limits** (document as findings, not as production truth):

- `C[+voice]` becomes units `C` + `[+voice]` with a space between — Index/ASCA usually want a **single** modified segment (`C[+voice]` or `C:[+voice]`), not `C` then a bare matrix.
- Kind B `S[+ voice]` under **parallel ON** treats the space inside brackets as a parallel separator → unmatched `[` and garbage units. That is a **hard failure mode** for any naive parse-time spacer.
- Digraph table is a short hand list, not ASCA `cardinals.json`.
- No ASCA CLI validation is run inside the HTML; “ASCA reminder” is documentary only.

---

## 3. Fixture results (reproduced from the prototype logic)

Modes:

- **defaults** — digraphs ON, parallel ON, insert ON  
- **naive** — digraphs ON, parallel OFF, insert ON  
- **digraphs off** — digraphs OFF, parallel ON, insert ON  

| Fixture | Source | Defaults: units → spaced | Contrast to notice |
|---------|--------|--------------------------|--------------------|
| parallel-afro | `dz ʃ tʃ` | `dz` \| `ʃ` \| `tʃ` → `dz · ʃ · tʃ` | **Naive** glues then spaces: same three units as `dz ʃ tʃ` without `·`, but only because digraphs keep affricates; **digraphs off** → `d z · ʃ · t ʃ` (wrong). Parallel warning always when spaces present. |
| affricate-tʃ | `tʃ` | `tʃ` → `tʃ` | Digraphs off → `t ʃ` (ASCA-untied split). |
| affricate-out | `dʒ` | `dʒ` → `dʒ` | Digraphs off → `d ʒ`. |
| labial-k | `kʷ` | `kʷ` → `kʷ` | Diacritic stays glued (good). |
| length | `aː` | `aː` → `aː` | Length stays glued (good for SoT; ASCA still needs compile `:[+long]`). |
| matrix | `C[+voice]` | `C` \| `[+voice]` → `C [+voice]` | **Feels wrong** for SoT: splits modifier from class letter. |
| matrix-space | `S[+ voice]` | **Broken** under defaults: `S` \| `[+` \| `v`… → garbage + unmatched `[` | **Naive** (strip spaces) → `S [+voice]` (still split S from matrix). Kind B + parallel mode is unsafe. |
| slots | `C₁C₂` | `C₁` \| `C₂` → `C₁ C₂` | Subscripts attach (good); spacing separates slots (policy choice). |
| identity | `V₀V₀` | `V₀` \| `V₀` → `V₀ V₀` | Same. |
| compound | `mV₀nV₀` | `m` \| `V₀` \| `n` \| `V₀` → `m V₀ n V₀` | Readable; matches “segment + slot” reading. |
| class-vnc | `VNC` | `V` \| `N` \| `C` → `V N C` | Treats class cluster as three letters (may or may not match Index intent). |
| set | `{ɣ,q}` | `{ɣ, q}` → `{ɣ, q}` | Set kept as one unit. |
| glued-word | `kat` | `k` \| `a` \| `t` → `k a t` | Happy path for “space every phoneme.” |
| ejective-lab | `kʼ kʷʼ` | `kʼ` \| `kʷʼ` → `kʼ · kʷʼ` | Parallel parts again; diacritics glued. |
| env-ish | `V₁[+high]_V₂` | `V₁` \| `[+high]` \| `_` \| `V₂` → `V₁ [+high] _ V₂` | Same class+matrix split issue as `C[+voice]`. |

Machine-readable dump of the same runs: [parse-time-whitespace-prototype-results.csv](./parse-time-whitespace-prototype-results.csv).

---

## 4. Walkthrough takeaways (what the tabs are teaching)

1. **Parallel spaces** — Index `dz ʃ tʃ` is three **parallel** pieces, not six phonemes. Any parse-time spacer must **preserve** that distinction or corrupt condensed rules. The `·` in the UI is the demo admitting two different space meanings collide.
2. **Affricate digraphs** — Without an Index digraph table, `tʃ` becomes `t ʃ` (ASCA’s untied reading). SoT spacing inherits that error permanently if done at parse.
3. **Length & labialisation** — Keeping `kʷ` / `aː` as one unit is feasible in the toy algorithm.
4. **Feature matrices** — Bracket-internal Kind B spaces break parallel-mode splitting; class+matrix without colon splits incorrectly. Parse-time Kind A spacing is **not** free.
5. **Subscript compounds** — `C₁C₂` / `mV₀nV₀` can be unitised, but spacing them is a co-reference / compile-policy choice, not a free readability win.

---

## 5. Feasibility verdict (for later grill — not locked)

**go-with-limits** on the *narrow* question “can we sketch a segmentiser?” — yes, for simple glued IPA and diacritics.

**Strong lean no-go on shipping parse-time SoT spacing as-is**, until at least:

1. Parallel vs phoneme spaces are modeled as **different** structures (not both ASCII space in one string), **or** parallel parts are normalised to commas / separate rules first.
2. Class letter + matrix attachment is fixed (`C[+voice]` ≠ `C` + `[+voice]`).
3. Kind B bracket-internal spaces are handled before any parallel split.
4. Digraph / multigraph inventory is owned and reviewed (not a throwaway list).

This aligns with the prior spike’s **compile-only Brassica spacing** recommendation, but leaves the door open if grill chooses a richer SoT (e.g. structured `segments: […]` IR) instead of mutating Index-shaped strings with ASCII spaces.

---

## 6. Open questions (resolved by [Grill: inter-segment whitespace placement](../issues/45-grill-inter-segment-whitespace-placement.md) 2026-09-06)

1. After seeing parallel `·` collisions, confirm reject ASCII-space SoT mutation — or require a non-space parallel encoding first?
2. Parallel Index spaces → ASCA commas: parse or compile? (Unblocks cleaner Kind A spacing later.)
3. Affricate ties at ASCA compile vs digraph table at parse?
4. Is `C[+voice]` → keep glued vs rewrite to `C:[+voice]` a separate ingest ticket?
5. Kind B `[+ voice]` normalisation schedule?
6. Structured segment arrays in YAML vs string fields forever?

---

## 7. Sources

- Demo: [prototypes/parse-time-inter-segment-whitespace.html](../prototypes/parse-time-inter-segment-whitespace.html)
- Spike findings: [inter-segment-whitespace-phoneme-boundaries.md](./inter-segment-whitespace-phoneme-boundaries.md)
- Examples CSV from spike: [inter-segment-whitespace-examples.csv](./inter-segment-whitespace-examples.csv)
- ADR-0002 applier-neutral index
