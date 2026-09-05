# Nested-set flatten prototype (spike 85)

Question: if we flatten Index editorial nested `{…}` at ingest (`stages`, `env`, `exception`), how much does compile validation improve, what regresses, and where in the parse pipeline should the transform run?

Throwaway code: [`flatten_nested_sets.py`](./flatten_nested_sets.py), [`nested_set_flatten_prototype.py`](./nested_set_flatten_prototype.py). Scan helpers: [`scan_nested_sets.py`](./scan_nested_sets.py) (`working_max_brace_depth`, `count_working_depth_ge2`). Per-rule table: [`nested-set-flatten-prototype.csv`](./nested-set-flatten-prototype.csv). Metrics dump: [`nested-set-flatten-prototype-metrics.json`](./nested-set-flatten-prototype-metrics.json).

**Not merged to `main`.** Corpus YAML was loaded read-only; validation used in-memory rules + committed inventory as baseline. No writes to `data/diachronica/index_diachronica_parsed.yml` or `.scratch/rule-index/inventory/`.

---

## 1. Algorithm scope

`flatten_nested_sets(text, mode=…)` — [`flatten_nested_sets.py`](./flatten_nested_sets.py). Prior art only: compile `_expand_sets` in [`src/conlanger/tools/compile/asca/parenthetical.py`](../../../src/conlanger/tools/compile/asca/parenthetical.py) (ticket 48 parentheticals; `_SET_RE` matches `{([^{}]*)}` so it cannot un-nest).

| In scope | Out of scope |
|----------|--------------|
| Same-type `{}` nesting: `{a,{b,c}}` → `{a,b,c}` | `segment{variants}` / ticket 48 (top-level `(h)ə{p,b}`) |
| Union of comma-bounded set members at depth > 1, including distribution of non-paren prefix/suffix (`{{h,k,ŋ}n,…}` → `{hn,kn,ŋn,…}`) | `(h)ə{p,b}` parallel columns (#71) |
| Mode `union_paren`: `({m,j,w})V` → `{mV,jV,wV}`; `(C){p,kʷ}` as a **set member** → `(C)p,(C)kʷ` | Unbalanced / malformed (`2173`, `4654`, …) — returned unchanged |
| Each **stage string** independently + **env** + **exception** | **`raw`** (never) |

Unbalanced strings (`brace_balance != 0`) are left unchanged. Flat sets are not re-serialized (preserves ASCA env-set spacing `:{#_, _#}:` from medial, [`transforms.py`](../../../src/conlanger/tools/ingest/transforms.py) `apply_medial_env_conditions`).

Self-check (2026-08-19): `uv run python .scratch/rule-index/research/flatten_nested_sets.py` — all fixtures pass, including `(h)ə{p,b}` unchanged in both modes and `{hə{p,b},ə{p,b}}` → `{həp,həb,əp,əb}` (compile-time D shape; see §6).

---

## 2. Method (Phase A)

1. Load [`data/diachronica/index_diachronica_parsed.yml`](../../../data/diachronica/index_diachronica_parsed.yml) (9201 index rules; [`nested-sets-scan.json`](./nested-sets-scan.json) `total_rules_scanned`).
2. Deep-copy; flatten `stages` / `env` / `exception` in memory (two modes).
3. Re-validate every source that either changed or is currently `failure_class=nested_brackets` via `validate_index_rule` / `iter_validation_rows` path ([`index_inventory.py`](../../../src/conlanger/tools/index_inventory.py) `validate_index_rule`; group mappings `asca_group_mappings_dict()` as `create_index`). ASCA **0.10.2** (`asca --version`).
4. Merge unchanged inventory rows from [`.scratch/rule-index/inventory/rule-inventory.csv`](../inventory/rule-inventory.csv). Unflattened rules cannot flip `ok`. Changelog flips are computed in memory against that CSV (`ok_flip_changelog_rows` match key `(source, alt_idx)`); **not** appended to the committed changelog.

Phase A on committed YAML is **P4-equivalent**: else resolution has already copied prev `env` → `exception` ([`section_policy.py`](../../../src/conlanger/tools/ingest/section_policy.py) `resolve_catch_all_else_rules`; YAML `:5510` already has `exception: _{s,({m,j,w})V}`).

---

## 3. Metrics

Inventory baseline (CSV walk, 2026-08-19): **9689** rows, **45** `nested_brackets` (summary [rule-inventory-summary.md](../inventory/rule-inventory-summary.md) also lists 45; #67 reported 46 on 2026-08-12). `ok=True` in the CSV includes **43** `section_skipped` rows (`ok=True` by [`validate_index_rule`](../../../src/conlanger/tools/index_inventory.py) when `section.skipped`); summary “OK **8227**” excludes those. Deltas below are identical on either counting convention.

Working-field brace depth counts **exclude `raw`** (`count_working_depth_ge2`). #67’s **40** used `classify_rule`, which also scans `raw` ([`scan_nested_sets.py`](./scan_nested_sets.py)).

| Metric | Before | After (union-only) | After (union + paren-in-set) |
|--------|-------:|-------------------:|-----------------------------:|
| Inventory `ok=True` rows | 8270 | 8277 | 8281 |
| `nested_brackets` rows | 45 | 32 | 27 |
| `ok` flips (changelog) | — | 7 | 11 |
| Regressions (`ok` True→False) | — | 0 | 0 |
| Rules with ≥1 field flattened | — | 13 | 20 |
| Corpus rules brace depth ≥ 2 (working fields) | 31 | 18 | 13 |

Compile-ok excluding `section_skipped`: **8227 → 8234 → 8238** ([`summarize_inventory`](../../../src/conlanger/tools/index_inventory.py) formula).

### `failure_class` transitions

From [`nested-set-flatten-prototype-metrics.json`](./nested-set-flatten-prototype-metrics.json) / CSV:

**Union-only**

| Transition | n | Sources (abbrev.) |
|------------|--:|-------------------|
| `nested_brackets` → `ok` | 7 | `:11518` env; `:1762` exception; `:5048` stages[0]; `:6192` `:6225` `:6226` exception; `:6193` stages[0] |
| `nested_brackets` → `syntax_other` | 5 | Salish `{{C[…],K}ʷ,w}_` cluster `:11552` `:11579` `:11601` `:11624` (alt 1); Mekens `:8439` |
| unchanged `nested_brackets` | 32 | compile-created D/A, unbalanced E, leftover YAML nests |

**Union + paren-in-set** — same 7 plus:

| Transition | n | Sources |
|------------|--:|---------|
| `nested_brackets` → `ok` | +4 (11 total) | `:1398` stages[0]; `:1903` env; `:5509` env; `:5510` exception |
| `nested_brackets` → `expected_underscore` | 1 | `:11722` exception `{t(’),lʲ,{n,l}(ˀ)}_` |

No `ok` True→False in either mode. Mode 2 can still rewrite already-ok fields (`:12670` `({ʔ,s})w`, `:13844` `({p,t,k})n`) without flipping `ok` — go-with-limits, not a changelog regression.

---

## 4. Parse insertion (Phase B)

Candidate slots from [`parse_rule_element`](../../../src/conlanger/tools/ingest/parser.py) / `IndexDiachronicaParser.parse`:

| Slot | Location | Verdict |
|------|----------|---------|
| P1 | After `extract_rule_parts`, before `series_expansions` | **Reject** |
| P2 | After `series_expansions`, before medial/else | **Reject** as canonical |
| P3 | After medial / feature / IPA, before `finalize_stages_shape` | Equivalent to P4 for else-copy today |
| P4 | After `resolve_catch_all_else_rules` | **Recommend** |

### Else-rule evidence (required)

**Complementary pair (flatten commutativity):** HTML [`index_diachronica_original.html:5509–5510`](../../../data/diachronica/index_diachronica_original.html) `m̩ n̩ → am an / _{s,({m,j,w)V}` then `m̩ n̩ → em en / else`. Parsed YAML already resolved else ([`index_diachronica_parsed.yml`](../../../data/diachronica/index_diachronica_parsed.yml) `:5510` `exception: _{s,({m,j,w})V}`). Fixture in `run_else_fixtures()`:

- P3: flatten prev `env`, then `resolve_catch_all_else_rules` copies that string to else `exception`.
- P4: copy nested `env` first, then flatten both fields.

For `union_paren`, both slots yield `exception: _{s,mV,jV,wV}` (`exception_equal: true` in metrics JSON). Union-only leaves the nested form in both slots (also equal). **Copy ∘ flatten = flatten ∘ copy** for this else rewrite ([`section_policy.py`](../../../src/conlanger/tools/ingest/section_policy.py) assigns `resolved["exception"] = prev_env`).

**Deferred else (does not copy nested exception):** `:1762` `aː → aa / W_ ! when _{C{C,ː},#}` then `:1763` `/ else` (HTML [lines 1762–1763](../../../data/diachronica/index_diachronica_original.html)). Prev has both `env` and `exception`, so else **keeps** `env: else` (YAML `:1763`; test `test_resolve_catch_all_else_deferred_prev_env_and_exception`). Flatten P3 vs P4 does not change that copy (there is none). Flattening `:1762` `exception` is independent and recovers `ok` in both modes (CSV).

**Recommendation: P4.** Same validation numbers as Phase A; runs after series / medial / stress / feature / IPA; flattens else-derived `exception` even if a future section policy copies env after `parse_rule_element`. P3 is observationally equivalent for current else code; production can implement P4-only (idempotent if both are wired).

### Interactions

- **`series_expansions`:** `{ʔ,hₓ}` (HTML `:998` `{ʔ,h<sub>x</sub>}`) expands **inside** braces to `{ʔ,h₁,h₂,h₃}` ([`series.py`](../../../src/conlanger/utils/series.py) `_expand_collectives_inside_braces`; [`parser_config.yml`](../../../data/parser_config.yml) `hₓ: [h₁, h₂, h₃]`). Current YAML `:998` is already flat — **not** in today’s 45 `nested_brackets`. P1 vs P2 equal on this shape (`series_slot_probe`). P1-only would miss braces **introduced** after P1 (`hₓ` *outside* braces → `{h₁,h₂,h₃}`).
- **`series.py` first-`}` matcher:** `expand_collectives_in_field` uses `text.find("}")`, not brace matching. Nested `{` before P2 can truncate the inner set. Flatten-before-series would paper over that, but P4 after series is the right *flatten* slot; the matcher bug is a separate ingest fix.
- **Medial:** replaces env with `_` + exception `:{#_, _#}:` — no nested `{}`. Flatten must not re-serialize that env-set (fixed in the prototype after a first pass mutated spacing).
- **Compile parentheticals (ticket 48):** `(h)ə{p,b}` stays depth-1 in YAML (`:2398` stages `(h)ə{p,b}`). `expand_index_parenthetical_notation` then emits `{hə{p,b},ə{p,b}}`, which ASCA lexes as `NestedBrackets` (inventory description for `:2398`). Parse-time flatten does **not** touch D. The same flatten **at compile after parentheticals would** rewrite that to `{həp,həb,əp,əb}` — which is why compile-only flatten is the wrong policy for #71.

### Rejected orderings

| Ordering | Why rejected |
|----------|----------------|
| P1-only | `series_expansions` can still introduce `{…}` afterward; flatten would miss them. |
| P2-only | Stress/medial/feature/IPA still rewrite env after series ([`parser.py`](../../../src/conlanger/tools/ingest/parser.py) lines 187–190). Canonical flatten should see post-normalizer strings. |
| P3-only | Equivalent for today’s else copy, but else-derived `exception` is created **after** `parse_rule_element`. P4 is the slot that matches “flatten all derived context fields.” |
| Compile-only flatten after `expand_meta_notation` / parentheticals | Would “fix” bucket D (`{hə{p,b},ə{p,b}}`) and mix #71 into #69/#70. Also leaves nested `{}` in applier-neutral YAML (ADR-0002). |
| Compile-only flatten *before* parentheticals | Same as parse-time on YAML fields for true nests, but env normalizers (medial, else, series) already live at parse — splitting flatten to compile fights that class. |

---

## 5. Source vs Index (qualitative, buckets A–E)

Index nested form is often **authorial condensation**, not a transcription of the cited grammar’s rule notation. `raw` keeps the HTML wording (ADR-0010). Cited publications were not all fetchable (JSTOR / dead Melchert PDF); claims below are grounded in Index HTML + YAML `citation` / first `<p>`, plus ASCA’s documented set syntax.

| Bucket | `source` | Index nested form | Cited source / note |
|--------|----------|-------------------|---------------------|
| A | `:998` | HTML `{ʔ,h<sub>x</sub>}` → YAML `{ʔ,h₁,h₂,h₃}` (already flat) | Ehret (1995) via HTML `:992` citation. Collective `hₓ` is Index series notation, not nested `{h₁,{h₂}}`. |
| A | `:5048` | `{{h₁,h₃}s,s{h₁,h₃}} → sː (contested)` | Melchert Anatolian PDF linked from HTML `:5034` (**link is dead**). Index itself marks the rule contested; union flatten → `{h₁s,h₃s,sh₁,sh₃}` **recovered `ok`**. Treat as Index union-of-clusters, not Melchert’s original formalism (unverified). |
| A | `:1398` | `{{s,z}(ˤ),ʒ}ʃ → ʃː` | Brustad et al. / Wikipedia / At-Tonsi (HTML `:1376`). Nested set + optional emphatic is Index shorthand; `union_paren` recovered `ok`. |
| B | `:1903` | `Cʷ → C / _ə{(C){p,kʷ},m,w}` | Goddard (1982) IJAL 48:16–48 (HTML `:1895`). Goddard prose lists rounding environments; Index packed them as a nested env set. `union_paren` → `_ə{(C)p,(C)kʷ,m,w}` recovered `ok`. |
| B | `:5509`/`:5510` | `_{s,({m,j,w})V}` copied to else exception | Old Irish section citation is only `dhokarena56` (HTML `:5496`) — **no named grammar**. Else copy is Index-internal ([ticket 53](../issues/53-correction-pass-prose-env-else.md)). |
| B | `:6192` | `! {{h,k,ŋ}n,w,v,l,r}_, _{u,o,i}` | Theiling `rules.sch` (HTML `:6183`). Index nested `{h,k,ŋ}n` is breaking-cluster notation; union → `{hn,kn,ŋn,…}` recovered `ok`. |
| C | `:6193` | `{e,w{æ,i}}` in stages | Same Theiling citation. Union splices `w{æ,i}` → recovered `ok`. |
| D | `:2398` | `(h)ə{p,b} → t / _l` (YAML depth 1) | Thompson (1976) Proto-Viet-Muong (HTML `:2377`). Parallel optional-prefix + column set — **must not** be treated as nested-`{}` union. Unchanged by naive flatten; compile parentheticals create NestedBrackets. |
| D | `:2409` | four `(h)ə{…}` columns | Same Thompson citation. Unchanged. |
| E | `:2173` | unbalanced `{a,o,u a {a,o,u} {o,u,i}` | Starostin/Dybo/Mudrak via Wikipedia (HTML `:2167`). Malformed Index chain; flatten leaves unchanged. |
| E | `:4654` | `m n ŋ t {{ɣ,ʁ} → {k,q}}` chain artifact | Swadesh (1952) IJAL 18:166–171 (HTML `:4647`). Arrow inside braces is parse/chain damage, not a nested set. |

---

## 6. Policy

### Parse-time vs compile-time

**Parse-time flatten at P4** (union on stages + env + exception; **union_paren** for env/exception and for I/O members like `:1398`). Preserve `raw`.

- ADR-0010: class-first mechanical de-condensation; `raw` remains the Index audit trail. Same class as medial, else, stress, feature/IPA, `series_expansions` ([`parser.py`](../../../src/conlanger/tools/ingest/parser.py) module docstring).
- ADR-0002: YAML should not store nested `{…}` that **no** applier accepts. ASCA 0.10.2: `NestedBrackets` — “Cannot have nested brackets of the same type” ([`syntax.rs`](https://github.com/Girv98/asca-rust/blob/0.10.2/src/error/syntax.rs); [doc/doc.md Sets](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md); [asca-rule-validity.md](./asca-rule-validity.md) §2 / §6). Brassica categories are also non-nested ([#67 findings](./nested-sets-inventory.md) §1).
- Compile-only (as #69/#70 were written) would either (a) leave nested YAML, or (b) if run after ticket-48 parentheticals, flatten D and violate the #71 boundary (self-check `{hə{p,b},ə{p,b}}` → `{həp,həb,əp,əb}`).

**Compile-time flatten remains relevant only for nesting introduced after parse** (group mappings / series mappings wrapping a letter already inside `{…}`, e.g. `:1149` YAML `{x₁,x₂}` → inventory `{{ɣ, ɣʷ, xʷ},x}`). That is **not** Index editorial nesting and is out of scope for #69/#70.

### Rewrite #69 / #70?

**Yes.** Implementation briefs rewritten to parse-time P4 (this spike). #69 unblocked. #70 union-flatten of YAML-nested I/O can proceed; D/parallel stays #71.

### Per #67 bucket (parse-time flatten)

| Bucket | Verdict | Evidence |
|--------|---------|----------|
| **A** true nested I/O | **go-with-limits** | `:5048` recovered (union); `:1398` needs `union_paren`; `:8439` → `syntax_other` (slash members); `:998` already flat via series; `:1149` `:3124` `:3737` `:12290` are compile-created / #71 shapes, not YAML nests. |
| **B** nested env/exception | **go** (use `union_paren`) | Union recovers `:1762` `:11518` `:6192` `:6225` `:6226`; paren mode adds `:1903` `:5509` `:5510`. Salish `Kʷ` cluster leaves `syntax_other` after flatten (group-mapping follow-on). |
| **C** parenthetical-in-set | **go-with-limits** | `:6193` union-ok; env shapes need paren mode. Do not expand already-ok `({set})X` globally without tests (`:12670` `:13844`). |
| **D** parallel columns | **no-go** | YAML `(h)ə{p,b}` / `e(C){V[…]}` unchanged; NestedBrackets is compile parentheticals. Confirms **#71** boundary. |
| **E** prose/malformed | **no-go** | Unbalanced strings unchanged; `:11722` paren mode → `expected_underscore` (not `ok`). Per-rule `manual_mappings` / skip. |

### #71 boundary

Naive flatten **does not** fix parallel-column bucket D. Inventory rows `:2398` `:2409` `:2415` `:3124` `:3737` `:5454` `:5900` `:6165` `:14327` stay `nested_brackets` with empty `fields_changed_*` (CSV). Do not implement D as a side effect of compile-after-parenthetical flatten.

---

## 7. Follow-ons

1. **#69** — parse-time P4 flatten of env/exception (`union_paren`); TDD on `:1903` `:5509` `:5510` `:6192` `:1762` `:11518`; document Salish `syntax_other` residuals.
2. **#70** — parse-time P4 flatten of stages (`union`, plus `union_paren` for `:1398`); `:5048` `:6193`; hold D for #71; `:8439` / unbalanced E not in this handler.
3. **#71** — grill `(h)ə{p,b}`, `e(C){V[…]}`, compile-created `{CC_C{V,#},CCG_C{V,#}}` from `CC(G)_C{V,#}` (`:1954`).
4. Optional later: compile flatten **after group mappings** for `:1149`-class nesting — separate from Index editorial flatten.

Run: `uv run python .scratch/rule-index/research/flatten_nested_sets.py` then `uv run python .scratch/rule-index/research/nested_set_flatten_prototype.py`.
