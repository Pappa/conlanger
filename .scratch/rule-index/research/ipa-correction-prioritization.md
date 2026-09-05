# IPA-shape correction-pass prioritisation (spike 114)

Research for spike [114](../issues/114-spike-ipa-correction-prioritization.md) (2026-09-05).

**Primary sources:**

- Inventory regen: `uv run create_index && uv run validate_rules` → [`rule-inventory-summary.md`](../inventory/rule-inventory-summary.md)
- Scan: [`scan_ipa_correction_classes.py`](./scan_ipa_correction_classes.py) → [`ipa-correction-classes.csv`](./ipa-correction-classes.csv), [`ipa-correction-buckets.csv`](./ipa-correction-buckets.csv)
- Auxiliary CSVs: [`expected_ipa_errors.csv`](../inventory/expected_ipa_errors.csv), [`invalid_ipa_errors.csv`](../inventory/invalid_ipa_errors.csv), [`expected_range_dots_errors.csv`](../inventory/expected_range_dots_errors.csv), [`field-isolation-error.csv`](../inventory/field-isolation-error.csv)
- Prior spikes: [106 near-miss queue](./near-miss-correction-prioritization.md) (superseded), [64 syntax_other](./syntax-other-near-miss-sections.md) (Khoisan defer)

---

## 1. Executive summary

Re-ran the full inventory on 2026-09-05. **Headline metrics match the spike-114 spawn baseline** — no drift on ok/fail/skipped or sections-all-OK. Near-miss failing-rule count is **326** (up from **322** cited at spawn; +4 from post-110 residual churn).

**Top four correction-pass levers** (by global mono-class sections-completed-if-cleared):

| Rank | Bucket | Sections complete | Rules | Filed ticket |
|-----:|--------|------------------:|------:|--------------|
| 1 | `expected_ipa` / editorial slash + prose residue | **8** | 30 | [115](../issues/115-correction-pass-editorial-slash-prose-residue.md) |
| 2 | `expected_ipa` / parenthetical optional modifiers | **8** | 21 | [116](../issues/116-correction-pass-paren-optional-modifiers.md) |
| 3 | `invalid_ipa` / prenasal `ⁿ` prefix | **6** | 11 | [117](../issues/117-correction-pass-prenasal-prefix.md) |
| 4 | `expected_range_dots` / European dot-affricate clusters | **3** | 35 | [118](../issues/118-correction-pass-dot-affricate-notation.md) |

**Explicit defer / manual / blocked:**

- **Khoisan clicks** (`ǃ`, `ǀ`, `ǁ`, `ǂ`, `!` notation) — **47** rules in §20.x — `manual_mappings` / `status: skipped` per [spike 64](./syntax-other-near-miss-sections.md) (unchanged)
- **`expected_ipa` / `prose_double_slash_env`** — **2** mono-class sections (§24.1.1, §24.1.4); env-paren `//` residue distinct from [108](../issues/108-correction-pass-double-slash-env.md) (`expected_underscore`); follow-on after 115
- **`expected_ipa` / `paren_optional_io`** — **2** mono-class sections; overlaps [48](../issues/48-correction-pass-parenthetical-segment-notation.md) / [111](../issues/111-correction-pass-cartesian-io-optionals.md) residuals — triage in 116 or manual
- **Heavy-section skips** (Salish 35.1.x, 29.2, 46.13) — seeded 2026-09-05; no IPA-class levers inside skipped sections today
- **Yup'ik `V.V` geminate dot ranges** — **0** `expected_range_dots` rows in §24.x on current inventory; Yup'ik failures are `prose_double_slash_env` + `prenasal_prefix` instead

**Estimated ceiling** if passes 115–118 land without regression: **+25** sections-all-OK (sum of mono-class subcluster impacts; some overlap possible across editorial vs modifier shapes).

---

## 2. Baseline drift

| Metric | Issue 114 spawn | 2026-09-05 regen | Drift |
|--------|----------------:|-----------------:|------:|
| Rules OK / fail / skipped | 8321 / 734 / 772 | **8321 / 734 / 772** | none |
| Sections all-OK | 417 / 714 (58.4%) | **417 / 714** (58.4%) | none |
| Sections skipped | 35 | **35** | none |
| Near-miss sections (1–3 fails) | 211 | **211** | none |
| Near-miss failing rules | 322 | **326** | **+4** |
| Mono-class sections (`expected_ipa`) | 24 | **24** | none |
| Mono-class sections (`invalid_ipa`) | 17 | **17** | none |
| Mono-class sections (`expected_range_dots`) | 6 | **6** | none |

Active failure-class head (unchanged from spawn except `syntax_other` 43→36 after passes 107–110):

| count | `failure_class` | spawn count |
|------:|-----------------|------------:|
| 125 | `unknown_character` | 125 |
| 105 | `expected_underscore` | 105 |
| 77 | `expected_ipa` | 77 |
| 58 | `invalid_ipa` | 58 |
| 41 | `expected_range_dots` | 41 |

IPA-class near-miss rules (≤3-fail hunt band): `expected_ipa` **43**, `invalid_ipa` **22**, `expected_range_dots` **11**.

---

## 3. Ranked subclusters (global mono-class sections-completed if cleared)

Primary metric: active sections where **all** fails fall in the bucket. Secondary: rule count.

| complete | sections | rules | failure_class | subcluster | section tags (nm / heavy / other) | recommendation |
|---------:|---------:|------:|---------------|------------|-----------------------------------|----------------|
| 8 | 19 | 30 | `expected_ipa` | `editorial_slash_gloss` | 13 / 0 / 6 | correction-pass → [115](../issues/115-correction-pass-editorial-slash-prose-residue.md) |
| 8 | 14 | 21 | `expected_ipa` | `paren_optional_modifier` | 11 / 0 / 3 | correction-pass → [116](../issues/116-correction-pass-paren-optional-modifiers.md) |
| 6 | 9 | 11 | `invalid_ipa` | `prenasal_prefix` | 9 / 0 / 0 | correction-pass → [117](../issues/117-correction-pass-prenasal-prefix.md) |
| 3 | 9 | 35 | `expected_range_dots` | `european_dot_affricate` | 4 / 0 / 5 | correction-pass → [118](../issues/118-correction-pass-dot-affricate-notation.md) |
| 2 | 7 | 8 | `expected_ipa` | `prose_double_slash_env` | 4 / 0 / 3 | defer — follow-on after 115 (env-paren `//`; not 108) |
| 2 | 4 | 6 | `expected_ipa` | `paren_optional_io` | 2 / 0 / 2 | defer — overlap 48/111 |
| 1 | 13 | 25 | `invalid_ipa` | `khoisan_click:ǃ` | 6 / 1 / 6 | **defer** — manual/skip (spike 64) |
| 1 | 9 | 11 | `invalid_ipa` | `khoisan_click:ǀ` | 2 / 1 / 6 | **defer** — manual/skip |
| 1 | 6 | 6 | `expected_range_dots` | `dot_inside_set` | 4 / 0 / 2 | fold into [118](../issues/118-correction-pass-dot-affricate-notation.md) |
| 1 | 2 | 2 | `expected_ipa` | `ipa_received_other:*` | 2 / 0 / 0 | `ipa_mappings` / manual |
| 0 | 4 | 6 | `invalid_ipa` | `khoisan_click:ǁ` | 0 / 0 / 4 | **defer** — manual/skip |
| 0 | 5 | 5 | `invalid_ipa` | `khoisan_click:ǂ` | 1 / 0 / 4 | **defer** — manual/skip |
| 0 | 3 | 4 | `expected_ipa` | `malformed_chain_or_prose` | 2 / 0 / 1 | manual / comment peel |
| 0 | 1 | 1 | `expected_ipa` | `null_in_io_residual` | 0 / 0 / 1 | defer — [109](../issues/109-correction-pass-parallel-output-null-residual.md) family |

Full row-level data: [`ipa-correction-classes.csv`](./ipa-correction-classes.csv) (176 rows). Bucket summary: [`ipa-correction-buckets.csv`](./ipa-correction-buckets.csv).

---

## 4. Class-specific analysis

### 4.1 `expected_ipa` — compile transforms vs mappings hold-outs

| Subcluster | Shape | Field blame | Class-first path? | Hold-out? |
|------------|-------|-------------|-------------------|-----------|
| `editorial_slash_gloss` | `/ts/?`, `/j/`, `(Pouletin` prose tails | env / mixed | **yes** — strip editorial `/…/` to `comment`; peel unclosed `(` prose | `{a/e}` alternation (§18.3.x) → expand to `{a,e}` at compile (structural, not gloss) |
| `paren_optional_modifier` | `k(ʷ)`, `ɸ(ʼ,ʰ)`, `(ˀ)t` | input / output | **yes** — unwrap modifier optionals per [111](../issues/111-correction-pass-cartesian-io-optionals.md) Family B | Salish `(ˀ)` in §37.1.2.6 — already near-miss, not skipped |
| `prose_double_slash_env` | `#_ ( // _a?)` | env\|exception | **yes** — peel paren tail after env focus; distinct from [108](../issues/108-correction-pass-double-slash-env.md) | — |
| `paren_optional_io` | `V=0`, `(N)P` | input | partial — [48](../issues/48-correction-pass-parenthetical-segment-notation.md) residual | §10.1.1, §31.1 |
| `ipa_received_other:*` | correspondence `*C` | input | **no** — `ipa_mappings` or section map | §10.8 |
| `malformed_chain_or_prose` | `{n̥n,nn̥ >` missing `/` | input | manual / ingest overlay | §17.7.3.1.1 |

**Separation verdict:** ~**85%** of `expected_ipa` rows are class-first compile/parse transforms; ~**15%** need `ipa_mappings`, `manual_mappings`, or ingest overlay (scattered `*`, `@`, comma-list residuals).

### 4.2 `invalid_ipa` — prenasal vs Khoisan

| Subcluster | Shape | Sections | Class-first path? |
|------------|-------|----------|-------------------|
| `prenasal_prefix` | `ⁿP`, `VⁿP`, `ⁿs` | §7.13, §10.3.5.x, §24.1.5/7, §30.1.1 | **yes** — compile `normalize_prenasal_prefix()` → matrix `N` + segment or `[+nasal]` feature |
| `khoisan_click:*` | `ǃ`, `ǀ`, `ǁ`, `ǂ`, `!`, `!!`, `ʘ` | §20.1.x, §20.2.x | **no** — spike-64 defer; batch `manual_mappings` or `skip_sections` |

**Separation verdict:** **11** rules (**6** mono-class sections) are prenasal compile normalisation; **47** rules (**~10** sections, only 2 mono-class) are Khoisan — defer unchanged.

Note: [110](../issues/110-correction-pass-diacritic-prerequisite-lengthening.md) cleared `ⁿP > N` voice-prerequisite rows in §10.3.5.x; remaining `invalid_ipa` there is the `ⁿ` token itself, not diacritic prereq.

### 4.3 `expected_range_dots` — Yup'ik vs European dot-affricate

| Subcluster | Shape | Sections | One pass or two? |
|------------|-------|----------|------------------|
| `european_dot_affricate` | `t.ʃ`, `p.`, `ç.k`, `kj.` | §17.10, §36.3.2.x | **Pass 118** — treat `.` as affricate / cluster boundary → expand to segment sequences or matrices |
| `dot_inside_set` | `{e,ed}`, `mt.` | §36.3.2.2.3, §17.12, §35.1.7 | fold into 118 |
| `yupik_geminate_dot_range` | `V.V` / `a.C` geminate | — | **0 rows** on current inventory — Yup'ik §24.x failures are `prose_double_slash_env` + `prenasal_prefix`, not `expected_range_dots` |

**Separation verdict:** **one** correction pass (118) for European/Tibeto-Burman dot notation; Yup'ik geminate shapes are not active `expected_range_dots` levers today.

---

## 5. Cross-check: passes 107–110, spike 64, heavy-section skips

### Resolved passes 107–110 (stale levers)

| Pass | Cluster | IPA overlap | Status |
|------|---------|-------------|--------|
| [107](../issues/107-correction-pass-prose-env-positions.md) | `expected_underscore` prose env | none direct | **resolved** — no `expected_ipa` prose-env `_` residuals from 107 scope |
| [108](../issues/108-correction-pass-double-slash-env.md) | `expected_underscore` `//` env | **partial** — `prose_double_slash_env` in `expected_ipa` is env-**paren** `//`, not bare `//` env | **resolved** for underscore class; **8** `expected_ipa` rows remain |
| [109](../issues/109-correction-pass-parallel-output-null-residual.md) | `syntax_other` parallel `∅` | 1 `null_in_io_residual` row | **resolved** for main cluster |
| [110](../issues/110-correction-pass-diacritic-prerequisite-lengthening.md) | `diacritic_prereq` | cleared `pː`/`ʰ` in §10.3.5.x; `ⁿ` token remains | **resolved** |

### Spike 64 Khoisan defer (unchanged)

All §20.x `invalid_ipa` rows (**47** rules) remain **defer** — no class-first compile path without owner policy on click notation. Batch `manual_mappings` or section-level skip; do not file correction pass.

### 2026-09-05 heavy-section skips

`skip_sections` seeded for Salish **35.1.x** (8 sections), **29.2**, **46.13**. No `expected_ipa` / `invalid_ipa` / `expected_range_dots` rows inside skipped sections in the active fail inventory. §35.1.9 (`expected_ipa` `//`) remains **active** (not in skip list).

---

## 6. Recommended next queue

Filed correction-pass instances (ticket-13 shape):

1. **[115 — editorial slash + prose residue](../issues/115-correction-pass-editorial-slash-prose-residue.md)** — **8** mono-class sections (`expected_ipa`)
2. **[116 — parenthetical optional modifiers](../issues/116-correction-pass-paren-optional-modifiers.md)** — **8** mono-class sections (`expected_ipa`)
3. **[117 — prenasal `ⁿ` prefix](../issues/117-correction-pass-prenasal-prefix.md)** — **6** mono-class sections (`invalid_ipa`)
4. **[118 — dot-affricate cluster notation](../issues/118-correction-pass-dot-affricate-notation.md)** — **3** mono-class sections (`expected_range_dots`)

**Explicit defer:** Khoisan clicks (§20.x), `prose_double_slash_env` env-paren follow-on, `paren_optional_io` residuals (48/111), scattered `ipa_mappings` hold-outs (`*`, `@`).
