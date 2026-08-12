# Nested sets in Index Diachronica / cleaned corpus

Research for spike [67](../issues/67-spike-nested-sets.md): nested `{…}` shapes in the cleaned rule corpus, overlap with optional outputs (ticket 66), and ASCA 0.10.2 representability.

Primary sources:

- Spike ticket: [67-spike-nested-sets.md](../issues/67-spike-nested-sets.md)
- Grill / optional outputs: [61-grill-optional-outputs.md](../issues/61-grill-optional-outputs.md), [66-implement-optional-outputs-alt-idx.md](../issues/66-implement-optional-outputs-alt-idx.md)
- ASCA **0.10.2**: [doc/doc.md](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md) — sets in I/O and env; [asca-rule-validity.md](./asca-rule-validity.md) §2 / §6
- Prior flatten precedent: [23-correction-pass-labialized-class-letters.md](../issues/23-correction-pass-labialized-class-letters.md) (`L(ʷ)` → `{L_labialized,L}` inside sets)
- Manual rewrites: [60-parse-time-manual-rule-mappings.md](../issues/60-parse-time-manual-rule-mappings.md)
- Corpus YAML: [`data/diachronica/index_diachronica_parsed.yml`](../../../data/diachronica/index_diachronica_parsed.yml)
- Inventory: [asca-rule-inventory.csv](../inventory/asca-rule-inventory.csv) (ASCA 0.10.2, 2026-08-12 baseline)

Local scan script: [`scan_nested_sets.py`](./scan_nested_sets.py) → [`nested-sets-scan.json`](./nested-sets-scan.json). Run: `uv run python .scratch/cleaned-rule-corpus/research/scan_nested_sets.py`.

---

## 1. Executive summary

| Finding | Count |
|---------|------:|
| Inventory rows with `failure_class = nested_brackets` | **46** |
| Corpus rules with brace depth **≥ 2** or unbalanced `{` in `stages` / `env` / `exception` | **40** |
| Of those, max depth **> 1** only (excl. depth-1 unbalanced) | **23** |
| Optional-output candidates skipped by ticket 66 (`"{" in member`) | **0** |

**Recommendation (by material bucket):**

| Bucket | Rules | Path |
|--------|------:|------|
| Nested `{}` in **env** / **exception** only | 14 | **Correction pass** — compile-time flatten (ticket [69](../issues/69-correction-pass-flatten-nested-context-sets.md)) |
| True nested `{}` in **stages** I/O | 9 | **Correction pass** — union-flatten or rule-split where safe (ticket [70](../issues/70-correction-pass-flatten-nested-io-sets.md)) |
| Index **optional-prefix + parallel set** `(h)ə{p,b}`, `e(C){V[…]}` | 11 | **Grill** then correction pass (ticket [71](../issues/71-grill-paren-and-parallel-set-notation.md)) |
| Residual **other** (prose env, chain malformation, deep parens) | 12 | **Defer** — per-rule `manual_mappings` or `status: skipped`; no general compile path |

**Do not** extend ticket 66 optional-output detection to nested members. The gate (`"{" in member` → no `alternatives`) is correct; the corpus simply has **no** flat optional-output rows with nested members today.

**Brassica:** nested sets are an ASCA lexer constraint (`NestedBrackets`); Brassica categories `[a b]` likewise have no nested-category grammar in [Writing Sound Changes](https://github.com/bradrn/brassica/blob/master/docs/Writing-Sound-Changes.md). Any flatten/split strategy should stay applier-neutral in YAML and emit per-backend surface at compile (ADR-0002).

---

## 2. Method

1. Loaded `index_diachronica_parsed.yml` (**9201** corpus rules, `stages` list spine per ADR-0011).
2. For each rule, parsed `stages` into adjacent input/output pairs (same as `expand_chained_corpus_rule`), and scanned `stages`, `env`, `exception`, and `raw` for max `{` depth, unbalanced braces, true nested set members (comma-bounded `{` inside `{…}`), and Index parenthetical-in-set (`segment{variants}` per ticket 48).
3. Cross-matched all **46** `nested_brackets` inventory rows (**45** unique `source` lines) to corpus rows by `source` (`file:line`).
4. Classified each failure into buckets (below); spot-checked ASCA error strings in inventory `description`.
5. Ran optional-output gate from `SoundChangeRule._build_alternatives` (`_is_whole_field_set`, `"{" in member`) over chained compile steps — **zero** flat optional-output rows with nested members.
6. Secondary pass: **31** additional rules use depth-1 `segment{…}` / `(h)ə{…}` shapes that still surface as `nested_brackets` after compile (overlap with ticket 48 residuals).

Historical note: ticket [02](../issues/02-inventory-valid-vs-invalid-rules.md) reported **585** `nested_brackets` at an earlier baseline; correction passes (parentheticals, labialized class letters, chain handling, etc.) reduced the cluster to **46**.

---

## 3. ASCA 0.10.2 constraints

From [asca-rule-validity.md](./asca-rule-validity.md) and ASCA 0.10.2 lexer:

| Pattern | ASCA result | Fix direction |
|---------|-------------|---------------|
| Nested sets `{{a,b}, c}` or `{a,{b,c}}` in I/O | `NestedBrackets` — *Cannot have nested brackets of the same type* | Flatten to one `{…}` level or split into sequential rules |
| Nested `{}` inside env set `_{s,({m,j,w})V}` | `NestedBrackets` | Flatten env members; expand optionals to explicit segments |
| Output-only set without input set (flat) | `LonelySet` | Optional outputs path (ticket 66) — **not** nested |
| Optionals `(…)` in I/O segment position | `OptLocError` / parse errors | Separate from nested sets; ticket [48](../issues/48-correction-pass-parenthetical-segment-notation.md) |
| `(h)ə{p,b}` — optional prefix + set | Often `NestedBrackets` or `syntax_other` depending on shape | Treat as Index parallel-column notation, not true nesting |

ASCA env sets use the same `{}` lexer state as I/O sets; there is no “env-only nesting” exception.

---

### Automated YAML scan buckets (`scan_nested_sets.py`)

Rules with brace depth **≥ 2** or unbalanced `{` in `stages` / `env` / `exception` (**40** rules):

| Bucket | YAML rules | `nested_brackets` inv overlap | Example `source` |
|--------|----------:|------------------------------:|------------------|
| `A_true_nested_io` | 5 | 5 | `index_diachronica_original.html:998` `{ʔ,{h1,h2}}` |
| `B_true_nested_env_exception` | 8 | 8 | `index_diachronica_original.html:6192` `{{h,k,ŋ}n,w,v,l,r}_` |
| `C_parenthetical_in_env_set` | 4 | 4 | `index_diachronica_original.html:1903` `_ə{(C){p,kʷ},m,w}` |
| `C_parenthetical_in_io_set` | 2 | 1 | `index_diachronica_original.html:6193` `{e,w{æ,i}}` |
| `E_unbalanced_malformed` | 21 | 5 | `index_diachronica_original.html:2173` unbalanced chain |

The remaining **~6** inventory `nested_brackets` rows are depth-1 Index shapes (§4.5–4.6) or compile-time nesting not visible at YAML depth ≥ 2.

---

## 4. Bucket inventory

Counts are **nested_brackets inventory rows** (46 total). A rule appears once per bucket.

### 4.1 `io_nested_braces` — true nested `{}` in stages (9)

Brace depth > 1 in the `stages` spine (input/output side of compiled steps).

| source | stages (abbrev.) |
|--------|------------------|
| `index_diachronica_original.html:998` | `{ʔ,{h1,h2}} → ∅` |
| `index_diachronica_original.html:1398` | `{{s,z}(ˤ),ʒ}ʃ → ʃː` |
| `index_diachronica_original.html:2173` | `… → {a,e} {o,u} {a,o,u a {a,o,u} {o,u,i}` (also **unbalanced**) |
| `index_diachronica_original.html:4654` | `m n ŋ t {{ɣ,ʁ} → {k,q}}` (chain-split artifact) |
| `index_diachronica_original.html:5048` | `{{∅,∅}s,s{∅,∅}} → sː` |
| `index_diachronica_original.html:3124` | `{e{V[- low]},eC{V[- low]}} → …` (paired nested output sets) |
| `index_diachronica_original.html:3737` | `{a{o,e},aC{o,e}} → a` |
| `index_diachronica_original.html:2398` | `(h)ə{p,b} → t` — classified here when nested inner `{p,b}` sits inside optional-prefixed parallel column (see also §4.5) |
| `index_diachronica_original.html:2409` | four parallel `(h)ə{…}` columns → `β dʲ ɟ ɡ` |

**ASCA:** all `NestedBrackets` at lex time.

**Recommendation:** ticket [70](../issues/70-correction-pass-flatten-nested-io-sets.md) — union-flatten simple nests (`{ʔ,{h1,h2}}` → `{ʔ,h1,h2}`); split paired nested output sets into sequential rules; `manual_mappings` for `5048` / `1398`; parse/chain fix for `4654` and unbalanced `2173`.

---

### 4.2 `env_nested_braces` — nested `{}` in env only (7)

| source | env (abbrev.) |
|--------|---------------|
| `index_diachronica_original.html:1903` | `_ə{(C){p,kʷ},m,w}` |
| `index_diachronica_original.html:5509` | `_{s,({m,j,w})V}` |
| `index_diachronica_original.html:11518` | `#_{xʲ,w{i,a},qʷa}` |
| `index_diachronica_original.html:11552` | `{{C[-fr,+bk,-hi,-lo],K}ʷ,w}_` |
| `index_diachronica_original.html:1954` | `{CC_C{V,#},CCG_C{V,#}}` (paired env sets on input side) |
| `index_diachronica_original.html:1903` | (see above) |
| `index_diachronica_original.html:1762` | env `W_` — *exception* carries nested shape; counted in §4.3 |

**ASCA:** `NestedBrackets`.

**Recommendation:** ticket [69](../issues/69-correction-pass-flatten-nested-context-sets.md) — flatten one level (ticket 23 precedent); expand `({m,j,w})V` → `{mV,jV,wV}`; paired env sets → two rules or flattened env union where semantics match.

---

### 4.3 `exception_nested_braces` — nested `{}` in exception only (7)

| source | exception (abbrev.) |
|--------|---------------------|
| `index_diachronica_original.html:1762` | `when _{C{C,V:[+long]},#}` |
| `index_diachronica_original.html:5510` | `_{s,({m,j,w})V}` |
| `index_diachronica_original.html:6192` | `{{h,k,ŋ}n,w,v,l,r}_, _{u,o,i}` |
| `index_diachronica_original.html:6225` | `{{h,k,ŋ}n,w,v,l,r}_` |
| `index_diachronica_original.html:6194` | (related cluster) |

**Recommendation:** same correction pass as §4.2 ([69](../issues/69-correction-pass-flatten-nested-context-sets.md)).

---

### 4.4 `context_paren_set` — single-depth `{…}` with `(…)` in env/exception (2)

| source | field |
|--------|-------|
| `index_diachronica_original.html:1954` | `CC(G)_C{V,#}` |
| `index_diachronica_original.html:6194` | `C(C)_{ʀ,s,t,θ}#` |

**ASCA:** `NestedBrackets` (paren + brace combo in env).

**Recommendation:** fold into [69](../issues/69-correction-pass-flatten-nested-context-sets.md) after grill clarifies `(G)` / `(C)` class-letter optionals in env.

---

### 4.5 `paren_set_single_depth` + `optional_prefix_parallel_set` — parallel columns, not true nesting (10)

Index uses **optional segment prefix + parallel set column** notation:

| source | shape |
|--------|-------|
| `index_diachronica_original.html:2398` | `(h)ə{p,b} → t / _l` |
| `index_diachronica_original.html:2409` | four `(h)ə{…}` columns |
| `index_diachronica_original.html:5454` | `{l̩,r̩} → ər(ə(r))` |
| `index_diachronica_original.html:6165` | `{æ,e}ː(w(a))` |
| `index_diachronica_original.html:3124` | `e(C){V[- low]}` |
| `index_diachronica_original.html:3737` | `a(C){o,e}` |
| `index_diachronica_original.html:5900` | `(j){u,ʌ}` |

**ASCA:** rejects; not always brace-depth > 1 but inventory classifies as `nested_brackets`.

**Recommendation:** ticket [71](../issues/71-grill-paren-and-parallel-set-notation.md) — grill semantics, then correction pass (expand to rule fan-out or flattened sets). Distinct from ticket 66 optional outputs (these are **input-side** parallel columns or segment templates).

---

### 4.6 `prose_or_malformed` + `other` — defer / per-rule (12)

| source | issue |
|--------|-------|
| `index_diachronica_original.html:2173` | unbalanced braces in stages |
| `index_diachronica_original.html:4265` | truncated set / chain damage |
| `index_diachronica_original.html:5839` | unbalanced `{` in env + prose exception |
| `index_diachronica_original.html:6380` | truncated `{n̥n,nn̥ tn̥` |
| `index_diachronica_original.html:5803` | prose env `C_ɹ for some C (toward(s)…)` |
| `index_diachronica_original.html:5570` | `#UU(_)U(U(_)U)` |
| `index_diachronica_original.html:2415` | `((h)ə)p d` |
| `index_diachronica_original.html:9306` | `n(V(s)) ʒ(Vʒ)` output |
| `index_diachronica_original.html:11857` | prose tail `oʔ (eventually` + broken set |

**Recommendation:** **explicit defer** — `manual_mappings.csv` where owner intent is known ([60](../issues/60-parse-time-manual-rule-mappings.md)); else `status: skipped` with `raw` preserved. Overlaps existing prose-env tickets [53](../issues/53-correction-pass-prose-env-else.md), [55](../issues/55-correction-pass-prose-env-medial.md). No cluster-wide compile path.

---

## 5. Optional-output overlap (ticket 66)

Ticket 66 builds `alternatives` only when:

- output is a whole-field `{…}` set,
- input is **not** a whole-field set, and
- no member contains `{`.

Scan of all chained compile steps: **0** rules match the first two gates **and** have nested members. The nested-set problem is **orthogonal** to optional outputs in the current corpus.

The one nested output example `{ʔ,{h1,h2}}` is on the **input** side (`998`), not an optional output.

---

## 6. Follow-on tickets

| Ticket | Type | Scope |
|--------|------|-------|
| [69](../issues/69-correction-pass-flatten-nested-context-sets.md) | correction pass | env + exception nested `{}` (~16 rows incl. context_paren_set) |
| [70](../issues/70-correction-pass-flatten-nested-io-sets.md) | correction pass | stages nested `{}` (~9 rows) |
| [71](../issues/71-grill-paren-and-parallel-set-notation.md) | grill | `(h)ə{p,b}`, `e(C){V[…]}`, optional-prefix parallel sets (~10 rows) |

**Deferred without new ticket:** `other` / malformed / prose bucket (12 rows) — per-rule `manual_mappings` or skip per ADR-0010.

---

## 7. References

- [subscript-notation-index-asca-brassica.md](./subscript-notation-index-asca-brassica.md) — Brassica `[a b]` vs ASCA `{a,b}` (no nested category grammar)
- [asca-compile-transform-order.md](./asca-compile-transform-order.md) — compile transform ordering for flatten passes
