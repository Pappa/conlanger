# ASCA compile transform ordering (planned steps)

Spike for [ticket 38](../issues/38-spike-asca-compile-transform-order.md).  
**Scope:** ASCA compile path only — Brassica ordering is explicitly out of scope.  
**ASCA version:** 0.10.2 (local `asca --version`; probes via `asca run` + `tests/fixtures/asca_probe_words.wsca`).

Primary sources: [`src/conlanger/tools/rules.py`](../../../src/conlanger/tools/rules.py) (`SoundChangeRule._compile_rule_text`), [positional-slots-and-identity-subscripts.md](./positional-slots-and-identity-subscripts.md), [subscript-notation-index-asca-brassica.md](./subscript-notation-index-asca-brassica.md), [ticket 06](../issues/06-resolve-applier-unsupported-abbreviations.md), [ASCA 0.10.2 References](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#references).

---

## 1. Executive summary

**Recommendation:** insert three new compile steps between the existing ellipsis normalizer (current step 2) and `apply_asca_group_mappings` (current step 3). Positional slots and identity subscripts share one transform. Section-local abbreviations must run **before** group mappings — order is safety-critical, not merely stylistic. Meta-notation stays a **late, cluster-driven** pass (after all mechanical normalizers). Length-mark normalization stays after ref expansion and should gain a bare-ref digit rule (`2ː` → `2:[+long]`).

Renumbered pipeline (integer `Order` column ready for [ticket 37](../issues/37-document-sound-change-pipeline.md) / [ticket 39](../issues/39-refactor-sound-change-ruleset.md)):

| Order | Step | Status | Rationale (one line) |
|------:|------|--------|----------------------|
| 0 | `drop_mixed_parallel_null_columns` (per I/O side) | implemented | Index parallel-column `∅`/`*` beside other segments → omit null tokens before join ([ticket 60](../issues/60-correction-pass-parallel-column-null.md)) |
| 0b | `expand_parallel_output_null_branches` (alternatives) | implemented | Index `∅` inside parallel output sets → branch split via `SoundChangeRule.alternatives` ([ticket 81](../issues/81-correction-pass-parallel-output-null.md)) |
| 1 | Join index fields (`input` + `output` + `env` + `exception`) | implemented | Establishes rule string before transforms |
| 2 | `normalize_asca_optional_grouping_ellipsis` | implemented | Index `(C…)` / `(…C)` must become ASCA `(C,0)` / `(..)C` before token transforms |
| 3 | `expand_index_subscript_references` (positional + identity) | planned | Unicode subscripts → ASCA `X=n` / bare `n`; must precede length norm for `N₂ː` → `2:[+long]` |
| 4 | `apply_section_local_abbreviations` | planned | Multi-letter section tokens (e.g. Athabaskan `TS`) must expand before `T`/`S` are split by group mappings |
| 5 | `apply_asca_group_mappings` | implemented | Class-letter CSV expansion; bracket-safe |
| 6 | `normalize_asca_length_marks` | implemented (+ extend) | `ː` → `:[+long]`; extend for bare ref digits after step 3 |
| 7 | `normalize_typographic_apostrophes` | implemented | U+2019 → ejective mark before ejective pass |
| 8 | `normalize_asca_ejective_marks` | implemented | `ʼ` → `:[+cg]` |
| 9 | `_apply_aliases` (`h₁`/`h₂`/`h₃`) | implemented | PIE laryngeals; last to avoid alias letters being re-expanded |
| 10 | `expand_meta_notation` (cluster handlers) | planned / cluster-driven | Retroflex, tone superscripts, repetition — no global policy yet; default slot is last |

**Brassica:** not covered — separate compile pipeline when implemented ([ADR-0001](../../../docs/adr/0001-sound-change-applier-backends.md)).

---

## 2. Implemented baseline (code order)

From `SoundChangeRule._compile_rule_text` ([`rules.py`](../../../src/conlanger/tools/rules.py) lines 361–376):

```text
join fields
  → normalize_asca_optional_grouping_ellipsis
  → apply_asca_group_mappings
  → normalize_asca_length_marks
  → normalize_typographic_apostrophes
  → normalize_asca_ejective_marks
  → _apply_aliases
```

Steps 1–2 and 5–9 above map to this code; steps 3–4 and 10 are new insertions.

---

## 3. Planned transforms — dependency analysis and order

### 3.1 Positional slots + identity subscripts → `expand_index_subscript_references` (Order **3**)

**Single transform.** Both map to ASCA reference syntax ([References](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#references)); token classifiers already separate them in [`series_mappings.py`](../../../src/conlanger/tools/series_mappings.py).

| Dependency | Must be true before this step |
|------------|-------------------------------|
| Ellipsis optionals (step 2) | `(C…)` already `(C,0)` so grouping letters inside optionals are not mistaken for bare class letters |
| Bracket regions | Feature matrices `[…]` preserved (same bracket-split pattern as group mappings) |
| Not yet expanded | Class letters still bare `C`, `V`, `S` so declarations are `C=1`, `V=0` on grouping letters |

| Must run before | Why |
|-----------------|-----|
| **Length marks (6)** | Output `N₂ː` → `N=2` + `2ː`; length pass must convert `2ː` → `2:[+long]` ([probe](#5-prototype-evidence)) |
| **Group mappings (5)** | Defensive: keep `S=1` not `P=1` when positional `S₁` is intended; see [§4.1](#41-positionalidentity-vs-group_mappings) |
| **Ejective / apostrophe (7–8)** | Diacritics on segments between refs (`C₁ˤC₂`) are ref-expansion edge cases, not ordering conflicts |

**Rejected orderings:**

| Alternative | Result |
|-------------|--------|
| After group mappings (5) | Happy-path `C₁`, `S₁` still work — `_GROUPING_FOLLOW` blocks expansion when subscript follows — but `S=1` is clearer than relying on that guard |
| After length marks (6) | **Rejected:** `V₀V₀ → V₀ː` leaves `0ː` on output; current length regex does not rewrite bare ref digits |
| At end (after aliases) | **Rejected:** Unicode `₁`/`₀` remain syntax errors; aliases do not help |

**Implementation notes (follow-on tickets, not blocking order):**

- **Whole-rule pass:** declare refs in input before invoking in output/env ([positional-slots research §6.2](./positional-slots-and-identity-subscripts.md)).
- **Env focus:** rules like `h → ʔ / V₀V₀` compile to `h > ʔ / _ V=0 V=0` — env `_` insertion is a separate compile concern ([probe](#5-prototype-evidence)).
- **Compounds / inter-slot diacritics:** `mV₀`, `C₁ˤC₂` need token-splitting beyond happy-path; `C=1ˤ` is **not** ASCA-valid — emit `C=1` + `1ˤ` or skip ([probe](#5-prototype-evidence)).
- **Feature-attached identity:** `V₀[+nas]` → `V:[+nas]=0` / `0:[+nas]` per ASCA ref+matrix rules (validated in positional-slots research).

### 3.2 Section-local abbreviations → `apply_section_local_abbreviations` (Order **4**)

Per [ticket 06](../issues/06-resolve-applier-unsupported-abbreviations.md) and [`CONTEXT.md`](../../../CONTEXT.md) (**Section-local abbreviation**): multi-letter section tokens (`TŠ`, `TS`, …) resolve from section `abbreviations` tables (populated from hierarchical CSV rows per [ticket 27](../issues/27-implement-parse-time-correspondence-series-expansion.md)), not from global `group_mappings.csv`.

| Dependency | Must be true before |
|------------|---------------------|
| Step 2 (ellipsis) | Optionals normalized |
| Step 3 (refs) | Optional but recommended first so `S₁` positional vs section-local classification is settled on Index-shaped tokens where ambiguous |

| Must run before | Why |
|-----------------|-----|
| **Group mappings (5)** | **Critical.** `TS` as one token must become `{t,s}` before `T` and `S` are expanded separately |

**Rejected ordering — group mappings before section-local:**

```text
TS > ts
  → apply_asca_group_mappings first
  → P:[-voice]P > ts        # WRONG (T→P:[-voice], S→P)
  → section-local never sees intact TS
```

**Accepted ordering — section-local before group mappings:**

```text
TS > ts
  → {t,s} > ts
  → group mappings unchanged (lowercase IPA inside set)
```

`TŠ` is unaffected by group-mapping order (no boundary match on `T` before `Š`), but **`TS` proves order 4 before 5 is mandatory** for all section-local tokens that prefix-match class letters.

**Rejected:** global rows in `group_mappings.csv` for section-only labels ([CONTEXT.md](../../../CONTEXT.md) avoid-list).

### 3.3 Meta-notation → `expand_meta_notation` (Order **10**, cluster-driven)

Per [`CONTEXT.md`](../../../CONTEXT.md) (**Meta-notation**): retroflex `X̣`, tone superscripts `V³`, repetition groups beyond step-2 ellipsis, etc. No global expansion policy yet ([spec.md](../spec.md) story 37).

| Pattern | Current handling | Recommended order when implemented |
|---------|------------------|-----------------------------------|
| `(C…)` / `(…C)` grouping ellipsis | Step 2 (implemented) | Keep at 2 |
| `(…X)` repetition / optional prose | Not implemented | Cluster ticket; default **10** unless probe shows interaction |
| Retroflex underdot `X̣` | Validation cluster | **10** — map to IPA segment per cluster |
| Tone / stress superscripts `V³` | Validation cluster | **10** or parse-time if only editorial |
| Mixed `V₀³` | Ref + meta | Split: step **3** for `V₀`, step **10** for `³` |

**Why last (default slot):** meta handlers are cluster-specific and may emit IPA or feature matrices; running after mechanical normalizers (5–9) avoids double-processing `ː`/`ʼ`/class letters. Re-evaluate per cluster when a handler is added — some may need **3** (before group mappings) if they emit class letters.

**Rejected:** single early pass before step 2 — would fight ellipsis normalization of `(…X)`.

---

## 4. Interaction with implemented steps

### 4.1 Positional/identity vs `group_mappings`

**Decision:** positional + identity ref expansion at **Order 3**, before group mappings at **Order 5**.

**Evidence:**

1. **Regex boundary (defensive):** `apply_asca_group_mappings_to_string` does not expand `C` in `C₁` — subscript is not in the **after** boundary ([`group_mappings.py`](../../../src/conlanger/tools/compile/asca/group_mappings.py)). Probes: `C₁`, `S₁`, `C=1`, `S=1` unchanged by group mappings alone. **Glued clusters** (`SR`, `VOR`, `VːR`) and env literals (`_Ra`) expand when **before** / **after** rules allow — see [sound-change-applier.md](../../../docs/sound-change-applier.md) § Class-letter expansion boundaries.
2. **Semantic clarity:** `S₁ → S=1` preserves the Index class letter on the declaration; `S → P` mapping must not apply to positional slots even if boundary rules change.
3. **No observed case** where refs-after-group differs on validated happy-path rules — but ordering refs first is cost-free and matches [positional-slots research §7 Q6](./positional-slots-and-identity-subscripts.md).

### 4.2 Positional/identity vs `normalize_asca_length_marks`

**Decision:** refs at **3**, length at **6**; extend length pass with `(\d)ː` → `\1:[+long]`.

**Evidence:**

| After ref expansion | After length (+ extension) | ASCA |
|---------------------|----------------------------|------|
| `V=0 0 > 0ː` | `V=0 0 > 0:[+long]` | OK |
| `N=1 N=2 > 2ː` | `N=1 N=2 > 2:[+long]` | OK |
| `C=1 C=2 > 2:[+long]` | unchanged | OK |

Without extension, `0ː` / `2ː` fail validation. Alternative (emit `0:[+long]` inside ref expander) duplicates length logic — prefer one extension in step 6.

### 4.3 Section-local vs `group_mappings`

See [§3.2](#32-section-local-abbreviations--apply_section_local_abbreviations-order-4). **Order 4 before 5 is required** for tokens like `TS`.

### 4.4 Meta-notation vs ellipsis (step 2)

Step 2 already converts Index grouping ellipsis to ASCA zero-or-more / skip. Meta-notation repetition `(…X)` for non-grouping letters is **not** covered — remains Order 10 cluster work. Do not move step 2 after refs.

### 4.5 Aliases (step 9)

`h₁`/`h₂`/`h₃` must remain **last** among mechanical transforms so expanded strings are not re-scanned by group mappings. No planned transform should run after step 9 except cluster-driven meta (step 10) that intentionally targets remaining Index tokens.

---

## 5. Prototype evidence

Probes run in-repo (`uv run python`, 2026-08-07) using `expand_refs` prototype + existing normalizers from `rules.py` + `asca run`.

### 5.1 Ref order variants (happy path)

For `C₁ C₂ > C₂`, `V₀ V₀ > V₀`, `S₁ S₂ > S₂`: all of `refs-before-group`, `refs-after-group`, `length-before-refs`, `refs-at-end` produced identical validated strings on happy-path cases — except length+ref cases below.

### 5.2 Length + refs (requires order 3 before 6)

| Index rule | Ref expansion | + length extension | Valid |
|------------|---------------|-------------------|-------|
| `V₀ V₀ > V₀ː` | `V=0 0 > 0ː` | `V=0 0 > 0:[+long]` | yes |
| `N₁ N₂ > N₂ː` | `N=1 N=2 > 2ː` | `N=1 N=2 > 2:[+long]` | yes |

### 5.3 Env focus (implementation ticket, not order spike)

| Rule | Valid |
|------|-------|
| `h > ʔ / _ V=0 V=0` | yes |
| `h > ʔ / V=0 V=0` (no `_`) | no |

### 5.4 Edge cases (separate implementation tickets)

| Rule | Notes |
|------|-------|
| `C₁ˤ C₂ > C₁ C₂ˤ` | `C=1ˤ` invalid; need split `C=1` + `1ˤ` |
| `V:[+nas]=0 V:[-nas]=0 > 0:[+nas]` | target shape OK |
| `X̣ > ʂ`, `V³ > V` | meta — fail until cluster handler |

### 5.5 Section-local vs group mappings

| Rule | local → group (order 4→5) | group → local (rejected) |
|------|---------------------------|--------------------------|
| `TS > ts` | `{t,s} > ts` | `P:[-voice]P > ts` |
| `T S > ts` | `P:[-voice] P > ts` | same (already split in Index) |
| `TŠ > tʃ` | `{t,ts} > tʃ` | `{t,ts} > tʃ` |

---

## 6. Pipeline table fragment (for docs/sound-change-applier.md)

Copy-ready fragment for [ticket 37](../issues/37-document-sound-change-pipeline.md) when that doc is written:

| Order | Step | Status | Rationale |
|------:|------|--------|-----------|
| 1 | Join index fields | implemented | Build single rule string with ASCA separators |
| 2 | `normalize_asca_optional_grouping_ellipsis` | implemented | Index optional ellipsis → ASCA `(C,0)` / `(..)X` |
| 3 | `expand_index_subscript_references` | planned | Positional `C₁` + identity `V₀` → ASCA refs ([research](./positional-slots-and-identity-subscripts.md)) |
| 4 | `apply_section_local_abbreviations` | planned | Section `abbreviations` table → concrete tokens **before** class-letter expansion ([ticket 06](../issues/06-resolve-applier-unsupported-abbreviations.md)) |
| 5 | `apply_asca_group_mappings` | implemented | `group_mappings.csv` class letters → ASCA groupings |
| 6 | `normalize_asca_length_marks` | implemented | `ː` → `:[+long]`; extend for ref digits `\dː` |
| 7 | `normalize_typographic_apostrophes` | implemented | Typographic apostrophe → `ʼ` |
| 8 | `normalize_asca_ejective_marks` | implemented | `ʼ` → `:[+cg]` |
| 9 | `_apply_aliases` | implemented | `h₁`/`h₂`/`h₃` → IPA |
| 10 | `expand_meta_notation` | planned (cluster) | Retroflex, tone superscripts, etc. ([research](./subscript-notation-index-asca-brassica.md)) |

---

## 7. Open questions → follow-on task tickets

| Question | Suggested ticket type |
|----------|----------------------|
| Implement `expand_index_subscript_references` (happy path + whole-rule binding) | task |
| Extend `normalize_asca_length_marks` for bare ref digit + `ː` | task (small, can merge with refs ticket) |
| Implement `apply_section_local_abbreviations` from section `abbreviations` | task |
| Env `_` focus insertion for rules with env but no `_` | task |
| Compound splits: `mV₀`, `C₁ˤC₂`, `CʔV₀` | task(s) |
| Classify uppercase `S₁` / Formosan labels (positional vs section-local) | spike or cluster |
| Per-cluster meta-notation handlers (retroflex, tone, …) | correction-pass / cluster tickets |
| Cross-field ref numbering when slot appears only in output | task (with apply tests) |

---

## 8. References

| Source | Role |
|--------|------|
| [`src/conlanger/tools/rules.py`](../../../src/conlanger/tools/rules.py) | Implemented compile order |
| [`src/conlanger/tools/series_mappings.py`](../../../src/conlanger/tools/series_mappings.py) | Subscript token classification |
| [`.scratch/.../research/positional-slots-and-identity-subscripts.md`](./positional-slots-and-identity-subscripts.md) | ASCA ref mapping probes |
| [`.scratch/.../research/subscript-notation-index-asca-brassica.md`](./subscript-notation-index-asca-brassica.md) | Four subscript uses; meta-notation |
| [`.scratch/.../issues/06-resolve-applier-unsupported-abbreviations.md`](../issues/06-resolve-applier-unsupported-abbreviations.md) | Section-local policy |
| [`.scratch/.../issues/37-document-sound-change-pipeline.md`](../issues/37-document-sound-change-pipeline.md) | Docs home for this table |
| [`.scratch/.../issues/39-refactor-sound-change-ruleset.md`](../issues/39-refactor-sound-change-ruleset.md) | Refactor blocked until this spike + 37 |
| [ASCA 0.10.2 doc — References](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#references) | `X=n` / bare `n` grammar |
| [ADR-0002 applier-neutral YAML](../../../docs/adr/0002-applier-neutral-yaml-rule-index.md) | Index-shaped YAML; compile-time projection |
| [ADR-0003 validate after compile](../../../docs/adr/0003-validate-after-applier-compile.md) | Validation gate |

---

## 9. Brassica exclusion

This spike assigns **ASCA-only** order integers. Brassica uses different co-reference surface syntax (`@#id`, `@n`, `>` gemination) per [subscript-notation research §5](./subscript-notation-index-asca-brassica.md). A separate Brassica compile ordering spike is required before Brassica compile is implemented.
